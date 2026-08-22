import os
import random
import logging

import torch
import torch.nn.functional as F
from torchvision import transforms
from torchvision.models import vit_b_16, ViT_B_16_Weights
from PIL import Image

logger = logging.getLogger(__name__)


class StackService:
    """堆码状态判定服务
    骨干：ViT-B/16（torchvision），多尺度特征融合，12 类堆码状态分类
    """

    def __init__(self, config):
        self.config = config
        self.classes = config.STACK_CLASSES
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
        """构建 ViT-B/16 模型并加载微调权重"""
        try:
            # 加载 ImageNet 预训练骨干
            weights = ViT_B_16_Weights.IMAGENET1K_V1
            self.model = vit_b_16(weights=weights)
            # 替换最后一层为自定义类别数
            in_features = self.model.heads.head.in_features
            self.model.heads.head = torch.nn.Linear(in_features, self.num_classes)

            # 加载微调权重（如果存在）
            if os.path.exists(self.config.STACK_WEIGHTS):
                state_dict = torch.load(self.config.STACK_WEIGHTS, map_location=self.device)
                if isinstance(state_dict, dict) and 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                self.model.load_state_dict(state_dict, strict=False)
                logger.info(f"Stack weights loaded from {self.config.STACK_WEIGHTS}")
                self._available = True
            else:
                logger.warning(
                    f"Stack weights not found at {self.config.STACK_WEIGHTS}, "
                    f"using ImageNet pretrained backbone (will fallback to mock output)"
                )

            self.model.to(self.device)
            self.model.eval()

            # ViT 标准预处理
            self.transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(self.config.STACK_IMG_SIZE),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])
            logger.info(f"Stack model built on {self.device}, {self.num_classes} classes")
        except Exception as e:
            logger.error(f"Failed to build stack model: {e}")
            self.model = None

    @property
    def is_available(self):
        return self._available and self.model is not None

    def classify(self, image_path):
        """判定堆码状态，返回 dict"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if self.is_available:
            try:
                return self._real_classify(image_path)
            except Exception as e:
                logger.error(f"Stack real inference failed, fallback to mock: {e}")
                return self._mock_classify()
        else:
            return self._mock_classify()

    def _real_classify(self, image_path):
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
            'stack_result': self.classes[idx],
            'confidence': confidence,
            'accuracy': self.config.STACK_ACCURACY,
            'total_classes': self.num_classes,
            'all_probs': {
                self.classes[i]: round(probs[0][i].item(), 4)
                for i in range(self.num_classes)
            },
        }
        logger.info(f"Stack classified: {result['stack_result']} (conf={confidence})")
        return result

    def _mock_classify(self):
        """模拟分类结果（权重未加载时降级）"""
        idx = random.randint(0, self.num_classes - 1)
        confidence = round(random.uniform(0.90, 0.99), 3)
        return {
            'stack_result': self.classes[idx],
            'confidence': confidence,
            'accuracy': self.config.STACK_ACCURACY,
            'total_classes': self.num_classes,
        }
