from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['4351'])[0]

        try:
            width, height = 500, 200
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            # ১. প্রিমিয়াম সফট গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড তৈরি (Smooth Slate-Lavender)
            bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            bg_draw = ImageDraw.Draw(bg_gradient)
            
            # উপর থেকে নিচে সফট কালার ট্রানজিশন
            for y in range(height):
                r = int(140 - (y / height) * 25)
                g = int(152 - (y / height) * 28)
                b = int(195 - (y / height) * 32)
                bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

            # ব্যাকগ্রাউন্ডকে রাউন্ডেড শেপে কাটা
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=24, fill=255)
            img.paste(bg_gradient, (0, 0), mask)

            draw = ImageDraw.Draw(img)

            # ২. সফট ইনার গ্লাস বর্ডার এবং টপ হাইলাইট (Premium Glass/Card Feel)
            draw.rounded_rectangle([(1, 1), (width-2, height-2)], radius=24, outline=(255, 255, 255, 70), width=2)
            draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=24, outline=(70, 80, 115, 90), width=1)

            # ৩. ফন্ট লোড
            font_num = get_bold_font(112)
            font_brand = get_bold_font(18)

            cx, cy = width // 2, (height // 2) + 12

            # ৪. উপরে ব্র্যান্ডিং "⚡ SN BOT CREATOR"
            brand_text = "⚡ SN BOT CREATOR"
            draw.text((width // 2, 27), brand_text, fill=(50, 60, 90, 180), font=font_brand, anchor="mm")
            draw.text((width // 2, 25), brand_text, fill=(245, 248, 255, 240), font=font_brand, anchor="mm")

            # ৫. সফট ৩D ডিপ শ্যাডো (Depth Shadow)
            shadow_mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_mask)
            
            # ৩D শ্যাডো লেয়ার
            for offset in [(7, 7), (6, 6), (5, 5), (4, 4), (3, 3), (2, 2)]:
                shadow_draw.text((cx + offset[0], cy + offset[1]), text, fill=(45, 55, 84, 255), font=font_num, anchor="mm")
            
            img.paste(shadow_mask, (0, 0), shadow_mask)

            # ৬. চক / স্কেচ টেক্সচার লেয়ার
            text_mask = Image.new("L", (width, height), 0)
            t_draw = ImageDraw.Draw(text_mask)
            t_draw.text((cx, cy), text, fill=255, font=font_num, anchor="mm")

            chalk_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            c_draw = ImageDraw.Draw(chalk_layer)

            # চক স্কেচ ডায়াগনাল লাইনস
            c_draw.rectangle([(0, 0), (width, height)], fill=(255, 255, 255, 140))
            for i in range(-height * 2, width + height * 2, 4):
                c_draw.line([(i, 0), (i + height, height)], fill=(255, 255, 255, 240), width=2)
                if i % 8 == 0:
                    c_draw.line([(i, 0), (i + height, height)], fill=(225, 235, 255, 200), width=3)

            # চারপাশের শার্প হোয়াইট আউটলাইন
            c_draw.text((cx, cy), text, fill=None, outline=(255, 255, 255, 255), font=font_num, anchor="mm")

            # মাস্ক পেস্ট করা
            img.paste(chalk_layer, (0, 0), text_mask)

            # ৭. ইমেজ রিটার্ন
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", quality=100)
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
