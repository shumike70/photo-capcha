from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
import math
import requests
from PIL import Image, ImageDraw, ImageFont

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['4289'])[0]

        try:
            width, height = 360, 120
            
            # বোল্ড ফন্ট লোড
            try:
                font_url = "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono-Bold.ttf"
                font_res = requests.get(font_url, timeout=4)
                font_num = ImageFont.truetype(io.BytesIO(font_res.content), 54)
                font_brand = ImageFont.truetype(io.BytesIO(font_res.content), 12)
            except:
                font_num = ImageFont.load_default()
                font_brand = ImageFont.load_default()

            spaced_text = "  ".join(list(text))
            frames = []
            total_frames = 8  # স্মুথ অ্যানিমেশনের জন্য ৮টি ফ্রেম

            # --- অ্যানিমেশন ফ্রেম তৈরি ---
            for i in range(total_frames):
                frame = Image.new("RGBA", (width, height), (6, 12, 24, 255))
                draw = ImageDraw.Draw(frame)

                # ১. ব্যাকগ্রাউন্ড গ্রিড
                for y in range(0, height, 15):
                    draw.line([(0, y), (width, y)], fill=(12, 24, 48, 255), width=1)
                for x in range(0, width, 25):
                    draw.line([(x, 0), (x, height)], fill=(12, 24, 48, 255), width=1)

                # ২. মুভিং সাইবার লেজার স্ক্যানার লাইন (উপর থেকে নিচে নড়বে)
                scan_y = int((i / total_frames) * height)
                draw.line([(0, scan_y), (width, scan_y)], fill=(0, 229, 255, 180), width=2)
                draw.line([(0, scan_y+1), (width, scan_y+1)], fill=(0, 229, 255, 70), width=4)

                # ৩. আউটার পালসিং নিয়ন বর্ডার
                pulse_alpha = int(180 + 70 * math.sin(i * math.pi / 4))
                draw.rounded_rectangle([(3, 3), (width-4, height-4)], radius=14, outline=(0, 229, 255, pulse_alpha), width=2)

                # ৪. টপ ব্র্যান্ডিং
                draw.text((width // 2, 18), "⚡ SN BOT CREATOR", fill=(0, 229, 255, 220), font=font_brand, anchor="mm")

                # ৫. ৩D টেক্সট ভাইব্রেশন ও গ্লোয়িং মুভমেন্ট (Glitch Motion)
                offset_x = int(math.sin(i * math.pi / 4) * 2)
                cx, cy = (width // 2) + offset_x, (height // 2) + 12

                # পেছনের ডার্ক ৩D শ্যাডো
                draw.text((cx + 3, cy + 3), spaced_text, fill=(2, 6, 15, 255), font=font_num, anchor="mm")
                # মাঝের ব্লু গ্লো
                draw.text((cx + 1, cy + 1), spaced_text, fill=(0, 180, 220, 255), font=font_num, anchor="mm")
                # সামনের ব্রাইট হোয়াইট/সায়ান গ্লোয়িং টেক্সট
                draw.text((cx, cy), spaced_text, fill=(240, 255, 255, 255), font=font_num, anchor="mm")

                frames.append(frame.convert("P", palette=Image.ADAPTIVE))

            # জিআইএফ (GIF) আউটপুট
            buffer = io.BytesIO()
            frames[0].save(
                buffer,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=100,  # প্রতি ফ্রেমের স্পিড (১০০ মিলিসেকেন্ড)
                loop=0         # অনবরত লুপে নড়বে
            )

            self.send_response(200)
            self.send_header('Content-Type', 'image/gif')
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
