"""诊断当前模型在10张测试图上的表现"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from services import OCRService, DamageService, StackService

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'test_images')

print("加载模型...")
ocr = OCRService(Config)
damage = DamageService(Config)
stack = StackService(Config)
print(f"OCR available: {ocr.is_available} ({ocr.engine_name})")
print(f"Damage available: {damage.is_available}")
print(f"Stack available: {stack.is_available}")
print()

files = sorted([f for f in os.listdir(TEST_DIR) if f.endswith(('.jpg', '.png'))])
for f in files:
    path = os.path.join(TEST_DIR, f)
    print(f"--- {f} ---")
    # OCR
    try:
        ocr_result = ocr.recognize(path)
        print(f"  OCR: {ocr_result}")
    except Exception as e:
        print(f"  OCR error: {e}")
    # Damage
    try:
        d = damage.detect(path)
        print(f"  破损: {d['damage_result']} (conf={d['confidence']}, level={d['damage_level']})")
    except Exception as e:
        print(f"  Damage error: {e}")
    # Stack
    try:
        s = stack.classify(path)
        print(f"  堆码: {s['stack_result']} (conf={s['confidence']})")
    except Exception as e:
        print(f"  Stack error: {e}")
    print()
