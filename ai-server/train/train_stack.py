"""
堆码状态分类模型训练脚本（ViT-B/16 微调）
数据集路径：data/stack/train 和 data/stack/val（ImageFolder 格式）
类别顺序需与 config.py 中 STACK_CLASSES 一致（12 类）

用法：
  python train_stack.py --data_dir ./data/stack --epochs 30 --batch_size 32 --lr 1e-4
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from train_utils import load_data, build_vit, run_training


def main():
    parser = argparse.ArgumentParser(description='Train Stack Classification (ViT-B/16)')
    parser.add_argument('--data_dir', type=str, default='./data/stack', help='数据集根目录')
    parser.add_argument('--epochs', type=int, default=30, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=32, help='批大小')
    parser.add_argument('--lr', type=float, default=1e-4, help='学习率')
    parser.add_argument('--img_size', type=int, default=224, help='输入图像尺寸')
    parser.add_argument('--save_path', type=str, default=Config.STACK_WEIGHTS, help='权重保存路径')
    args = parser.parse_args()

    device = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    train_loader, val_loader, class_names = load_data(
        args.data_dir, img_size=args.img_size, batch_size=args.batch_size,
    )
    print(f"Classes ({len(class_names)}): {class_names}")
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

    model = build_vit(num_classes=len(class_names), device=device)
    run_training(model, train_loader, val_loader, args.epochs, args.lr, device, args.save_path, class_names)


if __name__ == '__main__':
    main()
