"""
破损检测模型训练脚本（ResNet50 微调）
数据集路径：data/damage/train 和 data/damage/val（ImageFolder 格式）
类别顺序需与 config.py 中 DAMAGE_CLASSES 一致：
  0=无破损, 1=左侧轻微凹陷, 2=右侧凹陷, 3=顶部锈蚀, 4=底部刮擦, 5=角件变形, 6=门板变形

用法：
  python train_damage.py --data_dir ./data/damage --epochs 30 --batch_size 32 --lr 1e-4
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from train_utils import load_data, build_resnet50, run_training


def main():
    parser = argparse.ArgumentParser(description='Train Damage Detection (ResNet50)')
    parser.add_argument('--data_dir', type=str, default='./data/damage', help='数据集根目录')
    parser.add_argument('--epochs', type=int, default=30, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32, help='批大小')
    parser.add_argument('--lr', type=float, default=1e-4, help='学习率')
    parser.add_argument('--img_size', type=int, default=224, help='输入图像尺寸')
    parser.add_argument('--save_path', type=str, default=Config.DAMAGE_WEIGHTS, help='权重保存路径')
    args = parser.parse_args()

    device = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    train_loader, val_loader, class_names = load_data(
        args.data_dir, img_size=args.img_size, batch_size=args.batch_size,
    )
    print(f"Classes ({len(class_names)}): {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

    model = build_resnet50(num_classes=len(class_names), device=device)
    run_training(model, train_loader, val_loader, args.epochs, args.lr, device, args.save_path, class_names)


if __name__ == '__main__':
    main()
