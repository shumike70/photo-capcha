import io
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests

CACHED_FONT_DATA = None


def get_bold_font(size):
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            # গুগল ফন্টস থেকে হাই-কোয়ালিটি আলফা স্ল্যাব ওয়ান ফন্ট
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                CACHED_FONT_DATA = res.content
        except Exception:
            pass
    if CACHED_FONT_DATA:
        return ImageFont.truetype(io.BytesIO(CACHED_FONT_DATA), size)
    return ImageFont.load_default()


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get("text", ["4351"])[0]

        try:
            width, height = 500, 200

            # ১. আল্ট্রা-স্মুথ ভাইব্রেন্ট ব্যাকগ্রাউন্ড ক্যানভাস
            bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_gradient)

            # মসৃণ ৩-রঙের কালার গ্র্যাডিয়েন্ট
            for y in range(height):
                ratio = y / height
                r = int(108 * (1 - ratio) + 85 * ratio)
                g = int(118 * (1 - ratio) + 98 * ratio)
                b = int(175 * (1 - ratio) + 152 * ratio)
                bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

            # রাউন্ডেড শেপ মাস্ক (অ্যা Anti-Aliasing এর জন্য বড় ক্যানভাস ধরে তৈরি)
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=28, fill=255
            )

            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            img.paste(bg_gradient, (0, 0), mask)

            # ২. গ্লাসফর্মিজম ইনার কার্ড বর্ডার (Inner Glass Edge)
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [(1, 1), (width - 2, height - 2)],
                radius=28,
                outline=(255, 255, 255, 80),
                width=2,
            )
            img = Image.alpha_composite(img, overlay)

            draw = ImageDraw.Draw(img)

            # ৩. ফন্ট লোড ও সাইজিং
            font_num = get_bold_font(110)
            font_brand = get_bold_font(16)

            cx, cy = width // 2, (height // 2) + 14

            # ৪. ব্র্যান্ডিং টেক্সট উইথ সফট শ্যাডো
            brand_text = "⚡ SN BOT CREATOR"
            draw.text(
                (width // 2, 28),
                brand_text,
                fill=(30, 38, 62, 160),
                font=font_brand,
                anchor="mm",
            )
            draw.text(
                (width // 2, 26),
                brand_text,
                fill=(240, 245, 255, 240),
                font=font_brand,
                anchor="mm",
            )

            # ৫. ব্যাকগ্রাউন্ড নিয়ন/সফ্ট গ্লো ইফেক্ট (Neon Glow Layer)
            glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text(
                (cx, cy + 4),
                text,
                fill=(20, 25, 45, 180),
                font=font_num,
                anchor="mm",
            )
            glow_layer = glow_layer.filter(
                ImageFilter.GaussianBlur(radius=12)
            )
            img = Image.alpha_composite(img, glow_layer)

            # পুনরায় ডাইনামিক ড্র অবজেক্ট নেওয়া
            draw = ImageDraw.Draw(img)

            # ৬. ডিープ ৩D এক্সট্রুশন শ্যাডো (Multi-layered 3D Depth)
            shadow_color = (35, 42, 66, 255)
            depth_steps = [
                (8, 8),
                (7, 7),
                (6, 6),
                (5, 5),
                (4, 4),
                (3, 3),
                (2, 2),
                (1, 1),
            ]
            for dx, dy in depth_steps:
                draw.text(
                    (cx + dx, cy + dy),
                    text,
                    fill=shadow_color,
                    font=font_num,
                    anchor="mm",
                )

            # ৭. মেইন ফ্রন্ট টেক্সট (Bright Sharp White Face)
            draw.text(
                (cx, cy),
                text,
                fill=(255, 255, 255, 255),
                font=font_num,
                anchor="mm",
            )

            # ৮. টপ শাইন হাইলাইট (Top-Lighting Accent Layer)
            highlight_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            highlight_draw = ImageDraw.Draw(highlight_layer)
            highlight_draw.text(
                (cx, cy - 1),
                text,
                fill=(255, 255, 255, 90),
                font=font_num,
                anchor="mm",
            )
            img = Image.alpha_composite(img, highlight_layer)

            # ৯. হাই-কোয়ালিটি ইমেজ রিটার্ন
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", quality=100)

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header(
                "Cache-Control", "public, max-age=86400"
            )  # পারফরম্যান্সের জন্য ক্যাশিং
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
