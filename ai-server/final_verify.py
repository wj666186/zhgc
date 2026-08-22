import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from services.ocr_service import OCRService
from services.damage_service import DamageService

print('=' * 60)
print('最终模型验证')
print('=' * 60)

# OCR验证
print('\n--- 箱号OCR识别 ---')
ocr = OCRService(Config)
ocr_dir = 'data/real_dataset/ocr_train'
files = sorted([f for f in os.listdir(ocr_dir) if f.endswith('.jpg')])[:30]
ocr_correct = 0
ocr_total = 0
for f in files:
    expected = f.replace('ocr_', '').split('_')[1].replace('.jpg', '')
    result = ocr.recognize(os.path.join(ocr_dir, f))
    if result == expected:
        ocr_correct += 1
    ocr_total += 1
print(f'OCR准确率: {ocr_correct}/{ocr_total} = {ocr_correct/ocr_total*100:.1f}%')

# 破损检测验证
print('\n--- 破损检测（10张测试图）---')
damage = DamageService(Config)
test_labels = {
    'container_01.jpg': '无破损',
    'container_02.jpg': '左侧轻微凹陷',
    'container_03.jpg': '顶部锈蚀',
    'container_04.jpg': '无破损',
    'container_05.jpg': '底部刮擦',
    'container_06.jpg': '无破损',
    'container_07.jpg': '无破损',
    'container_08.jpg': '角件变形',
    'container_09.jpg': '无破损',
    'container_10.jpg': '门板变形',
}
dmg_correct = 0
dmg_total = 0
for fname, expected in sorted(test_labels.items()):
    path = os.path.join('uploads/test_images', fname)
    if not os.path.exists(path):
        continue
    result = damage.detect(path)
    pred = result['damage_result']
    conf = result['confidence']
    hit = pred == expected
    if hit:
        dmg_correct += 1
    dmg_total += 1
    status = 'OK' if hit else f'FAIL(expect:{expected})'
    print(f'  {fname:20s} pred:{pred:10s} conf:{conf:.3f} {status}')
print(f'破损检测准确率: {dmg_correct}/{dmg_total} = {dmg_correct/dmg_total*100:.1f}%')

print('\n' + '=' * 60)
print(f'总结: OCR={ocr_correct/ocr_total*100:.0f}%, 破损检测={dmg_correct/dmg_total*100:.0f}%')
print('=' * 60)
