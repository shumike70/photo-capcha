import io
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import requests

# ক্যাশিং যাতে প্রতিবার রিকোয়েস্টে ফন্ট ডাউনলোড করতে সময় না নেয়
CACHED_FONT_DATA = None


def get_bold_font(size):
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            # নির্ভরযোগ্য হাই-স্পিড CDN
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                CACHED_FONT_DATA = res.content
        except Exception:
            pass

    if CACHED_FONT_DATA:
        return ImageFont.truetype(io.BytesIO(CACHED_FONT_DATA), size)

    # ব্যাকআপ ফন্ট
    return ImageFont.load_default()


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get("text", ["4351"])[0]

        try:
            # ক্যাপচা ফ্রেম সাইজ (রেফারেন্স রেশিও)
            width, height = 500, 200

            # ১. স্লেট-পার্পল ব্যাকগ্রাউন্ড তৈরি
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(img)

            # রাউন্ডেড বক্স
            bg_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=24, fill=(132, 146, 192, 255)
            )

            # ব্যাকগ্রাউন্ডের টেক্সচার / ফাইন নয়েজ
            for _ in range(7000):
                nx = random.randint(0, width - 1)
                ny = random.randint(0, height - 1)
                n_color = random.choice(
                    [
                        (108, 122, 168, 160),
                        (156, 170, 218, 160),
                        (120, 134, 180, 180),
                    ]
                )
                bg_draw.point((nx, ny), fill=n_color)

            # ২. ফন্ট সাইজ একদম বড় (Size: 110)
            font_num = get_bold_font(110)
            font_brand = get_bold_font(18)

            cx, cy = width // 2, (height // 2) + 12

            # ৩. উপরে ব্র্যান্ডিং "⚡ SN BOT CREATOR"
            brand_text = "⚡ SN BOT CREATOR"
            # ব্র্যান্ডিং শ্যাডো + টেক্সট
            bg_draw.text(
                (width // 2 + 1, 26),
                brand_text,
                fill=(45, 54, 82, 160),
                font=font_brand,
                anchor="mm",
            )
            bg_draw.text(
                (width // 2, 25),
                brand_text,
                fill=(245, 248, 255, 230),
                font=font_brand,
                anchor="mm",
            )

            # ৪. বড় ৩D ডার্ক শ্যাডো (Dark Depth Shadow)
            shadow_mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)

            for offset in [(7, 7), (6, 6), (5, 5), (4, 4), (3, 3), (2, 2)]:
                shadow_draw.text(
                    (cx + offset[0], cy + offset[1]),
                    text,
                    fill=(45, 55, 84, 255),
                    font=font_num,
                    anchor="mm",
                )

            img.paste(shadow_mask, (0, 0), shadow_mask)

            # ৫. চক / হ্যাচড স্কেচ লেয়ার (White Chalk Effect)
            text_mask = Image.new("L", (width, height), 0)
            t_draw = ImageDraw.Draw(text_mask)
            t_draw.text((cx, cy), text, fill=255, font=font_num, anchor="mm")

            chalk_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            c_draw = ImageDraw.Draw(chalk_layer)

            # হালকা হোয়াইট বেস
            c_draw.rectangle(
                [(0, 0), (width, height)], fill=(255, 255, 255, 140)
            )

            # ডায়াগনাল চক স্কেচ লাইন
            for i in range(-height * 2, width + height * 2, 4):
                c_draw.line(
                    [(i, 0), (i + height, height)],
                    fill=(255, 255, 255, 245),
                    width=2,
                )
                if i % 8 == 0:
                    c_draw.line(
                        [(i, 0), (i + height, height)],
                        fill=(225, 235, 255, 200),
                        width=3,
                    )

            # টেক্সটের চারপাশে শার্প হোয়াইট স্ট্রোক/বর্ডার
            c_draw.text(
                (cx, cy),
                text,
                fill=None,
                outline=(255, 255, 255, 255),
                font=font_num,
                anchor="mm",
            )

            # মাস্ক অনুযায়ী ব্লেন্ড করা
            img.paste(chalk_layer, (0, 0), text_mask)

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
