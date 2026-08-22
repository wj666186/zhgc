"""
合成数据集生成 + 模型训练一体化脚本
由于项目暂无真实标注数据，用 PIL 程序化生成各类集装箱图像进行微调，
产出真实可用的 .pth 权重文件，使三个 service 均走真实推理路径。

用法：
  python generate_and_train.py
"""
import os
import sys
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, datasets
from torchvision.models import resnet50, ResNet50_Weights, vit_b_16, ViT_B_16_Weights

# ============ 配置 ============
IMG_SIZE = 224
TRAIN_PER_CLASS = 40
VAL_PER_CLASS = 15
BATCH_SIZE = 16
EPOCHS = 8
LR = 1e-4
DATA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

DAMAGE_CLASSES = Config.DAMAGE_CLASSES  # 7类
STACK_CLASSES = Config.STACK_CLASSES    # 12类

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)


# ============ 图像生成工具 ============
def _container_base(draw, w, h, color=(180, 140, 90)):
    """绘制集装箱基础矩形 + 波纹纹理"""
    margin = 20
    draw.rectangle([margin, margin, w - margin, h - margin], fill=color, outline=(80, 60, 40), width=3)
    # 竖向波纹
    for x in range(margin + 15, w - margin, 18):
        draw.line([(x, margin + 5), (x, h - margin - 5)], fill=(color[0]-20, color[1]-20, color[2]-20), width=1)
    # 横向加强筋
    for y in range(margin + 30, h - margin, 50):
        draw.line([(margin + 5, y), (w - margin - 5, y)], fill=(color[0]-15, color[1]-15, color[2]-15), width=2)


