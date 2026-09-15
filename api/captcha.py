from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
import requests
from PIL import Image, ImageDraw, ImageFont

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['4289'])[0]

        try:
            # 🎯 হুবহু নিচের রেফারেন্স সাইজ (Width: 360, Height: 120)
            width, height = 360, 120
            img = Image.new("RGBA", (width, height), (8, 14, 28, 255))
            draw = ImageDraw.Draw(img)

            # ১. ব্যাকগ্রাউন্ড সাইবার গ্রিড ও টেক্সচার (Cyber Lines)
            for y in range(0, height, 15):
                draw.line([(0, y), (width, y)], fill=(15, 28, 55, 255), width=1)
            for x in range(0, width, 25):
                draw.line([(x, 0), (x, height)], fill=(15, 28, 55, 255), width=1)

            # আউটার ৩D নিয়ন বর্ডার
            draw.rounded_rectangle([(3, 3), (width-4, height-4)], radius=14, outline=(0, 229, 255, 200), width=2)
            draw.rounded_rectangle([(6, 6), (width-7, height-7)], radius=12, outline=(0, 150, 200, 80), width=1)

            # ২. টপ ব্র্যান্ডিং ("⚡ SN BOT CREATOR")
            brand_text = "⚡ SN BOT CREATOR"
            try:
                # বোল্ড ফন্ট লোড (Google CDN থেকে সরাসরি লোড হবে, তাই কখনো ফন্ট মিসিং হবে না)
                font_url = "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Bold.ttf"
                font_res = requests.get(font_url, timeout=4)
                font_num = ImageFont.truetype(io.BytesIO(font_res.content), 56)
                font_brand = ImageFont.truetype(io.BytesIO(font_res.content), 12)
            except:
                font_num = ImageFont.load_default()
                font_brand = ImageFont.load_default()

            draw.text((width // 2, 20), brand_text, fill=(0, 229, 255, 200), font=font_brand, anchor="mm")

            # ৩. ৩D মাল্টি-লেয়ার গ্লোয়িং নাম্বার (3D Embossed Effect)
            spaced_text = "  ".join(list(text))
            cx, cy = width // 2, (height // 2) + 12

            # ৩D শ্যাডো লেয়ার (Bottom-Right Dark Shadow)
            for offset in [(4, 4), (3, 3), (2, 2)]:
                draw.text((cx + offset[0], cy + offset[1]), spaced_text, fill=(2, 6, 18, 255), font=font_num, anchor="mm")

            # ৩D নিয়ন ডেপথ গ্লো (Cyan Deep Layer)
            draw.text((cx + 1, cy + 1), spaced_text, fill=(0, 180, 220, 255), font=font_num, anchor="mm")

            # ৩D মেইন ব্রাইট হোয়াইট-সায়ান টেক্সট (Front Glowing Layer)
            draw.text((cx, cy), spaced_text, fill=(240, 255, 255, 255), font=font_num, anchor="mm")

            # ইমেজ এক্সপোর্ট
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
