"""
破损检测模型 v2 训练脚本
- 从 real_dataset/damage_raw 读取原始图（每类9张）
- 划分 7训练/2验证
- 强数据增强（每图增强8倍）
- ResNet50 分层微调（冻结底层，微调高层）
- 标签平滑 + OneCycleLR + 早停
"""
import os
import sys
import random
import shutil
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, datasets
from torchvision.models import resnet50, ResNet50_Weights

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE, 'data', 'real_dataset', 'damage_raw')
OUT_DIR = os.path.join(BASE, 'data', 'damage_v2')
WEIGHTS_PATH = Config.DAMAGE_WEIGHTS

CLASSES = Config.DAMAGE_CLASSES  # 与config一致
NUM_CLASSES = len(CLASSES)
IMG_SIZE = 224
AUG_PER_IMAGE = 8  # 每张原图增强8倍
SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


def augment_image(img: Image.Image) -> Image.Image:
    """强数据增强：随机组合多种变换"""
    w, h = img.size
    # 随机缩放裁剪
    if random.random() < 0.7:
        scale = random.uniform(0.7, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        left = random.randint(0, w - new_w)
        top = random.randint(0, h - new_h)
        img = img.crop((left, top, left + new_w, top + new_h))
        img = img.resize((w, h), Image.BILINEAR)

    # 水平翻转
    if random.random() < 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # 随机旋转
    if random.random() < 0.5:
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, fillcolor=(128, 128, 128), resample=Image.BILINEAR)

    # 颜色抖动
    if random.random() < 0.6:
        img = ImageEnhance.Brightness(img).enhance(random.uniform(0.7, 1.3))
        img = ImageEnhance.Contrast(img).enhance(random.uniform(0.7, 1.3))
        img = ImageEnhance.Color(img).enhance(random.uniform(0.7, 1.3))
        img = ImageEnhance.Sharpness(img).enhance(random.uniform(0.5, 1.5))

    # 高斯模糊
    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))

    # 高斯噪声
    if random.random() < 0.3:
        arr = np.array(img).astype(np.float32)
        noise = np.random.normal(0, random.uniform(5, 15), arr.shape)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

    return img


def prepare_dataset():
    """划分训练/验证集 + 数据增强，输出ImageFolder格式"""
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)

    # 目录名格式: 0_无破损, 1_左侧轻微凹陷, ...
    class_dirs = sorted([d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d))])
    print(f"Found {len(class_dirs)} classes")

    for split in ['train', 'val']:
        for cls_dir in class_dirs:
            os.makedirs(os.path.join(OUT_DIR, split, cls_dir), exist_ok=True)

    total_train = 0
    total_val = 0

    for cls_dir in class_dirs:
        src_dir = os.path.join(RAW_DIR, cls_dir)
        files = sorted([f for f in os.listdir(src_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        random.shuffle(files)

        # 动态划分：每类最后2张验证，其余训练
        n_val = min(2, len(files) // 5)
        n_val = max(n_val, 1)
        val_files = files[:n_val]
        train_files = files[n_val:]

        # 训练集：原图 + 增强
        for f in train_files:
            src = os.path.join(src_dir, f)
            img = Image.open(src).convert('RGB')
            # 保存原图
            dst = os.path.join(OUT_DIR, 'train', cls_dir, f)
            img.save(dst, quality=95)
            total_train += 1
            # 增强
            for i in range(AUG_PER_IMAGE):
                aug_img = augment_image(img)
                dst = os.path.join(OUT_DIR, 'train', cls_dir, f"aug_{i}_{f}")
                aug_img.save(dst, quality=90)
                total_train += 1

        # 验证集：仅原图
        for f in val_files:
            src = os.path.join(src_dir, f)
            dst = os.path.join(OUT_DIR, 'val', cls_dir, f)
            shutil.copy2(src, dst)
            total_val += 1

    print(f"Dataset prepared: train={total_train}, val={total_val}")
    return total_train, total_val


def get_dataloaders(batch_size=16):
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(IMG_SIZE),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    train_ds = datasets.ImageFolder(os.path.join(OUT_DIR, 'train'), transform=train_transform)
    val_ds = datasets.ImageFolder(os.path.join(OUT_DIR, 'val'), transform=val_transform)

    print(f"Train classes: {train_ds.classes}")
    print(f"Val classes: {val_ds.classes}")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)
    return train_loader, val_loader, train_ds.classes


def build_model(num_classes, device):
    """ResNet50 分层微调：冻结layer1/layer2，微调layer3/layer4/fc"""
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    # 冻结底层
    for param in model.conv1.parameters():
        param.requires_grad = False
    for param in model.bn1.parameters():
        param.requires_grad = False
    for param in model.layer1.parameters():
        param.requires_grad = False
    for param in model.layer2.parameters():
        param.requires_grad = False
    # 微调高层
    for param in model.layer3.parameters():
        param.requires_grad = True
    for param in model.layer4.parameters():
        param.requires_grad = True

    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(0.2),
        nn.Linear(256, num_classes),
    )
    return model.to(device)


def mixup_data(x, y, alpha=0.2):
    """Mixup 数据增强"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


def train_one_epoch(model, loader, criterion, optimizer, device, use_mixup=True):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()

        if use_mixup and random.random() < 0.5:
            images, labels_a, labels_b, lam = mixup_data(images, labels)
            outputs = model(images)
            loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return running_loss / total, correct / total


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    return running_loss / total, correct / total, all_preds, all_labels


def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # 1. 准备数据集
    print("\n=== Preparing dataset ===")
    prepare_dataset()

    # 2. 加载数据
    print("\n=== Loading data ===")
    train_loader, val_loader, class_names = get_dataloaders(batch_size=16)
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

    # 3. 构建模型
    print("\n=== Building model ===")
    model = build_model(NUM_CLASSES, device)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable: {trainable_params:,} / Total: {total_params:,}")

    # 4. 训练配置
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=1e-4, weight_decay=1e-4
    )
    num_epochs = 40
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=5e-4, epochs=num_epochs,
        steps_per_epoch=len(train_loader), pct_start=0.1
    )

    # 5. 训练循环
    print("\n=== Training ===")
    best_acc = 0.0
    patience = 8
    patience_counter = 0

    for epoch in range(num_epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device, use_mixup=True)
        val_loss, val_acc, preds, labels = validate(model, val_loader, criterion, device)
        scheduler.step()

        print(f"Epoch {epoch+1:2d}/{num_epochs} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"LR: {optimizer.param_groups[0]['lr']:.6f}")

        if val_acc > best_acc:
            best_acc = val_acc
            patience_counter = 0
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'best_acc': best_acc,
                'epoch': epoch + 1,
            }, WEIGHTS_PATH)
            print(f"  -> Best model saved (val_acc={best_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  -> Early stopping at epoch {epoch+1}")
                break

    # 6. 最终验证
    print(f"\n=== Final Validation (best model) ===")
    checkpoint = torch.load(WEIGHTS_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    val_loss, val_acc, preds, labels = validate(model, val_loader, criterion, device)
    print(f"Best val accuracy: {val_acc:.4f} ({val_acc*100:.1f}%)")

    # 逐类准确率
    print("\nPer-class accuracy:")
    for i, cls in enumerate(class_names):
        cls_mask = np.array(labels) == i
        if cls_mask.sum() > 0:
            cls_acc = (np.array(preds)[cls_mask] == i).mean()
            print(f"  {cls:12s}: {cls_acc*100:.0f}% ({cls_mask.sum()} samples)")

    print(f"\nTraining complete. Weights saved to {WEIGHTS_PATH}")


if __name__ == '__main__':
    main()
