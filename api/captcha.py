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
            # ক্যাপচা সাইজ
            width, height = 380, 130

            # ১. ব্যাকগ্রাউন্ড ক্যানভাস তৈরি
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            # রাউন্ডেড স্লেট-পার্পল বক্স
            bg_box = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_box)
            bg_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=16, fill=(122, 134, 175, 255)
            )

            # ব্যাকগ্রাউন্ডে টেক্সচার / গ্রেইন নয়েজ যোগ করা
            for _ in range(4000):
                nx = random.randint(0, width - 1)
                ny = random.randint(0, height - 1)
                noise_color = random.choice(
                    [
                        (102, 114, 155, 180),
                        (140, 152, 195, 180),
                        (112, 124, 165, 200),
                    ]
                )
                bg_draw.point((nx, ny), fill=noise_color)

            img.paste(bg_box, (0, 0), bg_box)

            # ২. বোল্ড স্ল্যাব ফন্ট লোড (Google Fonts থেকে সরাসরি লোড)
            try:
                font_url = "https://github.com/google/fonts/raw/main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
                font_res = requests.get(font_url, timeout=5)
                font_num = ImageFont.truetype(io.BytesIO(font_res.content), 76)
            except:
                font_num = ImageFont.load_default()

            cx, cy = width // 2, (height // 2) - 3

            # ৩. ডার্ক ৩D শ্যাডো (Dark Depth Shadow)
            shadow_mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)
            for offset in [(4, 4), (3, 3), (2, 2), (1, 2)]:
                shadow_draw.text(
                    (cx + offset[0], cy + offset[1]),
                    text,
                    fill=(45, 54, 82, 255),
                    font=font_num,
                    anchor="mm",
                )

            img.paste(shadow_mask, (0, 0), shadow_mask)

            # ৪. চক / স্কেচ হ্যাচড টেক্সট মাস্ক (Chalk/Hatched Effect)
            text_mask = Image.new("L", (width, height), 0)
            t_draw = ImageDraw.Draw(text_mask)
            t_draw.text((cx, cy), text, fill=255, font=font_num, anchor="mm")

            # টেক্সটের ভেতরে ডায়াগনাল চক স্কেচ লাইন তৈরি
            chalk_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            c_draw = ImageDraw.Draw(chalk_layer)

            # বেস লাইট শেইড
            c_draw.rectangle(
                [(0, 0), (width, height)], fill=(240, 245, 255, 100)
            )

            # ডায়াগনাল লাইনস (Sketch Hatching)
            for i in range(-height, width + height, 3):
                c_draw.line(
                    [(i, 0), (i + height, height)],
                    fill=(255, 255, 255, 230),
                    width=1,
                )
                if i % 6 == 0:
                    c_draw.line(
                        [(i, 0), (i + height, height)],
                        fill=(220, 230, 255, 180),
                        width=2,
                    )

            # টেক্সটের বর্ডার ও শেপ স্পষ্ট করার জন্য আউটলাইন
            c_draw.text(
                (cx, cy),
                text,
                fill=None,
                outline=(255, 255, 255, 220),
                font=font_num,
                anchor="mm",
            )

            # মাস্ক অনুযায়ী টেক্সট পেস্ট করা
            img.paste(chalk_layer, (0, 0), text_mask)

            # ৫. ইমেজ রিটার্ন
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
