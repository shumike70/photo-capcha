from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
import requests
from PIL import Image, ImageDraw, ImageFont

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URL থেকে টেক্সট নেওয়া
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['1234'])[0]

        try:
            # আপনার লোগো ব্যাকগ্রাউন্ড
            bg_url = "https://i.ibb.co.com/Mxpk7wwc/image.png"
            res = requests.get(bg_url, timeout=5)
            img = Image.open(io.BytesIO(res.content)).convert("RGB")
            img = img.resize((450, 250))

            draw = ImageDraw.Draw(img)
            
            # মাঝখানে নিয়ন সায়ান বক্স ও টেক্সট
            draw.rounded_rectangle([(120, 80), (330, 170)], radius=12, fill=(0, 0, 0, 210), outline=(0, 229, 255), width=3)
            
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()

            draw.text((225, 125), text, fill=(0, 229, 255), font=font, anchor="mm")

            # ছবি আউটপুট
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
