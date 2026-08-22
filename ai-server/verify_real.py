"""全面验证：OCR准确率 + 破损/堆码在训练集图片上的召回率"""
import os, sys, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from services import OCRService, DamageService, StackService

BASE = os.path.dirname(os.path.abspath(__file__))
ocr = OCRService(Config)
damage = DamageService(Config)
stack = StackService(Config)

# ========== 1. OCR 准确率（精确绘制的80张）==========
print("=" * 60)
print("1. OCR 识别准确率（精确绘制数据集，前20张）")
print("=" * 60)
ocr_dir = os.path.join(BASE, 'data', 'real_dataset', 'ocr_train')
pattern = re.compile(r'[A-Z]{4}\d{7}')
correct = 0
total = 0
files = sorted([f for f in os.listdir(ocr_dir) if f.endswith('.jpg')])[:20]
for f in files:
    expected = f.replace('ocr_', '').split('_')[1].replace('.jpg', '')
    path = os.path.join(ocr_dir, f)
    result, _ = ocr.engine(path)
    texts = [item[1] for item in result] if result else []
    recognized = 'UNKNOWN'
    for t in texts:
        m = pattern.search(t.upper())
        if m:
            recognized = m.group()
            break
    hit = recognized == expected
    if hit:
        correct += 1
    total += 1
    status = "✅" if hit else f"❌(识别:{recognized})"
    print(f"  {f[:30]:32s} 期望:{expected} {status}")
print(f"\nOCR 准确率: {correct}/{total} = {correct/total*100:.0f}%")

# ========== 2. 破损检测在训练集图片上的召回率 ==========
print("\n" + "=" * 60)
print("2. 破损检测 - 训练集图片召回率（每类2张）")
print("=" * 60)
damage_raw = os.path.join(BASE, 'data', 'real_dataset', 'damage_raw')
damage_correct = 0
damage_total = 0
for cls_dir in sorted(os.listdir(damage_raw)):
    full_dir = os.path.join(damage_raw, cls_dir)
    if not os.path.isdir(full_dir):
        continue
    cls_name = cls_dir.split('_', 1)[1] if '_' in cls_dir else cls_dir
    files = [f for f in os.listdir(full_dir) if f.endswith(('.jpg', '.png'))][:2]
    for f in files:
        path = os.path.join(full_dir, f)
        result = damage.detect(path)
        pred = result['damage_result']
        hit = pred == cls_name
        if hit:
            damage_correct += 1
        damage_total += 1
        status = "✅" if hit else f"❌(预测:{pred})"
        print(f"  [{cls_name:8s}] {f:20s} conf={result['confidence']:.3f} {status}")
print(f"\n破损检测召回率: {damage_correct}/{damage_total} = {damage_correct/damage_total*100:.0f}%")

# ========== 3. 堆码分类在训练集图片上的召回率 ==========
print("\n" + "=" * 60)
print("3. 堆码分类 - 训练集图片召回率（每类2张）")
print("=" * 60)
stack_raw = os.path.join(BASE, 'data', 'real_dataset', 'stack_raw')
stack_correct = 0
stack_total = 0
for cls_dir in sorted(os.listdir(stack_raw)):
    full_dir = os.path.join(stack_raw, cls_dir)
    if not os.path.isdir(full_dir):
        continue
    cls_name = cls_dir.split('_', 1)[1] if '_' in cls_dir else cls_dir
    files = [f for f in os.listdir(full_dir) if f.endswith(('.jpg', '.png'))][:2]
    for f in files:
        path = os.path.join(full_dir, f)
        result = stack.classify(path)
        pred = result['stack_result']
        hit = pred == cls_name
        if hit:
            stack_correct += 1
        stack_total += 1
        status = "✅" if hit else f"❌(预测:{pred})"
        print(f"  [{cls_name:8s}] {f:20s} conf={result['confidence']:.3f} {status}")
print(f"\n堆码分类召回率: {stack_correct}/{stack_total} = {stack_correct/stack_total*100:.0f}%")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print(f"OCR准确率: {correct/total*100:.0f}% (精确绘制箱号图片)")
print(f"破损检测召回率: {damage_correct/damage_total*100:.0f}% (训练集图片)")
print(f"堆码分类召回率: {stack_correct/stack_total*100:.0f}% (训练集图片)")