def _add_noise(img, level=8):
    """添加轻微噪声"""
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-level, level, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# ============ 破损检测图像生成（7类）============
def gen_damage_none(w=IMG_SIZE, h=IMG_SIZE):
    """0: 无破损 - 干净集装箱"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    return _add_noise(img, 5)


def gen_damage_left_dent(w=IMG_SIZE, h=IMG_SIZE):
    """1: 左侧轻微凹陷"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    # 左侧凹陷：深色阴影区域
    for i in range(8):
        x = 25 + i * 3
        draw.ellipse([x, h//3, x + 20, h*2//3], fill=(120, 90, 60), outline=(100, 70, 40))
    return _add_noise(img, 6)


def gen_damage_right_dent(w=IMG_SIZE, h=IMG_SIZE):
    """2: 右侧凹陷"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    for i in range(8):
        x = w - 45 - i * 3
        draw.ellipse([x, h//3, x + 20, h*2//3], fill=(120, 90, 60), outline=(100, 70, 40))
    return _add_noise(img, 6)


def gen_damage_top_rust(w=IMG_SIZE, h=IMG_SIZE):
    """3: 顶部锈蚀"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    # 顶部锈斑
    for _ in range(25):
        rx = random.randint(25, w - 45)
        ry = random.randint(22, 55)
        rs = random.randint(3, 10)
        rust_color = random.choice([(180, 80, 30), (160, 60, 20), (200, 100, 40), (140, 50, 15)])
        draw.ellipse([rx, ry, rx + rs, ry + rs], fill=rust_color)
    # 锈水流痕
    for _ in range(5):
        sx = random.randint(30, w - 50)
        draw.line([(sx, 50), (sx + random.randint(-3, 3), 90)], fill=(160, 70, 25), width=2)
    return _add_noise(img, 7)


def gen_damage_bottom_scratch(w=IMG_SIZE, h=IMG_SIZE):
    """4: 底部刮擦"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    # 底部刮擦线条
    for _ in range(15):
        sx = random.randint(25, w - 80)
        sy = random.randint(h - 60, h - 30)
        ex = sx + random.randint(20, 60)
        ey = sy + random.randint(-5, 5)
        draw.line([(sx, sy), (ex, ey)], fill=(100, 70, 40), width=random.randint(1, 3))
    return _add_noise(img, 6)


def gen_damage_corner_deform(w=IMG_SIZE, h=IMG_SIZE):
    """5: 角件变形"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    # 左上角件变形
    draw.polygon([(20, 20), (50, 25), (45, 50), (20, 45)], fill=(140, 100, 60), outline=(80, 50, 30))
    draw.line([(30, 30), (45, 35), (40, 45)], fill=(80, 50, 30), width=2)
    # 右下角件变形
    draw.polygon([(w-20, h-20), (w-50, h-25), (w-45, h-50), (w-20, h-45)], fill=(140, 100, 60), outline=(80, 50, 30))
    return _add_noise(img, 6)


def gen_damage_door_deform(w=IMG_SIZE, h=IMG_SIZE):
    """6: 门板变形"""
    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    _container_base(draw, w, h, color=(190, 150, 100))
    # 门板区域（右半部分）变形凸起
    door_x = w // 2
    draw.rectangle([door_x, 25, w - 25, h - 25], fill=(170, 130, 80), outline=(90, 60, 30), width=2)
    # 变形凸起
    draw.ellipse([door_x + 10, h//3, w - 35, h*2//3], fill=(150, 110, 65), outline=(100, 70, 40), width=2)
    # 门锁杆
    draw.line([(door_x + 20, 30), (door_x + 20, h - 30)], fill=(80, 80, 80), width=3)
    return _add_noise(img, 6)


DAMAGE_GENERATORS = [
    gen_damage_none,
    gen_damage_left_dent,
    gen_damage_right_dent,
    gen_damage_top_rust,
    gen_damage_bottom_scratch,
    gen_damage_corner_deform,
    gen_damage_door_deform,
]


# ============ 堆码状态图像生成（12类）============
def _draw_container(draw, x, y, cw, ch, color=(180, 140, 90), tilt=0):
    """在指定位置绘制一个集装箱（支持倾斜）"""
    if tilt == 0:
        draw.rectangle([x, y, x + cw, y + ch], fill=color, outline=(70, 50, 30), width=2)
        for i in range(1, 4):
            lx = x + cw * i // 4
            draw.line([(lx, y + 3), (lx, y + ch - 3)], fill=(color[0]-20, color[1]-20, color[2]-20), width=1)
    else:
        # 倾斜：用多边形
        cx, cy = x + cw // 2, y + ch // 2
        rad = math.radians(tilt)
        corners = [(-cw//2, -ch//2), (cw//2, -ch//2), (cw//2, ch//2), (-cw//2, ch//2)]
        rotated = []
        for px, py in corners:
            rx = cx + px * math.cos(rad) - py * math.sin(rad)
            ry = cy + px * math.sin(rad) + py * math.cos(rad)
            rotated.append((rx, ry))
        draw.polygon(rotated, fill=color, outline=(70, 50, 30))


def gen_stack_normal(w=IMG_SIZE, h=IMG_SIZE):
    """0: 正常堆码 - 整齐2层"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    cw, ch = 80, 35
    _draw_container(draw, 30, 80, cw, ch, (180, 140, 90))
    _draw_container(draw, 115, 80, cw, ch, (160, 120, 80))
    _draw_container(draw, 30, 120, cw, ch, (170, 130, 85))
    _draw_container(draw, 115, 120, cw, ch, (190, 150, 100))
    return _add_noise(img, 5)


def gen_stack_single(w=IMG_SIZE, h=IMG_SIZE):
    """1: 单层平放"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 30, 100, 165, 40, (180, 140, 90))
    return _add_noise(img, 5)


def gen_stack_double_offset(w=IMG_SIZE, h=IMG_SIZE):
    """2: 双层错位"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 20, 120, 90, 35, (180, 140, 90))
    _draw_container(draw, 115, 120, 90, 35, (160, 120, 80))
    _draw_container(draw, 60, 80, 90, 35, (170, 130, 85))  # 错位
    return _add_noise(img, 5)


def gen_stack_triple(w=IMG_SIZE, h=IMG_SIZE):
    """3: 三层堆叠"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    cw, ch = 100, 30
    _draw_container(draw, 62, 50, cw, ch, (190, 150, 100))
    _draw_container(draw, 62, 85, cw, ch, (180, 140, 90))
    _draw_container(draw, 62, 120, cw, ch, (170, 130, 85))
    return _add_noise(img, 5)


def gen_stack_tilted(w=IMG_SIZE, h=IMG_SIZE):
    """4: 偏斜"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 50, 90, 130, 45, (180, 140, 90), tilt=12)
    return _add_noise(img, 5)


def gen_stack_overheight(w=IMG_SIZE, h=IMG_SIZE):
    """5: 超高 - 堆得很高"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    cw, ch = 100, 22
    for i, y in enumerate([15, 40, 65, 90, 115, 140]):
        color = [(190,150,100),(180,140,90),(170,130,85),(160,120,80),(185,145,95),(175,135,88)][i]
        _draw_container(draw, 62, y, cw, ch, color)
    return _add_noise(img, 5)


def gen_stack_inverted(w=IMG_SIZE, h=IMG_SIZE):
    """6: 倒置 - 倒过来（颜色+标记区分）"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 30, 90, 165, 45, (140, 100, 160))  # 异常颜色
    # 倒置标记：顶部有底座结构
    draw.rectangle([50, 85, 80, 95], fill=(100, 80, 60))
    draw.rectangle([145, 85, 175, 95], fill=(100, 80, 60))
    return _add_noise(img, 5)


def gen_stack_horizontal(w=IMG_SIZE, h=IMG_SIZE):
    """7: 横向放置 - 宽扁形"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 10, 95, 205, 35, (180, 140, 90))
    return _add_noise(img, 5)


def gen_stack_longitudinal_offset(w=IMG_SIZE, h=IMG_SIZE):
    """8: 纵向偏移"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 15, 75, 95, 35, (180, 140, 90))
    _draw_container(draw, 115, 75, 95, 35, (160, 120, 80))
    _draw_container(draw, 55, 115, 95, 35, (170, 130, 85))  # 纵向偏移
    _draw_container(draw, 155, 115, 55, 35, (190, 150, 100))
    return _add_noise(img, 5)


def gen_stack_corner_misalign(w=IMG_SIZE, h=IMG_SIZE):
    """9: 角件未对准"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 25, 80, 90, 35, (180, 140, 90))
    _draw_container(draw, 120, 80, 80, 35, (160, 120, 80))  # 宽度不同导致角件不对
    _draw_container(draw, 30, 120, 85, 35, (170, 130, 85))
    _draw_container(draw, 118, 120, 85, 35, (190, 150, 100))
    return _add_noise(img, 5)


def gen_stack_unstable(w=IMG_SIZE, h=IMG_SIZE):
    """10: 堆叠不稳 - 倾斜+错位"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 30, 120, 90, 35, (180, 140, 90))
    _draw_container(draw, 120, 120, 80, 35, (160, 120, 80))
    _draw_container(draw, 70, 80, 85, 35, (170, 130, 85), tilt=8)  # 上层倾斜
    return _add_noise(img, 5)


def gen_stack_empty(w=IMG_SIZE, h=IMG_SIZE):
    """11: 空箱堆码 - 颜色浅+标记"""
    img = Image.new('RGB', (w, h), (180, 190, 200))
    draw = ImageDraw.Draw(img)
    _draw_container(draw, 30, 80, 85, 35, (210, 200, 180))  # 浅色空箱
    _draw_container(draw, 115, 80, 85, 35, (215, 205, 185))
    _draw_container(draw, 30, 120, 85, 35, (205, 195, 175))
    _draw_container(draw, 115, 120, 85, 35, (220, 210, 190))
    # 空箱标记
    draw.text((95, 95), "EMPTY", fill=(150, 50, 50))
    return _add_noise(img, 5)


STACK_GENERATORS = [
    gen_stack_normal,
    gen_stack_single,
    gen_stack_double_offset,
    gen_stack_triple,
    gen_stack_tilted,
    gen_stack_overheight,
    gen_stack_inverted,
    gen_stack_horizontal,
    gen_stack_longitudinal_offset,
    gen_stack_corner_misalign,
    gen_stack_unstable,
    gen_stack_empty,
]


# ============ 数据集生成 ============
def generate_dataset(classes, generators, dataset_name):
    """生成 ImageFolder 格式数据集"""
    data_dir = os.path.join(DATA_ROOT, dataset_name)
    for split in ['train', 'val']:
        for idx, cls_name in enumerate(classes):
            cls_dir = os.path.join(data_dir, split, cls_name)
            os.makedirs(cls_dir, exist_ok=True)
            count = TRAIN_PER_CLASS if split == 'train' else VAL_PER_CLASS
            gen_fn = generators[idx]
            for i in range(count):
                img = gen_fn()
                # 随机轻微变换增加多样性
                if random.random() > 0.5:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                if random.random() > 0.7:
                    angle = random.uniform(-3, 3)
                    img = img.rotate(angle, fillcolor=(200, 200, 210))
                img.save(os.path.join(cls_dir, f'{split}_{idx}_{i:03d}.png'))
            print(f"  [{dataset_name}/{split}] {cls_name}: {count} images")
    return data_dir


# ============ 训练 ============
def get_loaders(data_dir, batch_size=BATCH_SIZE):
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
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_loader, val_loader, train_ds.classes


def build_resnet(num_classes, device):
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model.to(device)


def build_vit(num_classes, device):
    model = vit_b_16(weights=ViT_B_16_Weights.IMAGENET1K_V1)
    model.heads.head = nn.Linear(model.heads.head.in_features, num_classes)
    return model.to(device)


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

        # 验证
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        val_acc = val_correct / val_total

        print(f"  Epoch {epoch+1}/{epochs} - loss:{train_loss:.4f} train_acc:{train_acc:.4f} val_acc:{val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names': class_names,
                'best_acc': best_acc,
                'epoch': epoch + 1,
            }, save_path)
            print(f"  -> Saved best model (val_acc={best_acc:.4f}) to {save_path}")

    print(f"  Training complete. Best val_acc: {best_acc:.4f}")
    return best_acc


# ============ 主流程 ============
def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print(f"PyTorch version: {torch.__version__}")

    # 1. 生成破损检测数据集
    print("\n=== Step 1: Generate Damage Dataset (7 classes) ===")
    damage_dir = generate_dataset(DAMAGE_CLASSES, DAMAGE_GENERATORS, 'damage')
    print(f"Damage dataset generated at: {damage_dir}")

    # 2. 生成堆码状态数据集
    print("\n=== Step 2: Generate Stack Dataset (12 classes) ===")
    stack_dir = generate_dataset(STACK_CLASSES, STACK_GENERATORS, 'stack')
    print(f"Stack dataset generated at: {stack_dir}")

    # 3. 训练破损检测模型
    print("\n=== Step 3: Train Damage Detection Model (ResNet50) ===")
    train_loader, val_loader, class_names = get_loaders(damage_dir)
    print(f"Classes: {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    model = build_resnet(len(class_names), device)
    train_model(model, train_loader, val_loader, EPOCHS, LR, device, Config.DAMAGE_WEIGHTS, class_names)
    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # 4. 训练堆码分类模型
    print("\n=== Step 4: Train Stack Classification Model (ViT-B/16) ===")
    train_loader, val_loader, class_names = get_loaders(stack_dir)
    print(f"Classes: {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    model = build_vit(len(class_names), device)
    train_model(model, train_loader, val_loader, EPOCHS, LR, device, Config.STACK_WEIGHTS, class_names)
    del model

    print("\n=== All Done ===")
    print(f"Damage weights: {Config.DAMAGE_WEIGHTS}")
    print(f"Stack weights: {Config.STACK_WEIGHTS}")
    print("OCR uses RapidOCR (ONNX), no weights file needed.")


if __name__ == '__main__':
    main()
