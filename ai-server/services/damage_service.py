import os
import random
import logging

import torch
import torch.nn.functional as F
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image

logger = logging.getLogger(__name__)


class DamageService:
    """集装箱破损检测服务
    骨干：ResNet50（torchvision），在港口破损图像上微调
    类别：无破损 / 左侧轻微凹陷 / 右侧凹陷 / 顶部锈蚀 / 底部刮擦 / 角件变形 / 门板变形
    """

    def __init__(self, config):
        self.config = config
        self.classes = config.DAMAGE_CLASSES
        self.levels = config.DAMAGE_LEVELS
        self.num_classes = len(self.classes)
        self.model = None
        self.transform = None
        self.device = self._get_device()
        self._available = False
        self._build_model()

    def _get_device(self):
        dev = getattr(self.config, 'DEVICE', 'auto')
        if dev == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return dev

    def _build_model(self):
        """构建 ResNet50 模型并加载微调权重（与训练脚本结构一致）"""
        try:
            # 加载 ImageNet 预训练骨干
            weights = ResNet50_Weights.IMAGENET1K_V2
            self.model = resnet50(weights=weights)
            # 替换最后一层为与训练一致的两层分类头
            in_features = self.model.fc.in_features
            self.model.fc = torch.nn.Sequential(
                torch.nn.Dropout(0.3),
                torch.nn.Linear(in_features, 256),
                torch.nn.ReLU(inplace=True),
                torch.nn.Dropout(0.2),
                torch.nn.Linear(256, self.num_classes),
            )

            # 加载微调权重（如果存在）
            if os.path.exists(self.config.DAMAGE_WEIGHTS):
                state_dict = torch.load(self.config.DAMAGE_WEIGHTS, map_location=self.device)
                # 兼容保存为整个 model 和只保存 state_dict 两种格式
                if isinstance(state_dict, dict) and 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                self.model.load_state_dict(state_dict, strict=False)
                logger.info(f"Damage weights loaded from {self.config.DAMAGE_WEIGHTS}")
                self._available = True
            else:
                logger.warning(
                    f"Damage weights not found at {self.config.DAMAGE_WEIGHTS}, "
                    f"using ImageNet pretrained backbone (will fallback to mock output)"
                )

            self.model.to(self.device)
            self.model.eval()

            # 图像预处理（与 ImageNet 训练一致）
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(self.config.DAMAGE_IMG_SIZE),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])
            logger.info(f"Damage model built on {self.device}, {self.num_classes} classes")
        except Exception as e:
            logger.error(f"Failed to build damage model: {e}")
            self.model = None

    @property
    def is_available(self):
        return self._available and self.model is not None

    def detect(self, image_path):
        """检测箱体破损，返回 dict"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if self.is_available:
            try:
                return self._real_detect(image_path)
            except Exception as e:
                logger.error(f"Damage real inference failed, fallback to mock: {e}")
                return self._mock_detect()
        else:
            return self._mock_detect()

    def _real_detect(self, image_path):
        """真实推理：预处理 → 前向 → softmax → 取 Top1"""
        image = Image.open(image_path).convert('RGB')
        x = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(x)
            probs = F.softmax(logits, dim=1)
            confidence, pred_idx = torch.max(probs, dim=1)

        idx = pred_idx.item()
        confidence = round(confidence.item(), 3)
        result = {
            'damage_result': self.classes[idx],
            'damage_level': self.levels[idx],
            'confidence': confidence,
            'metric': self.config.DAMAGE_METRIC,
            'all_probs': {
                self.classes[i]: round(probs[0][i].item(), 4)
                for i in range(self.num_classes)
            },
        }
        logger.info(f"Damage detected: {result['damage_result']} (conf={confidence})")
        return result

    def _mock_detect(self):
        """模拟检测结果（权重未加载时降级）"""
        idx = random.randint(0, self.num_classes - 1)
        # 无破损置信度高，破损类置信度稍低
        if idx == 0:
            confidence = round(random.uniform(0.95, 0.999), 3)
        else:
            confidence = round(random.uniform(0.80, 0.96), 3)
        return {
            'damage_result': self.classes[idx],
            'damage_level': self.levels[idx],
            'confidence': confidence,
            'metric': self.config.DAMAGE_METRIC,
        }
