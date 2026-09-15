from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
import math
from PIL import Image, ImageDraw

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = str(query.get('text', ['3782'])[0])[:4]

        try:
            width, height = 360, 120
            frames = []
            total_frames = 8

            # ৭-সেগমেন্ট ডিজিটাল ৩D সাইবার নাম্বার ড্রয়ার
            segments = {
                '0': ['a', 'b', 'c', 'd', 'e', 'f'],
                '1': ['b', 'c'],
                '2': ['a', 'b', 'g', 'e', 'd'],
                '3': ['a', 'b', 'g', 'c', 'd'],
                '4': ['f', 'g', 'b', 'c'],
                '5': ['a', 'f', 'g', 'c', 'd'],
                '6': ['a', 'f', 'g', 'e', 'c', 'd'],
                '7': ['a', 'b', 'c'],
                '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
                '9': ['a', 'b', 'c', 'd', 'f', 'g']
            }

            def draw_digit(draw_obj, char, x, y, color, width_val):
                w, h = 32, 54  # বড় বোল্ড সাইজ
                hw = h // 2
                segs = segments.get(char, segments['0'])
                lines = {
                    'a': [(x+5, y), (x+w-5, y)],
                    'b': [(x+w, y+5), (x+w, y+hw-3)],
                    'c': [(x+w, y+hw+3), (x+w, y+h-5)],
                    'd': [(x+5, y+h), (x+w-5, y+h)],
                    'e': [(x, y+hw+3), (x, y+h-5)],
                    'f': [(x, y+5), (x, y+hw-3)],
                    'g': [(x+5, y+hw), (x+w-5, y+hw)]
                }
                for seg in segs:
                    draw_obj.line(lines[seg], fill=color, width=width_val)

            # --- অ্যানিমেশন ফ্রেম তৈরি ---
            for i in range(total_frames):
                frame = Image.new("RGBA", (width, height), (5, 10, 22, 255))
                draw = ImageDraw.Draw(frame)

                # ১. ব্যাকগ্রাউন্ড সাইবার গ্রিড
                for gy in range(0, height, 16):
                    draw.line([(0, gy), (width, gy)], fill=(12, 24, 50, 255), width=1)
                for gx in range(0, width, 24):
                    draw.line([(gx, 0), (gx, height)], fill=(12, 24, 50, 255), width=1)

                # ২. মুভিং লেজার স্ক্যানার অ্যানিমেশন (Moving Scanner)
                scan_y = int((i / total_frames) * height)
                draw.line([(0, scan_y), (width, scan_y)], fill=(0, 229, 255, 160), width=2)
                draw.line([(0, scan_y+1), (width, scan_y+1)], fill=(0, 229, 255, 60), width=4)

                # ৩. আউটার ৩D পালসিং নিয়ন বর্ডার
                pulse = int(180 + 75 * math.sin(i * math.pi / 4))
                draw.rounded_rectangle([(4, 4), (width-5, height-5)], radius=12, outline=(0, 229, 255, pulse), width=2)

                # ৪. ৪টি ডিজিট একদম সেন্টারে বড় করে আঁকা
                start_x = 75
                spacing = 56
                offset_glitch = int(math.sin(i * math.pi / 4) * 2)

                for idx, ch in enumerate(text):
                    dx = start_x + (idx * spacing) + offset_glitch
                    dy = 42

                    # ৩D ডেপথ ডার্ক শ্যাডো
                    draw_digit(draw, ch, dx+3, dy+3, (2, 8, 20, 255), 7)
                    # ৩D নিয়ন গ্লো লেয়ার
                    draw_digit(draw, ch, dx, dy, (0, 229, 255, 120), 8)
                    # ৩D মেইন নিয়ন লেয়ার
                    draw_digit(draw, ch, dx, dy, (0, 229, 255, 255), 5)
                    # সামনের ব্রাইট হোয়াইট হাইলাইট
                    draw_digit(draw, ch, dx, dy, (240, 255, 255, 255), 2)

                frames.append(frame.convert("P", palette=Image.ADAPTIVE))

            buffer = io.BytesIO()
            frames[0].save(
                buffer,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=90,
                loop=0
            )

            self.send_response(200)
            self.send_header('Content-Type', 'image/gif')
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
