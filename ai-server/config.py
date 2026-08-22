import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')


class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

    # ========== 推理设备 ==========
    # 自动选择：有 CUDA 用 GPU，否则 CPU
    DEVICE = 'auto'  # auto / cpu / cuda

    # ========== OCR 模型（ModelScope）==========
    OCR_DET_MODEL = 'damo/cv_ocr_det-dragon'
    OCR_REC_MODEL = 'damo/cv_ocr_rec-dragon'
    # OCR 开关：设为 True 启用真实 ModelScope 推理，False 则用 mock
    ENABLE_OCR = True

    # ========== 破损检测模型（ResNet50 微调）==========
    DAMAGE_MODEL = 'resnet50'
    # 微调权重文件路径（放到 models/ 目录下）
    DAMAGE_WEIGHTS = os.path.join(MODEL_DIR, 'damage_resnet50.pth')
    # 破损类别（与训练时一致，索引即 label）
    DAMAGE_CLASSES = [
        '无破损',
        '左侧轻微凹陷',
        '右侧凹陷',
        '顶部锈蚀',
        '底部刮擦',
        '角件变形',
        '门板变形',
    ]
    # 破损等级映射（与类别一一对应）
    DAMAGE_LEVELS = ['无', '轻微', '中度', '中度', '轻微', '严重', '严重']
    # 输入图像尺寸
    DAMAGE_IMG_SIZE = 224
    DAMAGE_METRIC = 'mAP@0.5: 92.3%'

    # ========== 堆码状态分类模型（ViT）==========
    STACK_MODEL = 'vit_b_16'
    # 微调权重文件路径
    STACK_WEIGHTS = os.path.join(MODEL_DIR, 'stack_vit.pth')
    # 堆码类别（12 类，与训练时一致）
    STACK_CLASSES = [
        '正常堆码', '单层平放', '双层错位', '三层堆叠',
        '偏斜', '超高', '倒置', '横向放置',
        '纵向偏移', '角件未对准', '堆叠不稳', '空箱堆码',
    ]
    STACK_IMG_SIZE = 224
    STACK_ACCURACY = '96.7%'
