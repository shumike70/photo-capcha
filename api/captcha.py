import io
import logging
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests

logger = logging.getLogger(__name__)

CACHED_FONT_DATA = None


def get_bold_font(size: int):
    """Fetches custom Google font with fallback."""
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                CACHED_FONT_DATA = res.content
        except Exception as err:
            logger.warning(f"Font download failed: {err}")

    if CACHED_FONT_DATA:
        return ImageFont.truetype(io.BytesIO(CACHED_FONT_DATA), size)
    return ImageFont.load_default()


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get("text", ["4351"])[0][:12]

        try:
            width, height = 500, 200

            # ১. ব্যাকগ্রাউন্ড ক্যানভাস (Gradient)
            bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_gradient)

            for y in range(height):
                ratio = y / height
                r = int(15 * (1 - ratio) + 28 * ratio)
                g = int(23 * (1 - ratio) + 16 * ratio)
                b = int(42 * (1 - ratio) + 65 * ratio)
                bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

            # ২. রাউন্ডেড মাস্ক
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=28, fill=255)

            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            img.paste(bg_gradient, (0, 0), mask)

            # ৩. গ্লাসফর্মিজম ইনসাইড বর্ডার
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [(1, 1), (width - 2, height - 2)],
                radius=28,
                outline=(255, 255, 255, 60),
                width=2,
            )
            img = Image.alpha_composite(img, overlay)

            draw = ImageDraw.Draw(img)

            # ৪. ফন্ট লোডিং
            font_num = get_bold_font(110)
            font_brand = get_bold_font(16)
            cx, cy = width // 2, (height // 2) + 12

            # ৫. ব্র্যান্ডিং টেক্সট (ইমোজি ছাড়া নিরাপদ স্ট্রাকচার)
            brand_text = "SN BOT CREATOR"
            draw.text((cx + 1, 27), brand_text, fill=(0, 0, 0, 180), font=font_brand, anchor="mm")
            draw.text((cx, 26), brand_text, fill=(255, 200, 80, 255), font=font_brand, anchor="mm")

            # ৬. নিয়ন গ্লো লেয়ার
            glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text((cx, cy + 2), text, fill=(0, 210, 255, 230), font=font_num, anchor="mm")
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=12))
            img = Image.alpha_composite(img, glow_layer)

            draw = ImageDraw.Draw(img)

            # ৭. ৩D শ্যাডো লেয়ার
            shadow_color = (10, 15, 30, 255)
            for d in range(8, 0, -1):
                draw.text((cx + d, cy + d), text, fill=shadow_color, font=font_num, anchor="mm")

            # ৮. মেইন ফ্রন্ট টেক্সট
            draw.text((cx, cy), text, fill=(255, 255, 255, 255), font=font_num, anchor="mm")

            # ৯. হাইলাইট লেয়ার
            highlight_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            highlight_draw = ImageDraw.Draw(highlight_layer)
            highlight_draw.text((cx, cy - 2), text, fill=(255, 255, 255, 120), font=font_num, anchor="mm")
            img = Image.alpha_composite(img, highlight_layer)

            # ১০. ইমেজ বাফার আউটপুট
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", optimize=True)
            image_data = buffer.getvalue()

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(image_data)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(image_data)

        except Exception as e:
            logger.error(f"Render Error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
