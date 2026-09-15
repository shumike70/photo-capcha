from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
from PIL import Image, ImageDraw

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = str(query.get('text', ['3782'])[0])[:4]

        try:
            # কমপ্যাক্ট সাইবার সাইজ (360x120)
            width, height = 360, 120
            img = Image.new("RGBA", (width, height), (5, 10, 24, 255))
            draw = ImageDraw.Draw(img)

            # ১. ব্যাকগ্রাউন্ড সাইবার গ্রিড
            for gy in range(0, height, 15):
                draw.line([(0, gy), (width, gy)], fill=(12, 25, 55, 255), width=1)
            for gx in range(0, width, 24):
                draw.line([(gx, 0), (gx, height)], fill=(12, 25, 55, 255), width=1)

            # ২. লেজার স্ক্যানার লাইন (Cyber Laser Beam)
            draw.line([(0, 60), (width, 60)], fill=(0, 229, 255, 120), width=2)
            draw.line([(0, 61), (width, 61)], fill=(0, 229, 255, 40), width=4)

            # ৩. আউটার ৩D নিয়ন বর্ডার
            draw.rounded_rectangle([(3, 3), (width-4, height-4)], radius=12, outline=(0, 229, 255, 240), width=2)
            draw.rounded_rectangle([(6, 6), (width-7, height-7)], radius=10, outline=(0, 150, 220, 80), width=1)

            # ৪. ৭-সেগমেন্ট ৩D বড় সাইবার নাম্বার ড্রয়ার
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
                w, h = 34, 56  # অনেক বড় ও স্পষ্ট বোল্ড সাইজ
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

            # ৫. ৪টি ডিজিট একদম সেন্টারে ৩D গ্লো সহ আঁকা
            start_x = 72
            spacing = 58
            for idx, ch in enumerate(text):
                dx = start_x + (idx * spacing)
                dy = 32

                # পেছনের ডার্ক ৩D শ্যাডো
                draw_digit(draw, ch, dx+4, dy+4, (2, 5, 15, 255), 7)
                # ৩D নিয়ন গ্লো লেয়ার
                draw_digit(draw, ch, dx, dy, (0, 229, 255, 120), 8)
                # ৩D মেইন নিয়ন বডি
                draw_digit(draw, ch, dx, dy, (0, 229, 255, 255), 5)
                # সামনের উজ্জ্বল হোয়াইট কোর
                draw_digit(draw, ch, dx, dy, (245, 255, 255, 255), 2)

            # ৬. পিওর PNG আউটপুট পাঠানো (Content-Type: image/png)
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
