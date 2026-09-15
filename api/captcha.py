import io
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests

# Configure logging for production tracing
logger = logging.getLogger(__name__)

# Cache variables
CACHED_FONT_DATA = None
CACHED_BASE_CANVAS = None  # Caches background gradient + glass border mask


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
    """Pre-renders static components (gradient canvas & rounded border)."""
    global CACHED_BASE_CANVAS
    if CACHED_BASE_CANVAS is not None:
        return CACHED_BASE_CANVAS.copy()

    # 1. Background Gradient Canvas
    bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_gradient)

    for y in range(height):
        ratio = y / height
        r = int(108 * (1 - ratio) + 85 * ratio)
        g = int(118 * (1 - ratio) + 98 * ratio)
        b = int(175 * (1 - ratio) + 152 * ratio)
        bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Rounded Mask
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=28, fill=255)

    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    base.paste(bg_gradient, (0, 0), mask)

    # 3. Inner Glass Edge Overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [(1, 1), (width - 2, height - 2)],
        radius=28,
        outline=(255, 255, 255, 80),
        width=2,
    )

    CACHED_BASE_CANVAS = Image.alpha_composite(base, overlay)
    return CACHED_BASE_CANVAS.copy()


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        # Input validation & length restriction to prevent canvas overflow/OOM
        text = query.get("text", ["4351"])[0][:12]

        try:
            width, height = 500, 200

            # 1. Reuse cached static base canvas
            img = get_base_canvas(width, height)
            draw = ImageDraw.Draw(img)

            # 2. Load Fonts
            font_num = get_bold_font(110)
            font_brand = get_bold_font(16)
            cx, cy = width // 2, (height // 2) + 14

            # 3. Branding Text
            brand_text = "⚡ SN BOT CREATOR"
            draw.text((cx, 28), brand_text, fill=(30, 38, 62, 160), font=font_brand, anchor="mm")
            draw.text((cx, 26), brand_text, fill=(240, 245, 255, 240), font=font_brand, anchor="mm")

            # 4. Neon Glow Layer
            glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text((cx, cy + 4), text, fill=(20, 25, 45, 180), font=font_num, anchor="mm")
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=12))
            img = Image.alpha_composite(img, glow_layer)

            draw = ImageDraw.Draw(img)

            # 5. 3D Extrusion Shadow
            shadow_color = (35, 42, 66, 255)
            for d in range(8, 0, -1):
                draw.text((cx + d, cy + d), text, fill=shadow_color, font=font_num, anchor="mm")

            # 6. Main Front Text Face
            draw.text((cx, cy), text, fill=(255, 255, 255, 255), font=font_num, anchor="mm")

            # 7. Top Highlight
            highlight_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            highlight_draw = ImageDraw.Draw(highlight_layer)
            highlight_draw.text((cx, cy - 1), text, fill=(255, 255, 255, 90), font=font_num, anchor="mm")
            img = Image.alpha_composite(img, highlight_layer)

            # 8. Output Stream Generation
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", optimize=True)
            image_data = buffer.getvalue()

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(image_data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(image_data)

        except Exception as e:
            logger.error(f"Error rendering image: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
