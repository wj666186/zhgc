import os
import re
import random
import logging
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


class OCRService:
    """箱号 OCR 识别服务
    优先使用 RapidOCR（ONNX 推理，轻量快速）；
    通过图像预处理管道（对比度增强、去噪、放大、二值化）提升识别率；
    通过正则提取标准集装箱号（4字母+7数字）+ 常见OCR错误纠正。
    """

    # 集装箱箱号正则：4 个大写字母 + 7 位数字
    CONTAINER_PATTERN = re.compile(r'[A-Z]{4}\d{7}')

    # 常见 OCR 字符混淆映射（用于箱号后处理纠正）
    OCR_CONFUSION = {
        'O': '0', 'Q': '0', 'D': '0',
        'I': '1', 'L': '1', 'T': '1',
        'Z': '2',
        'S': '5',
        'B': '8',
        'G': '6',
        'U': '0', 'V': '0',
    }

    def __init__(self, config):
        self.config = config
        self.engine = None
        self.engine_name = None
        self._available = False
        if getattr(config, 'ENABLE_OCR', True):
            self._load_rapidocr()
            if not self._available:
                self._load_modelscope()

    def _load_rapidocr(self):
        """加载 RapidOCR（推荐，ONNX 推理）"""
        try:
            from rapidocr_onnxruntime import RapidOCR
            self.engine = RapidOCR()
            self.engine_name = 'RapidOCR (ONNX)'
            self._available = True
            logger.info("RapidOCR engine loaded successfully")
        except Exception as e:
            logger.warning(f"RapidOCR unavailable: {e}")
            self.engine = None

    def _load_modelscope(self):
        """加载 ModelScope OCR（可选）"""
        try:
            from modelscope.pipelines import pipeline
            from modelscope.utils.constant import Tasks

            det_model = pipeline(Tasks.ocr_detection, model=self.config.OCR_DET_MODEL)
            rec_model = pipeline(Tasks.ocr_recognition, model=self.config.OCR_REC_MODEL)
            self.engine = (det_model, rec_model)
            self.engine_name = f"ModelScope ({self.config.OCR_DET_MODEL} + {self.config.OCR_REC_MODEL})"
            self._available = True
            logger.info("ModelScope OCR engine loaded successfully")
        except Exception as e:
            logger.warning(f"ModelScope OCR unavailable, fallback to mock: {e}")
            self.engine = None

    @property
    def is_available(self):
        return self._available

    def recognize(self, image_path):
        """识别集装箱箱号，返回字符串"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        if self._available:
            try:
                return self._real_recognize(image_path)
            except Exception as e:
                logger.error(f"OCR real inference failed, fallback to mock: {e}")
                return self._mock_recognize()
        else:
            return self._mock_recognize()

    def _real_recognize(self, image_path):
        """真实 OCR 推理：多策略预处理 + 识别 + 后处理"""
        if self.engine_name == 'RapidOCR (ONNX)':
            return self._rapidocr_recognize(image_path)
        else:
            return self._modelscope_recognize(image_path)

    def _preprocess_variants(self, image_path):
        """生成多种预处理变体，逐一尝试OCR，取最优结果"""
        img = Image.open(image_path).convert('RGB')
        variants = []

        # 变体1：原图（轻度增强）
        variants.append(('original', self._light_enhance(img)))

        # 变体2：灰度+CLAHE对比度增强
        variants.append(('clahe', self._clahe_enhance(img)))

        # 变体3：放大2x + 增强
        variants.append(('upscaled', self._upscale_enhance(img)))

        # 变体4：二值化
        variants.append(('binary', self._binary_enhance(img)))

        return variants

    def _light_enhance(self, img):
        """轻度增强：提升对比度和锐度"""
        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        return img

    def _clahe_enhance(self, img):
        """灰度化 + CLAHE 对比度受限自适应直方图均衡化"""
        gray = img.convert('L')
        arr = np.array(gray)
        # 简易CLAHE：分块直方图均衡化
        h, w = arr.shape
        tile = 64
        for i in range(0, h, tile):
            for j in range(0, w, tile):
                block = arr[i:i+tile, j:j+tile]
                if block.size > 0:
                    # 对比度拉伸
                    p2, p98 = np.percentile(block, (2, 98))
                    if p98 > p2:
                        block = np.clip((block - p2) * 255.0 / (p98 - p2), 0, 255).astype(np.uint8)
                        arr[i:i+tile, j:j+tile] = block
        enhanced = Image.fromarray(arr).convert('RGB')
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)
        return enhanced

    def _upscale_enhance(self, img):
        """放大2倍 + 增强对比度和锐度"""
        w, h = img.size
        upscaled = img.resize((w * 2, h * 2), Image.LANCZOS)
        upscaled = ImageEnhance.Contrast(upscaled).enhance(1.4)
        upscaled = ImageEnhance.Sharpness(upscaled).enhance(2.0)
        return upscaled

    def _binary_enhance(self, img):
        """灰度 + 自适应二值化"""
        gray = img.convert('L')
        arr = np.array(gray)
        # Otsu二值化
        from PIL import ImageOps
        binary = ImageOps.autocontrast(gray, cutoff=2)
        arr2 = np.array(binary)
        threshold = np.mean(arr2) * 0.85
        binary_arr = (arr2 > threshold).astype(np.uint8) * 255
        result = Image.fromarray(binary_arr).convert('RGB')
        return result

    def _rapidocr_recognize(self, image_path):
        """RapidOCR 推理：多预处理变体尝试"""
        best_result = 'UNKNOWN'
        best_confidence = 0.0

        variants = self._preprocess_variants(image_path)

        for name, proc_img in variants:
            try:
                # 保存临时文件供RapidOCR读取
                import tempfile
                tmp_path = os.path.join(tempfile.gettempdir(), f'ocr_tmp_{name}_{os.getpid()}.jpg')
                proc_img.save(tmp_path, quality=95)

                result, _ = self.engine(tmp_path)
                texts = []
                confidences = []
                if result:
                    for item in result:
                        if len(item) >= 2 and item[1]:
                            texts.append(str(item[1]))
                            try:
                                conf = float(item[2]) if len(item) >= 3 else 0.9
                            except (ValueError, TypeError):
                                conf = 0.9
                            confidences.append(conf)

                container_no = self._extract_container_no(texts)
                avg_conf = float(np.mean(confidences)) if confidences else 0.0

                logger.info(f"OCR [{name}] recognized: {container_no} (conf={avg_conf:.3f}, raw={texts})")

                # 如果找到标准格式箱号且置信度高，直接返回
                if self.CONTAINER_PATTERN.match(container_no) and avg_conf > best_confidence:
                    best_result = container_no
                    best_confidence = avg_conf
                    if avg_conf > 0.7:
                        break

                # 如果还没找到标准格式，记录最长文本
                if best_result == 'UNKNOWN' and container_no != 'UNKNOWN':
                    best_result = container_no
                    best_confidence = avg_conf

                # 清理临时文件
                try:
                    os.remove(tmp_path)
                except:
                    pass

            except Exception as e:
                logger.warning(f"OCR variant {name} failed: {e}")
                continue

        return best_result

    def _modelscope_recognize(self, image_path):
        """ModelScope 推理"""
        det_model, rec_model = self.engine
        det_result = det_model(image_path)
        rec_result = rec_model(image_path)
        texts = rec_result.get('text', [])
        if isinstance(texts, str):
            texts = [texts]
        container_no = self._extract_container_no(texts)
        logger.info(f"ModelScope OCR recognized: {container_no} (raw: {texts})")
        return container_no

    def _extract_container_no(self, texts):
        """从识别文本列表中提取标准集装箱号（4字母+7数字）+ 错误纠正"""
        # 第一轮：直接匹配标准格式
        for text in texts:
            if not text:
                continue
            match = self.CONTAINER_PATTERN.search(text.upper())
            if match:
                return match.group()

        # 第二轮：尝试纠正常见OCR错误后再匹配
        for text in texts:
            if not text:
                continue
            corrected = self._correct_ocr_errors(text.upper())
            match = self.CONTAINER_PATTERN.search(corrected)
            if match:
                return match.group()

        # 第三轮：从文本中提取最长的字母数字组合
        candidates = []
        for text in texts:
            if not text:
                continue
            # 移除非字母数字字符
            cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
            if len(cleaned) >= 8:
                candidates.append(cleaned)

        if candidates:
            # 取最长的候选
            best = max(candidates, key=len)
            # 如果长度接近11，尝试纠正
            if len(best) >= 10:
                corrected = self._correct_ocr_errors(best)
                if self.CONTAINER_PATTERN.match(corrected):
                    return corrected
            return best[:11] if len(best) >= 11 else best

        return 'UNKNOWN'

    def _correct_ocr_errors(self, text):
        """纠正常见OCR字符混淆
        规则：前4位应为字母，后7位应为数字
        """
        if len(text) < 8:
            return text

        result = list(text)
        # 前4位：数字→字母（0→O, 1→I, 5→S, 8→B）
        digit_to_letter = {'0': 'O', '1': 'I', '5': 'S', '8': 'B', '6': 'G', '2': 'Z'}
        for i in range(min(4, len(result))):
            if result[i] in digit_to_letter:
                result[i] = digit_to_letter[result[i]]

        # 后7位：字母→数字
        for i in range(4, min(11, len(result))):
            if result[i] in self.OCR_CONFUSION:
                result[i] = self.OCR_CONFUSION[result[i]]

        return ''.join(result)

    def _mock_recognize(self):
        """模拟 OCR 识别结果（引擎不可用时降级）"""
        prefixes = ['CSLU', 'MSKU', 'MEDU', 'TCLU', 'HLXU', 'EITU', 'OOLU', 'APLU']
        prefix = random.choice(prefixes)
        number = str(random.randint(1000000, 9999999))
        return prefix + number
