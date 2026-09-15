import io
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache variables
CACHED_FONT_DATA = None
CACHED_BASE_CANVAS = None


def get_bold_font(size: int):
    """Fetches and caches the custom font; falls back to default if unavailable."""
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                CACHED_FONT_DATA = res.content
        except Exception as err:
            logger.warning(f"Font download failed, using default: {err}")

    if CACHED_FONT_DATA:
        return ImageFont.truetype(io.BytesIO(CACHED_FONT_DATA), size)
    return ImageFont.load_default()


def get_base_canvas(width: int, height: int) -> Image.Image:
    """Pre-renders static components with enhanced dark vibrant gradient background."""
    global CACHED_BASE_CANVAS
    if CACHED_BASE_CANVAS is not None:
        return CACHED_BASE_CANVAS.copy()

    # 1. High-quality Deep Dark Gradient Canvas
    bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_gradient)

    # Modern dark neon palette (Deep Purple to Dark Midnight Blue)
    for y in range(height):
        ratio = y / height
        r = int(24 * (1 - ratio) + 12 * ratio)
        g = int(28 * (1 - ratio) + 16 * ratio)
        b = int(55 * (1 - ratio) + 38 * ratio)
        bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Smooth Rounded Mask with Antialiasing
    scale = 2  # Supersampling for ultra crisp smooth edges
    big_w, big_h = width * scale, height * scale
    mask_big = Image.new("L", (big_w, big_h), 0)
    mask_draw = ImageDraw.Draw(mask_big)
    mask_draw.rounded_rectangle([(0, 0), (big_w, big_h)], radius=28 * scale, fill=255)
    mask = mask_big.resize((width, height), Image.Resampling.LANCZOS)

    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base.paste(bg_gradient, (0, 0), mask)

    # 3. Inner Glass Edge Border Accent
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [(1, 1), (width - 2, height - 2)],
        radius=28,
        outline=(255, 255, 255, 60),
        width=2,
    )

    CACHED_BASE_CANVAS = Image.alpha_composite(base, overlay)
    return CACHED_BASE_CANVAS.copy()


def generate_optimized_image(text="4351"):
    width, height = 500, 200

    # Base Canvas
    img = get_base_canvas(width, height)
    draw = ImageDraw.Draw(img)

    # Load Fonts
    font_num = get_bold_font(110)
    font_brand = get_bold_font(16)
    cx, cy = width // 2, (height // 2) + 14

    # 1. Branding Text (Gold / Cyan Accent Color for high contrast)
    brand_text = "⚡ SN BOT CREATOR"
    draw.text((cx + 1, 27), brand_text, fill=(0, 0, 0, 180), font=font_brand, anchor="mm")
    draw.text((cx, 26), brand_text, fill=(255, 215, 0, 255), font=font_brand, anchor="mm") # Gold accent

    # 2. Cyber Cyan Glow Layer for Main Text
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text((cx, cy + 4), text, fill=(0, 229, 255, 220), font=font_num, anchor="mm")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=15))
    img = Image.alpha_composite(img, glow_layer)

    draw = ImageDraw.Draw(img)

    # 3. Enhanced Deep Multi-layer 3D Extrusion Shadow (Gradient Dark Blue to Magenta shadow)
    for d in range(9, 0, -1):
        color_r = int(20 + d * 2)
        color_g = int(10 + d * 3)
        color_b = int(40 + d * 15)
        draw.text((cx + d, cy + d), text, fill=(color_r, color_g, color_b, 255), font=font_num, anchor="mm")

    # 4. Main Front Text Face (Vibrant Gradient / Neon Cyan / Soft White Face)
    draw.text((cx, cy), text, fill=(240, 253, 255, 255), font=font_num, anchor="mm")

    # 5. Top Highlight (Bright White Specular Edge)
    highlight_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    highlight_draw = ImageDraw.Draw(highlight_layer)
    highlight_draw.text((cx, cy - 2), text, fill=(255, 255, 255, 140), font=font_num, anchor="mm")
    img = Image.alpha_composite(img, highlight_layer)

    # Save high quality sample image
    output_path = "output_preview.png"
    img.convert("RGB").save(output_path, format="PNG", optimize=True)
    print("Sample image generated successfully.")

generate_optimized_image("4351")
