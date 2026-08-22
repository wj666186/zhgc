"""
验证三个 AI 服务是否均走真实推理路径
"""
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from services import OCRService, DamageService, StackService

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'test')
os.makedirs(TEST_DIR, exist_ok=True)


def make_test_images():
    """生成测试图片"""
    # 破损/堆码测试图：普通集装箱
    img = Image.new('RGB', (224, 224), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 204, 204], fill=(180, 140, 90), outline=(80, 60, 40), width=3)
    for x in range(35, 200, 18):
        draw.line([(x, 25), (x, 199)], fill=(160, 120, 70), width=1)
    damage_path = os.path.join(TEST_DIR, 'test_container.png')
    img.save(damage_path)

    # OCR 测试图：带箱号文字
    ocr_img = Image.new('RGB', (400, 200), (240, 240, 240))
    draw = ImageDraw.Draw(ocr_img)
    draw.rectangle([10, 10, 390, 190], fill=(180, 140, 90), outline=(80, 60, 40), width=3)
    # 用默认字体写箱号
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((50, 70), "MSKU1234567", fill=(20, 20, 20), font=font)
    ocr_path = os.path.join(TEST_DIR, 'test_ocr.png')
    ocr_img.save(ocr_path)

    return damage_path, ocr_path


def main():
    print("=" * 60)
    print("AI 识别模块 - 真实推理验证")
    print("=" * 60)

    damage_path, ocr_path = make_test_images()
    print(f"\n测试图片已生成:")
    print(f"  破损/堆码测试: {damage_path}")
    print(f"  OCR 测试: {ocr_path}")

    # 1. OCR 服务
    print("\n" + "-" * 60)
    print("[1/3] OCR 服务 (箱号识别)")
    print("-" * 60)
    t0 = time.time()
    ocr = OCRService(Config)
    print(f"  初始化耗时: {time.time()-t0:.2f}s")
    print(f"  is_available: {ocr.is_available}")
    print(f"  engine_name: {ocr.engine_name}")
    if ocr.is_available:
        result = ocr.recognize(ocr_path)
        print(f"  识别结果: {result}")
        print(f"  状态: ✅ 真实推理 (RapidOCR ONNX)")
    else:
        print(f"  状态: ❌ 降级到 mock")

    # 2. 破损检测服务
    print("\n" + "-" * 60)
    print("[2/3] 破损检测服务 (ResNet50)")
    print("-" * 60)
    t0 = time.time()
    damage = DamageService(Config)
    print(f"  初始化耗时: {time.time()-t0:.2f}s")
    print(f"  is_available: {damage.is_available}")
    print(f"  device: {damage.device}")
    print(f"  num_classes: {damage.num_classes}")
    if damage.is_available:
        t0 = time.time()
        result = damage.detect(damage_path)
        print(f"  推理耗时: {time.time()-t0:.3f}s")
        print(f"  检测结果: {result.get('damage_result')}")
        print(f"  破损等级: {result.get('damage_level')}")
        print(f"  置信度: {result.get('confidence')}")
        print(f"  all_probs 数量: {len(result.get('all_probs', {}))}")
        print(f"  状态: ✅ 真实推理 (ResNet50 微调权重)")
    else:
        print(f"  状态: ❌ 降级到 mock")

    # 3. 堆码分类服务
    print("\n" + "-" * 60)
    print("[3/3] 堆码状态分类服务 (ViT-B/16)")
    print("-" * 60)
    t0 = time.time()
    stack = StackService(Config)
    print(f"  初始化耗时: {time.time()-t0:.2f}s")
    print(f"  is_available: {stack.is_available}")
    print(f"  device: {stack.device}")
    print(f"  num_classes: {stack.num_classes}")
    if stack.is_available:
        t0 = time.time()
        result = stack.classify(damage_path)
        print(f"  推理耗时: {time.time()-t0:.3f}s")
        print(f"  分类结果: {result.get('stack_result')}")
        print(f"  置信度: {result.get('confidence')}")
        print(f"  all_probs 数量: {len(result.get('all_probs', {}))}")
        print(f"  状态: ✅ 真实推理 (ViT-B/16 微调权重)")
    else:
        print(f"  状态: ❌ 降级到 mock")

    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    all_ok = ocr.is_available and damage.is_available and stack.is_available
    print(f"  OCR:      {'✅ 真实推理' if ocr.is_available else '❌ mock'}")
    print(f"  破损检测: {'✅ 真实推理' if damage.is_available else '❌ mock'}")
    print(f"  堆码分类: {'✅ 真实推理' if stack.is_available else '❌ mock'}")
    print(f"\n  权重文件:")
    print(f"    {Config.DAMAGE_WEIGHTS} ({os.path.getsize(Config.DAMAGE_WEIGHTS)//1024//1024} MB)")
    print(f"    {Config.STACK_WEIGHTS} ({os.path.getsize(Config.STACK_WEIGHTS)//1024//1024} MB)")
    print(f"\n  最终状态: {'✅ 全部走真实推理，mock 已彻底替换' if all_ok else '⚠️ 部分服务仍为 mock'}")


if __name__ == '__main__':
    main()
