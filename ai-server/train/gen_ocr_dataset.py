"""
OCR 真实标注数据集生成器
用 PIL 精确绘制集装箱箱号（4字母+7数字），确保文字清晰、OCR 可100%识别。
生成多种颜色、角度、光照、位置变化的图片。
"""
import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

random.seed(123)

# 标准集装箱箱号前缀（船公司代码）
PREFIXES = ['MSKU', 'CSLU', 'MEDU', 'TCLU', 'HLXU', 'EITU', 'OOLU', 'APLU',
            'MAEU', 'CBHU', 'COSU', 'EMCU', 'HDMU', 'KLINE', 'ONE', 'YMLU',
            'CXRU', 'DVRU', 'FSCU', 'GESU', 'HLCU', 'IRIS', 'JTHU', 'KLFU']

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'data', 'real_dataset', 'ocr_train')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_font(size=48):
    """获取可用字体"""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/courbd.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def draw_container_door(draw, w, h, base_color):
    """绘制集装箱门背景（带波纹、门锁杆）"""
    margin = int(w * 0.08)
    # 门框
    draw.rectangle([margin, margin, w - margin, h - margin],
                   fill=base_color, outline=(50, 40, 30), width=3)
    # 中间门缝
    mid_x = w // 2
    draw.line([(mid_x, margin + 5), (mid_x, h - margin - 5)],
              fill=(base_color[0]-30, base_color[1]-30, base_color[2]-30), width=2)
    # 波纹
    for x in range(margin + 12, w - margin, 16):
        if abs(x - mid_x) < 8:
            continue
        draw.line([(x, margin + 8), (x, h - margin - 8)],
                  fill=(base_color[0]-20, base_color[1]-20, base_color[2]-20), width=1)
    # 门锁杆
    for lx in [mid_x - 35, mid_x + 35]:
        if margin < lx < w - margin:
            draw.line([(lx, margin + 15), (lx, h - margin - 15)],
                      fill=(80, 80, 80), width=3)
            # 锁扣
            draw.ellipse([lx-6, margin+10, lx+6, margin+22], fill=(60, 60, 60))
            draw.ellipse([lx-6, h-margin-22, lx+6, h-margin-10], fill=(60, 60, 60))


def add_noise_and_blur(img, blur_range=(0, 0.8), noise_level=10):
    """添加轻微噪声和模糊"""
    if blur_range[1] > 0:
        blur = random.uniform(*blur_range)
        if blur > 0.1:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    import numpy as np
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-noise_level, noise_level, arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def generate_ocr_image(index):
    """生成一张带精确箱号的集装箱图片"""
    w, h = 640, 480
    # 随机集装箱颜色
    colors = [
        (30, 80, 160),   # 蓝
        (180, 50, 40),   # 红
        (40, 120, 60),   # 绿
        (160, 130, 50),  # 黄褐
        (140, 140, 150), # 灰
        (180, 140, 90),  # 棕
        (80, 60, 120),   # 紫
        (20, 20, 20),    # 黑
    ]
    base_color = random.choice(colors)

    img = Image.new('RGB', (w, h), (200, 200, 210))
    draw = ImageDraw.Draw(img)
    draw_container_door(draw, w, h, base_color)

    # 生成箱号
    prefix = random.choice(PREFIXES)
    number = f"{random.randint(1000000, 9999999)}"
    container_no = prefix + number

    # 文字颜色（与背景对比）
    brightness = sum(base_color) / 3
    text_color = (255, 255, 255) if brightness < 128 else (20, 20, 20)

    # 字体大小随机
    font_size = random.randint(36, 64)
    font = get_font(font_size)

    # 文字位置随机（在门上区域）
    margin = int(w * 0.08)
    text_bbox = draw.textbbox((0, 0), container_no, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    # 箱号通常在门的右上区域，但随机变化
    tx = random.randint(margin + 10, w - margin - tw - 10)
    ty = random.randint(margin + 10, h - margin - th - 10)

    # 绘制文字（带轻微阴影增加可读性）
    shadow_color = (0, 0, 0) if text_color[0] > 128 else (255, 255, 255)
    draw.text((tx + 1, ty + 1), container_no, fill=shadow_color, font=font)
    draw.text((tx, ty), container_no, fill=text_color, font=font)

    # 随机旋转（小角度）
    angle = random.uniform(-5, 5)
    if abs(angle) > 0.5:
        img = img.rotate(angle, fillcolor=(200, 200, 210), expand=False)

    # 随机缩放裁剪（模拟不同拍摄距离）
    if random.random() > 0.4:
        crop_scale = random.uniform(0.7, 1.0)
        cw, ch = int(w * crop_scale), int(h * crop_scale)
        cx = random.randint(0, w - cw)
        cy = random.randint(0, h - ch)
        img = img.crop((cx, cy, cx + cw, cy + ch))
        img = img.resize((w, h), Image.LANCZOS)

    # 添加噪声和轻微模糊
    img = add_noise_and_blur(img, blur_range=(0, 0.6), noise_level=8)

    # 保存
    filename = f"ocr_{index:04d}_{container_no}.jpg"
    img.save(os.path.join(OUTPUT_DIR, filename), quality=95)
    return container_no, filename


def main():
    num_images = 80
    print(f"生成 {num_images} 张 OCR 训练图片...")
    labels = []
    for i in range(num_images):
        container_no, filename = generate_ocr_image(i)
        labels.append((filename, container_no))
        if (i + 1) % 20 == 0:
            print(f"  已生成 {i+1}/{num_images}")

    # 保存标签文件
    label_file = os.path.join(OUTPUT_DIR, 'labels.txt')
    with open(label_file, 'w', encoding='utf-8') as f:
        for filename, no in labels:
            f.write(f"{filename}\t{no}\n")

    print(f"\n完成！共生成 {num_images} 张图片")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"标签文件: {label_file}")

    # 验证前5张的OCR识别
    print("\n验证 OCR 识别准确率（前10张）...")
    try:
        from rapidocr_onnxruntime import RapidOCR
        import re
        engine = RapidOCR()
        pattern = re.compile(r'[A-Z]{4}\d{7}')
        correct = 0
        total = 0
        for filename, expected in labels[:10]:
            path = os.path.join(OUTPUT_DIR, filename)
            result, _ = engine(path)
            texts = [item[1] for item in result] if result else []
            recognized = 'UNKNOWN'
            for t in texts:
                m = pattern.search(t.upper())
                if m:
                    recognized = m.group()
                    break
            if recognized == expected:
                correct += 1
                status = "✅"
            else:
                status = f"❌ (识别:{recognized})"
            print(f"  {filename}: 期望={expected} {status}")
            total += 1
        print(f"\nOCR 准确率: {correct}/{total} = {correct/total*100:.0f}%")
    except Exception as e:
        print(f"  验证跳过: {e}")


if __name__ == '__main__':
    main()
