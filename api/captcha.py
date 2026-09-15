from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
import requests
from PIL import Image, ImageDraw, ImageFont

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['1234'])[0]

        try:
            # আসল লোগো ইমেজ
            bg_url = "https://i.ibb.co.com/Mxpk7wwc/image.png"
            res = requests.get(bg_url, timeout=5)
            img = Image.open(io.BytesIO(res.content)).convert("RGBA")
            
            # ১:১ অরিজিনাল স্কয়ার সাইজ (400x400) - ছবি একটুও কাটবে না
            img = img.resize((400, 400), Image.Resampling.LANCZOS)

            # ৩D ইফেক্ট লেয়ার
            overlay = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # ৩D সাইবার গ্লাস বক্স
            box = [(50, 165), (350, 245)]
            # ডার্ক গ্লাস ব্যাকগ্রাউন্ড
            draw.rounded_rectangle(box, radius=14, fill=(5, 12, 25, 230))
            # বাইরের নিয়ন গ্লো বর্ডার
            draw.rounded_rectangle([(48, 163), (352, 247)], radius=16, outline=(0, 229, 255, 100), width=2)
            # মেইন নিয়ন বর্ডার
            draw.rounded_rectangle(box, radius=14, outline=(0, 229, 255, 255), width=3)

            try:
                font = ImageFont.truetype("arial.ttf", 55)
            except:
                font = ImageFont.load_default()

            # ডিজিটগুলোর মাঝে সুন্দর স্পেসিং
            spaced_text = "  ".join(list(text))

            # 3D Depth Shadow (পেছনের ডার্ক নিয়ন শ্যাডো)
            draw.text((202, 207), spaced_text, fill=(0, 100, 140, 255), font=font, anchor="mm")
            # 3D Main Glowing Text (সামনের ব্রাইট নিয়ন টেক্সট)
            draw.text((200, 205), spaced_text, fill=(0, 245, 255, 255), font=font, anchor="mm")

            # লেয়ার একসাথে জোড়া লাগানো
            final_img = Image.alpha_composite(img, overlay).convert("RGB")

            buffer = io.BytesIO()
            final_img.save(buffer, format="PNG", quality=100)
            
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
