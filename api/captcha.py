import io
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests

CACHED_FONT_DATA = None

def get_bold_font(size):
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                CACHED_FONT_DATA = res.content
        except Exception:
            pass
    if CACHED_FONT_DATA:
        return ImageFont.truetype(io.BytesIO(CACHED_FONT_DATA), size)
    return ImageFont.load_default()

def render_image(text="4351"):
    # High resolution rendering scale for ultra clarity (2x supersampling)
    scale = 2
    width, height = 500 * scale, 200 * scale

    # Create base ultra modern dark gradient canvas
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Ultra Background: Deep Midnight Obsidian/Neon-Cyan Gradient
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    bg_draw = ImageDraw.Draw(bg)

    for y in range(height):
        ratio = y / height
        # Modern Ultra Dark Mesh Gradient (Rich Deep Navy/Indigo to Dark Purple)
        r = int(12 + ratio * 18)
        g = int(15 + ratio * 15)
        b = int(35 + ratio * 45)
        bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Mask for rounded card
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=32 * scale, fill=255)

    img.paste(bg, (0, 0), mask)
    draw = ImageDraw.Draw(img)

    # Ultra Cyber Glow Accents on background corners
    glow_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_bg)
    glow_draw.ellipse([(-50*scale, -50*scale), (180*scale, 180*scale)], fill=(0, 220, 255, 60))
    glow_draw.ellipse([(width - 180*scale, height - 180*scale), (width + 50*scale, height + 50*scale)], fill=(140, 0, 255, 60))
    glow_bg = glow_bg.filter(ImageFilter.GaussianBlur(radius=30 * scale))
    img = Image.alpha_composite(img, glow_bg)
    draw = ImageDraw.Draw(img)

    # Glassmorphism Crisp Border
    draw.rounded_rectangle(
        [(2 * scale, 2 * scale), (width - 2 * scale, height - 2 * scale)],
        radius=32 * scale,
        outline=(0, 220, 255, 120),
        width=3 * scale,
    )

    # Fonts
    font_num = get_bold_font(110 * scale)
    font_brand = get_bold_font(16 * scale)

    cx, cy = width // 2, (height // 2) + 14 * scale

    # Branding text with high contrast sharp outline
    brand_text = "⚡ SN BOT CREATOR"
    # Sharp Shadow
    draw.text((width // 2, 28 * scale + 2 * scale), brand_text, fill=(0, 0, 0, 230), font=font_brand, anchor="mm")
    # Crisp Neon White Brand
    draw.text((width // 2, 28 * scale), brand_text, fill=(0, 240, 255, 255), font=font_brand, anchor="mm")

    # Ultra Sharp 3D Shadow (Crisp Solid Blocks - No Blur)
    # High contrast solid black/dark cyan drop shadow for max readability
    for dx, dy in [(10, 10), (9, 9), (8, 8), (7, 7), (6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
        draw.text(
            (cx + dx * scale, cy + dy * scale),
            text,
            fill=(5, 10, 25, 255),
            font=font_num,
            anchor="mm",
        )

    # Thick Crisp Dark Stroke around text for Ultra Sharpness
    stroke_w = 4 * scale
    for sx in range(-stroke_w, stroke_w + 1):
        for sy in range(-stroke_w, stroke_w + 1):
            if sx*sx + sy*sy <= stroke_w*stroke_w:
                draw.text((cx + sx, cy + sy), text, fill=(10, 15, 30, 255), font=font_num, anchor="mm")

    # Pure Solid Ultra White Front Face
    draw.text((cx, cy), text, fill=(255, 255, 255, 255), font=font_num, anchor="mm")

    # Downscale smoothly to final target resolution for Retina Crisp anti-aliasing
    final_img = img.resize((500, 200), resample=Image.LANCZOS)
    
    final_img.convert("RGB").save("preview_ultra_clear.png", "PNG", quality=100)

render_image()
