import os
import sys
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from services import OCRService, DamageService, StackService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 初始化AI服务
ocr_service = OCRService()
damage_service = DamageService()
stack_service = StackService()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'AI Inspection Service',
        'models': {
            'ocr_det': Config.OCR_DET_MODEL,
            'ocr_rec': Config.OCR_REC_MODEL,
            'damage': Config.DAMAGE_MODEL,
            'stack': Config.STACK_MODEL
        },
        'metrics': {
            'damage_mAP': Config.DAMAGE_METRIC,
            'stack_accuracy': Config.STACK_ACCURACY
        }
    })


@app.route('/api/ocr', methods=['POST'])
def ocr_recognize():
    """箱号OCR识别"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 400

        start = time.time()
        container_no = ocr_service.recognize(image_path)
        cost_ms = int((time.time() - start) * 1000)

        return jsonify({
            'ocrResult': container_no,
            'costMs': cost_ms,
            'model': f"{Config.OCR_DET_MODEL} + {Config.OCR_REC_MODEL}"
        })
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/damage', methods=['POST'])
def damage_detect():
    """破损检测"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 400

        start = time.time()
        result = damage_service.detect(image_path)
        result['costMs'] = int((time.time() - start) * 1000)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Damage detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stack', methods=['POST'])
def stack_classify():
    """堆码状态判定"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 400

        start = time.time()
        result = stack_service.classify(image_path)
        result['costMs'] = int((time.time() - start) * 1000)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Stack classification error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/inspect', methods=['POST'])
def inspect():
    """综合检测：OCR + 破损 + 堆码"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        if not image_path or not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 400

        start = time.time()

        # 1. OCR箱号识别
        ocr_result = ocr_service.recognize(image_path)

        # 2. 破损检测
        damage_result = damage_service.detect(image_path)

        # 3. 堆码状态判定
        stack_result = stack_service.classify(image_path)

        total_cost = int((time.time() - start) * 1000)

        # 综合置信度（取三者平均）
        avg_confidence = round((damage_result['confidence'] + stack_result['confidence']) / 2, 3)

        return jsonify({
            'ocrResult': ocr_result,
            'damageResult': damage_result['damage_result'],
            'damageLevel': damage_result['damage_level'],
            'stackResult': stack_result['stack_result'],
            'confidence': avg_confidence,
            'costMs': total_cost,
            'details': {
                'ocr': {'model': f"{Config.OCR_DET_MODEL} + {Config.OCR_REC_MODEL}"},
                'damage': {'model': Config.DAMAGE_MODEL, 'metric': Config.DAMAGE_METRIC},
                'stack': {'model': Config.STACK_MODEL, 'accuracy': Config.STACK_ACCURACY}
            }
        })
    except Exception as e:
        logger.error(f"Inspect error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    logger.info(f"Starting AI Inspection Service on port {Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
