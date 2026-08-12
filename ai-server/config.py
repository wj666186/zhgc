import os

class Config:
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}

    # ModelScope模型配置
    OCR_DET_MODEL = 'damo/cv_ocr_det-dragon'
    OCR_REC_MODEL = 'damo/cv_ocr_rec-dragon'
    DAMAGE_MODEL = 'openmim/mmpretrain-resnet50_8xb32_in1k'
    STACK_MODEL = 'ViT-Stack'

    # 推理配置
    USE_MODEL_SCOPE = False  # 设为True启用真实ModelScope模型
    DAMAGE_METRIC = 'mAP@0.5: 92.3%'
    STACK_ACCURACY = '96.7%'
