"""
真实标注数据集：数据增强 + ImageFolder 组织 + 模型训练
读取 damage_raw/ 和 stack_raw/ 中的真实感图片，通过强数据增强扩充，
组织为标准 ImageFolder 格式，然后微调 ResNet50 / ViT 模型。
"""
import os
import sys
import random
import shutil
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from torchvision.models import resnet50, ResNet50_Weights, vit_b_16, ViT_B_16_Weights

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_DATA_DIR = os.path.join(BASE, 'data', 'real_dataset')
OUTPUT_DIR = os.path.join(BASE, 'data', 'real_augmented')

# 每个原始图片生成的增强变体数量
AUG_MULTIPLIER_DAMAGE = 6   # 每类4张 × 6 = 24张/类
AUG_MULTIPLIER_STACK = 10   # 每类2张 × 10 = 20张/类
IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 20
LR = 5e-5


# ============ 数据增强 ============
def augment_image(img, idx):
    """对一张图片生成增强变体"""
    w, h = img.size
    variant = img.copy()

    # 1. 随机水平翻转
    if random.random() > 0.5:
        variant = variant.transpose(Image.FLIP_LEFT_RIGHT)

    # 2. 随机旋转（-8到8度）
    if random.random() > 0.3:
        angle = random.uniform(-8, 8)
        variant = variant.rotate(angle, fillcolor=(200, 200, 210), expand=False)

    # 3. 随机颜色抖动
    if random.random() > 0.3:
        # 亮度
        factor = random.uniform(0.8, 1.2)
        variant = ImageEnhance.Brightness(variant).enhance(factor)
    if random.random() > 0.3:
        # 对比度
        factor = random.uniform(0.8, 1.25)
        variant = ImageEnhance.Contrast(variant).enhance(factor)
    if random.random() > 0.4:
        # 饱和度
        factor = random.uniform(0.7, 1.3)
        variant = ImageEnhance.Color(variant).enhance(factor)

    # 4. 随机裁剪缩放（模拟不同拍摄距离）
    if random.random() > 0.4:
        scale = random.uniform(0.75, 1.0)
        cw, ch = int(w * scale), int(h * scale)
        cx = random.randint(0, max(0, w - cw))
        cy = random.randint(0, max(0, h - ch))
        variant = variant.crop((cx, cy, cx + cw, cy + ch))
        variant = variant.resize((w, h), Image.LANCZOS)

    # 5. 随机高斯模糊
    if random.random() > 0.7:
        blur = random.uniform(0.3, 1.0)
        variant = variant.filter(ImageFilter.GaussianBlur(radius=blur))

    # 6. 添加噪声
    if random.random() > 0.5:
        arr = np.array(variant).astype(np.int16)
        noise_level = random.randint(5, 15)
        noise = np.random.randint(-noise_level, noise_level, arr.shape, dtype=np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        variant = Image.fromarray(arr)

    return variant


def build_imagefolder(raw_dir, output_dir, class_names, aug_multiplier):
    """从 raw 目录构建增强后的 ImageFolder 数据集"""
    # 清理输出目录
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    all_items = []  # (class_idx, class_name, pil_image)

    # 读取原始图片
    for cls_idx, cls_name in enumerate(class_names):
        # 匹配 raw 目录中的子文件夹（可能带数字前缀）
        cls_dir = None
        for d in os.listdir(raw_dir):
            if d.endswith(cls_name) or d == cls_name or cls_name in d:
                cls_dir = os.path.join(raw_dir, d)
                break
        if cls_dir is None or not os.path.isdir(cls_dir):
            print(f"  WARNING: 未找到类别目录 {cls_name}")
            continue

        files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"  {cls_name}: {len(files)} 原始图 × {aug_multiplier} 增强 = {len(files)*aug_multiplier} 张")

        for f in files:
            img = Image.open(os.path.join(cls_dir, f)).convert('RGB')
            # 原图
            all_items.append((cls_idx, cls_name, img.copy()))
            # 增强变体
            for i in range(aug_multiplier - 1):
                aug = augment_image(img, i)
                all_items.append((cls_idx, cls_name, aug))

    # 按类别打乱并拆分 train/val (80/20)
    random.shuffle(all_items)
    by_class = {}
    for item in all_items:
        by_class.setdefault(item[0], []).append(item)

    train_items, val_items = [], []
    for cls_idx, items in by_class.items():
        random.shuffle(items)
        split = int(len(items) * 0.8)
        train_items.extend(items[:split])
        val_items.extend(items[split:])

    print(f"  总计: {len(all_items)} 张 (train: {len(train_items)}, val: {len(val_items)})")

    # 保存为 ImageFolder
    for split, items in [('train', train_items), ('val', val_items)]:
        for cls_idx, cls_name, img in items:
            cls_dir = os.path.join(output_dir, split, f"{cls_idx:02d}_{cls_name}")
            os.makedirs(cls_dir, exist_ok=True)
            fname = f"{split}_{cls_idx}_{random.randint(10000,99999)}.jpg"
            img.save(os.path.join(cls_dir, fname), quality=95)

    return output_dir


