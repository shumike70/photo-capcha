import io
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import requests


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get("text", ["4233"])[0]

        try:
            # ক্যাপচা বক্সের সাইজ
            width, height = 400, 140

            # ১. ব্যাকগ্রাউন্ড ক্যানভাস
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            # রাউন্ডেড স্লেট-পার্পল বক্স
            bg_box = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_box)
            bg_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=18, fill=(122, 134, 175, 255)
            )

            # ব্যাকগ্রাউন্ডে টেক্সচার / নয়েজ
            for _ in range(4500):
                nx = random.randint(0, width - 1)
                ny = random.randint(0, height - 1)
                noise_color = random.choice(
                    [
                        (102, 114, 155, 180),
                        (142, 154, 196, 180),
                        (112, 124, 165, 200),
                    ]
                )
                bg_draw.point((nx, ny), fill=noise_color)

            img.paste(bg_box, (0, 0), bg_box)

            # ২. ফন্ট লোড করা
            try:
                # ক্যাপচা নাম্বারের জন্য এক্সট্রা বোল্ড ও বড় ফন্ট (Size: 92)
                num_font_url = "https://github.com/google/fonts/raw/main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
                num_res = requests.get(num_font_url, timeout=5)
                font_num = ImageFont.truetype(io.BytesIO(num_res.content), 92)

                # ব্র্যান্ডিং টেক্সটের ফন্ট (Size: 15)
                brand_font_url = "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Bold.ttf"
                brand_res = requests.get(brand_font_url, timeout=5)
                font_brand = ImageFont.truetype(
                    io.BytesIO(brand_res.content), 15
                )
            except:
                font_num = ImageFont.load_default()
                font_brand = ImageFont.load_default()

            # ৩. উপরে "⚡ SN BOT CREATOR" ব্র্যান্ডিং টেক্সট
            draw = ImageDraw.Draw(img)
            brand_text = "⚡ SN BOT CREATOR"

            # ব্র্যান্ডিং টেক্সটের ড্রপ শ্যাডো ও কালার
            draw.text(
                (width // 2 + 1, 20),
                brand_text,
                fill=(45, 54, 82, 190),
                font=font_brand,
                anchor="mm",
            )
            draw.text(
                (width // 2, 19),
                brand_text,
                fill=(240, 245, 255, 240),
                font=font_brand,
                anchor="mm",
            )

            # ৪. বড় ৩D ক্যাপচা নাম্বারের পজিশন
            cx, cy = width // 2, (height // 2) + 16

            # ৩D ডার্ক শ্যাডো লেয়ার (Bold Deep Shadow)
            shadow_mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)
            for offset in [(5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
                shadow_draw.text(
                    (cx + offset[0], cy + offset[1]),
                    text,
                    fill=(42, 50, 78, 255),
                    font=font_num,
                    anchor="mm",
                )

            img.paste(shadow_mask, (0, 0), shadow_mask)

            # ৫. চক / স্কেচ হ্যাচড ইফেক্ট লেয়ার
            text_mask = Image.new("L", (width, height), 0)
            t_draw = ImageDraw.Draw(text_mask)
            t_draw.text((cx, cy), text, fill=255, font=font_num, anchor="mm")

            chalk_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            c_draw = ImageDraw.Draw(chalk_layer)

            # বেস লাইট শেইড
            c_draw.rectangle(
                [(0, 0), (width, height)], fill=(245, 248, 255, 120)
            )

            # চক স্কেচ ডায়াগনাল লাইন
            for i in range(-height * 2, width + height * 2, 4):
                c_draw.line(
                    [(i, 0), (i + height, height)],
                    fill=(255, 255, 255, 240),
                    width=2,
                )
                if i % 8 == 0:
                    c_draw.line(
                        [(i, 0), (i + height, height)],
                        fill=(220, 230, 255, 200),
                        width=3,
                    )

            # চারপাশের শার্প হোয়াইট আউটলাইন
            c_draw.text(
                (cx, cy),
                text,
                fill=None,
                outline=(255, 255, 255, 255),
                font=font_num,
                anchor="mm",
            )

            # মাস্ক অনুযায়ী পেস্ট
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
