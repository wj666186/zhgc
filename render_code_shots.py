# -*- coding: utf-8 -*-
"""
Render Java source files into IDE-style code screenshots (dark theme, line numbers, syntax highlight).
"""
import os
from pygments import lex
from pygments.lexers import JavaLexer
from pygments.styles import get_style_by_name
from PIL import Image, ImageDraw, ImageFont

# ---------- config ----------
OUT_DIR = r"C:\Users\86186\Desktop\gangkou\code_screenshots"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_PATH = r"C:\Windows\Fonts\Deng.ttf"             # DengXian, supports Chinese
FONT_BOLD = r"C:\Windows\Fonts\Dengb.ttf"
FONT_SIZE = 18
LINE_HEIGHT = 26
PAD_X = 24
PAD_Y = 20
GUTTER_W = 60          # line-number column width
BG = (30, 30, 30)      # dark background
GUTTER_BG = (37, 37, 38)
FG = (212, 212, 212)   # default foreground

# maps pygments token types -> color
def token_color(ttype):
    # fall back up the token hierarchy
    while ttype is not None:
        name = str(ttype)
        # keyword (public, class, @Override, etc.)
        if 'Keyword' in name:           return (86, 156, 214)   # blue
        if 'String' in name:             return (206, 145, 120)  # orange/brown
        if 'Comment' in name:           return (106, 153, 85)   # green
        if 'Name.Decorator' in name:     return (220, 220, 170)  # yellow @Annotation
        if 'Name.Class' in name:         return (78, 201, 176)   # teal class names
        if 'Name.Function' in name:      return (220, 220, 170)  # yellow method
        if 'Literal.Number' in name:     return (181, 206, 168)  # light green numbers
        if 'Operator' in name:           return (212, 212, 212)
        ttype = ttype.parent
    return FG

def render_file(src_path, out_name, title=None):
    with open(src_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # lex -> list of (token, text)
    lexer = JavaLexer()
    tokens = list(lex(code, lexer))

    # split tokens into lines, preserving per-char color
    lines = [[]]      # lines[i] = list of (text, color)
    for ttype, text in tokens:
        color = token_color(ttype)
        for ch in text:
            if ch == '\n':
                lines.append([])
            else:
                lines[-1].append((ch, color))

    n_lines = len(lines)

    # measure width
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    font_bold = ImageFont.truetype(FONT_BOLD, FONT_SIZE)
    font_gutter = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # compute max content width
    max_w = 0
    for line in lines:
        w = 0
        for ch, _ in line:
            w += font.getlength(ch)
        max_w = max(max_w, w)

    title_h = 0
    if title:
        title_h = 36
        font_title = ImageFont.truetype(FONT_BOLD, 16)

    img_w = int(GUTTER_W + PAD_X * 2 + max_w + 20)
    img_h = int(title_h + PAD_Y * 2 + n_lines * LINE_HEIGHT)

    img = Image.new('RGB', (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)

    # gutter background
    draw.rectangle([0, 0, GUTTER_W, img_h], fill=GUTTER_BG)

    # title bar
    y = PAD_Y
    if title:
        draw.text((GUTTER_W + PAD_X, 8), title, fill((200, 200, 200)), font=ImageFont.truetype(FONT_BOLD, 16))
        y = title_h + PAD_Y

    # draw lines
    for i, line in enumerate(lines):
        line_no = str(i + 1)
        # line number (right aligned)
        draw.text((GUTTER_W - 10 - font_gutter.getlength(line_no), y),
                  line_no, fill((130, 130, 130)), font=font_gutter)

        # code
        x = GUTTER_W + PAD_X
        for ch, color in line:
            draw.text((x, y), ch, fill=color, font=font)
            x += font.getlength(ch)

        y += LINE_HEIGHT

    out_path = os.path.join(OUT_DIR, out_name)
    img.save(out_path)
    print(f"saved: {out_path}  ({img_w}x{img_h})")
    return out_path

def fill(t):
    return t

if __name__ == '__main__':
    base = r"C:\Users\86186\Desktop\gangkou\port-schedule-server\src\main\java\com\port"
    render_file(
        os.path.join(base, "websocket", "ContainerWebSocketServer.java"),
        "01_ContainerWebSocketServer.png",
        title="com.port.websocket.ContainerWebSocketServer.java"
    )
    render_file(
        os.path.join(base, "service", "impl", "ContainerServiceImpl.java"),
        "02_ContainerServiceImpl.png",
        title="com.port.service.impl.ContainerServiceImpl.java"
    )
    render_file(
        os.path.join(base, "controller", "ContainerTwinController.java"),
        "03_ContainerTwinController.png",
        title="com.port.controller.ContainerTwinController.java"
    )
    print("done.")
