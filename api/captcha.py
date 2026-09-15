import io
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import requests

CACHED_FONT_DATA = None


def get_bold_font(size):
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            # গুগল ফন্টস থেকে হাই-কোয়ালিটি আলফা স্ল্যাব ওয়ান ফন্ট
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

            # ১. সফট স্লেট-ল্যাভেন্ডার ক্লিন ব্যাকগ্রাউন্ড
            bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_gradient)

            for y in range(height):
                r = int(136 - (y / height) * 22)
                g = int(148 - (y / height) * 25)
                b = int(192 - (y / height) * 28)
                bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

            # রাউন্ডেড শেপ মাস্ক
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=24, fill=255
            )

            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            img.paste(bg_gradient, (0, 0), mask)
            draw = ImageDraw.Draw(img)

            # সফট কার্ড বর্ডার
            draw.rounded_rectangle(
                [(1, 1), (width - 2, height - 2)],
                radius=24,
                outline=(255, 255, 255, 60),
                width=2,
            )

            # ২. ফন্ট লোড (বড় এবং বোল্ড)
            font_num = get_bold_font(114)
            font_brand = get_bold_font(18)

            cx, cy = width // 2, (height // 2) + 12

            # ৩. উপরে "⚡ SN BOT CREATOR"
            brand_text = "⚡ SN BOT CREATOR"
            draw.text(
                (width // 2, 27),
                brand_text,
                fill=(45, 54, 82, 180),
                font=font_brand,
                anchor="mm",
            )
            draw.text(
                (width // 2, 25),
                brand_text,
                fill=(245, 248, 255, 245),
                font=font_brand,
                anchor="mm",
            )

            # ৪. ডার্ক ৩D সলিড ডেপথ শ্যাডো (কোনো ঝাপসা ছাড়া একদম নিখুঁত থ্রিডি ড্রপ)
            shadow_color = (42, 50, 78, 255)
            for offset in [
                (6, 6),
                (5, 5),
                (4, 4),
                (3, 3),
                (2, 2),
                (1, 1),
                (0, 6),
                (6, 0),
            ]:
                draw.text(
                    (cx + offset[0], cy + offset[1]),
                    text,
                    fill=shadow_color,
                    font=font_num,
                    anchor="mm",
                )

            # ৫. টপ ফ্রন্ট লেয়ার: একদম সলিড, ব্রাইট ও শার্প হোয়াইট
            draw.text(
                (cx, cy),
                text,
                fill=(255, 255, 255, 255),
                font=font_num,
                anchor="mm",
            )

            # ৬. ইমেজ রিটার্ন
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", quality=100)

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
