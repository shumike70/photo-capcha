from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import io
from PIL import Image, ImageDraw, ImageFont

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        text = query.get('text', ['1234'])[0]

        try:
            # Full HD ক্যানভাস (500x500) - পিওর ব্ল্যাক ব্যাকগ্রাউন্ড
            width, height = 500, 500
            img = Image.new("RGBA", (width, height), (3, 7, 18, 255))
            draw = ImageDraw.Draw(img)

            # কালার প্যালেট (Electric Neon Cyan)
            CYAN = (0, 229, 255, 255)
            CYAN_GLOW = (0, 229, 255, 60)
            DARK_BG = (8, 16, 32, 230)

            # --- ১. রোবট অ্যান্টেনা (Antenna) ---
            draw.line([(250, 45), (250, 80)], fill=CYAN, width=4)
            draw.ellipse([(238, 25), (262, 49)], outline=CYAN, width=4)
            draw.ellipse([(244, 31), (256, 43)], fill=CYAN)

            # --- ২. রোবটের দুই পাশের সার্কিট (Side Circuits) ---
            # Left Circuits
            draw.line([(130, 130), (85, 115)], fill=CYAN, width=3)
            draw.ellipse([(73, 105), (87, 119)], fill=CYAN)
            draw.line([(130, 175), (80, 175)], fill=CYAN, width=3)
            draw.ellipse([(68, 167), (82, 181)], fill=CYAN)
            draw.line([(130, 220), (85, 235)], fill=CYAN, width=3)
            draw.ellipse([(73, 231), (87, 245)], fill=CYAN)

            # Right Circuits
            draw.line([(370, 130), (415, 115)], fill=CYAN, width=3)
            draw.ellipse([(413, 105), (427, 119)], fill=CYAN)
            draw.line([(370, 175), (420, 175)], fill=CYAN, width=3)
            draw.ellipse([(418, 167), (432, 181)], fill=CYAN)
            draw.line([(370, 220), (415, 235)], fill=CYAN, width=3)
            draw.ellipse([(413, 231), (427, 245)], fill=CYAN)

            # --- ৩. রোবট হেড বডি (Robot Head Outline) ---
            head_box = [(130, 80), (370, 270)]
            # আউটার নিয়ন গ্লো
            draw.rounded_rectangle([(126, 76), (374, 274)], radius=32, outline=CYAN_GLOW, width=4)
            draw.rounded_rectangle(head_box, radius=30, outline=CYAN, width=5)

            # নিচে স্পিচ ট্রায়াঙ্গেল (Logo Tail)
            draw.polygon([(190, 270), (220, 305), (245, 270)], outline=CYAN)
            draw.line([(190, 270), (220, 305), (245, 270)], fill=CYAN, width=4)

            # --- ৪. মাঝখানে 3D Cyber HUD স্ক্রিন (ক্যাপচার জন্য) ---
            hud_box = [(150, 130), (350, 235)]
            # ৩D ব্যাকড্রপ
            draw.rounded_rectangle(hud_box, radius=16, fill=DARK_BG)
            draw.rounded_rectangle([(147, 127), (353, 238)], radius=18, outline=CYAN_GLOW, width=3)
            draw.rounded_rectangle(hud_box, radius=16, outline=CYAN, width=3)

            # ফন্ট লোড
            try:
                font_captcha = ImageFont.truetype("arial.ttf", 52)
                font_logo = ImageFont.truetype("arial.ttf", 36)
                font_sub = ImageFont.truetype("arial.ttf", 22)
            except:
                font_captcha = ImageFont.load_default()
                font_logo = ImageFont.load_default()
                font_sub = ImageFont.load_default()

            # --- ৫. 3D Glowing Captcha টেক্সট ---
            spaced_text = "  ".join(list(text))
            # 3D Shadow Depth (পেছনে ডার্ক শ্যাডো)
            draw.text((253, 185), spaced_text, fill=(0, 90, 140, 255), font=font_captcha, anchor="mm")
            # 3D Main Glow (সামনে নিয়ন টেক্সট)
            draw.text((250, 182), spaced_text, fill=(0, 245, 255, 255), font=font_captcha, anchor="mm")

            # --- ৬. নিচের ব্র্যান্ডিং নাম ("SN BOT CREATOR") ---
            # "SN BOT" - বোল্ড নিয়ন
            draw.text((252, 357), "SN BOT", fill=(0, 100, 150, 255), font=font_logo, anchor="mm")
            draw.text((250, 355), "SN BOT", fill=CYAN, font=font_logo, anchor="mm")
            
            # "CREATOR" - সাব-হেডিং
            draw.text((250, 400), "C R E A T O R", fill=(180, 230, 255, 255), font=font_sub, anchor="mm")

            # ইমেজ আউটপুট পাঠানো
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
