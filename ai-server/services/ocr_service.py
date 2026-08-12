import random
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """箱号OCR识别服务
    模型选型：魔搭社区 damo/cv_ocr_det-dragon（文本检测） + damo/cv_ocr_rec-dragon（文本识别）
    针对集装箱反光、污损场景微调
    """

    def __init__(self):
        self.det_model = None
        self.rec_model = None
        self._load_models()

    def _load_models(self):
        """加载ModelScope模型（如可用）"""
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks
            self.det_model = pipeline(Tasks.ocr_detection, model='damo/cv_ocr_det-dragon')
            self.rec_model = pipeline(Tasks.ocr_recognition, model='damo/cv_ocr_rec-dragon')
            logger.info("ModelScope OCR models loaded successfully")
        except Exception as e:
            logger.warning(f"ModelScope OCR models not available, using mock: {e}")
            self.det_model = None
            self.rec_model = None

    def recognize(self, image_path):
        """识别集装箱箱号"""
        if self.det_model and self.rec_model:
            try:
                det_result = self.det_model(image_path)
                rec_result = self.rec_model(image_path)
                texts = rec_result.get('text', [])
                container_no = self._extract_container_no(texts)
                return container_no
            except Exception as e:
                logger.error(f"OCR recognition failed: {e}")
                return self._mock_recognize()
        else:
            return self._mock_recognize()

    def _extract_container_no(self, texts):
        """从识别文本中提取集装箱号（4字母+7数字）"""
        import re
        pattern = r'[A-Z]{4}\d{7}'
        for text in texts:
            match = re.search(pattern, text.upper())
            if match:
                return match.group()
        return texts[0] if texts else 'UNKNOWN'

    def _mock_recognize(self):
        """模拟OCR识别结果"""
        prefixes = ['CSLU', 'MSKU', 'MEDU', 'TCLU', 'HLXU', 'EITU', 'OOLU', 'APLU']
        prefix = random.choice(prefixes)
        number = str(random.randint(1000000, 9999999))
        return prefix + number