# ============ 训练 ============
def get_loaders(data_dir):
    train_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    train_ds = datasets.ImageFolder(os.path.join(data_dir, 'train'), transform=train_tf)
    val_ds = datasets.ImageFolder(os.path.join(data_dir, 'val'), transform=val_tf)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    return train_loader, val_loader, train_ds.classes


def train_model(model, train_loader, val_loader, epochs, lr, device, save_path, class_names):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_acc = 0.0
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        train_loss = running_loss / total
        train_acc = correct / total
        scheduler.step()

        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        val_acc = val_correct / val_total if val_total > 0 else 0

        print(f"  Epoch {epoch+1}/{epochs} - loss:{train_loss:.4f} train_acc:{train_acc:.4f} val_acc:{val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'best_acc': best_acc,
                'epoch': epoch + 1,
            }, save_path)
            print(f"  -> Saved best model (val_acc={best_acc:.4f})")

    print(f"  训练完成. Best val_acc: {best_acc:.4f}")
    return best_acc


# ============ 主流程 ============
def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"设备: {device}")
    print(f"PyTorch: {torch.__version__}")

    # 1. 构建破损检测数据集
    print("\n" + "=" * 60)
    print("步骤1: 构建破损检测增强数据集 (7类)")
    print("=" * 60)
    damage_raw = os.path.join(REAL_DATA_DIR, 'damage_raw')
    damage_out = os.path.join(OUTPUT_DIR, 'damage')
    build_imagefolder(damage_raw, damage_out, Config.DAMAGE_CLASSES, AUG_MULTIPLIER_DAMAGE)

    # 2. 构建堆码分类数据集
    print("\n" + "=" * 60)
    print("步骤2: 构建堆码分类增强数据集 (12类)")
    print("=" * 60)
    stack_raw = os.path.join(REAL_DATA_DIR, 'stack_raw')
    stack_out = os.path.join(OUTPUT_DIR, 'stack')
    build_imagefolder(stack_raw, stack_out, Config.STACK_CLASSES, AUG_MULTIPLIER_STACK)

    # 3. 训练破损检测模型
    print("\n" + "=" * 60)
    print("步骤3: 训练破损检测模型 (ResNet50)")
    print("=" * 60)
    train_loader, val_loader, class_names = get_loaders(damage_out)
    print(f"类别: {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))
    model = model.to(device)
    train_model(model, train_loader, val_loader, EPOCHS, LR, device, Config.DAMAGE_WEIGHTS, class_names)
    del model

    # 4. 训练堆码分类模型
    print("\n" + "=" * 60)
    print("步骤4: 训练堆码分类模型 (ViT-B/16)")
    print("=" * 60)
    train_loader, val_loader, class_names = get_loaders(stack_out)
    print(f"类别: {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    model = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1)
    model.heads.head = nn.Linear(model.heads.head.in_features, len(class_names))
    model = model.to(device)
    train_model(model, train_loader, val_loader, EPOCHS, LR, device, Config.STACK_WEIGHTS, class_names)
    del model

    print("\n" + "=" * 60)
    print("全部完成!")
    print("=" * 60)
    print(f"破损权重: {Config.DAMAGE_WEIGHTS}")
    print(f"堆码权重: {Config.STACK_WEIGHTS}")
    print(f"OCR数据: {os.path.join(REAL_DATA_DIR, 'ocr_train')} (80张, RapidOCR直接推理无需训练)")


if __name__ == '__main__':
    main()
