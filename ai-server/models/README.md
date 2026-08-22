# 模型权重目录

将训练好的模型权重文件放到此目录下，文件名需与 `config.py` 中配置一致：

| 文件 | 对应模型 | 说明 |
|------|----------|------|
| `damage_resnet50.pth` | 破损检测（ResNet50） | 7 类破损分类微调权重 |
| `stack_vit.pth` | 堆码分类（ViT-B/16） | 12 类堆码状态微调权重 |

## 权重格式

支持两种保存格式，加载时自动兼容：

1. **仅 state_dict**（推荐）：
   ```python
   torch.save(model.state_dict(), 'damage_resnet50.pth')
   ```

2. **包含元信息的 dict**（训练脚本默认格式）：
   ```python
   torch.save({
       'model_state_dict': model.state_dict(),
       'class_names': [...],
       'best_acc': 0.92,
       'epoch': 30,
   }, 'damage_resnet50.pth')
   ```

## 训练权重

使用 `train/` 目录下的脚本训练：

```bash
# 破损检测
python train/train_damage.py --data_dir ./data/damage --epochs 30

# 堆码分类
python train/train_stack.py --data_dir ./data/stack --epochs 30
```

数据集需为 ImageFolder 格式（每个子文件夹为一个类别），类别顺序需与 `config.py` 中 `DAMAGE_CLASSES` / `STACK_CLASSES` 一致。

## 注意

- 权重文件未放置时，服务会自动降级到 mock 输出，不影响接口可用性
- OCR 模型由 ModelScope 自动下载缓存，无需手动放置
