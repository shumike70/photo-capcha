import io
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from PIL import Image, ImageDraw, ImageFont
import requests

CACHED_FONT_DATA = None


def get_bold_font(size):
    global CACHED_FONT_DATA
    if CACHED_FONT_DATA is None:
        try:
            # গুগল ফন্টস থেকে আলফা স্ল্যাব ওয়ান ফন্ট ডাউনলোড
            url = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf"
            res = requests.get(url, timeout=5)
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
        text = query.get("text", ["4351"])[0]

        try:
            width, height = 500, 200

            # ১. আল্ট্রা ডার্ক ওবিসিডিয়ান গ্র্যাডিয়েন্ট ব্যাকগ্রাউন্ড
            bg_gradient = Image.new("RGBA", (width, height), (0, 0, 0, 255))
            bg_draw = ImageDraw.Draw(bg_gradient)

            for y in range(height):
                ratio = y / height
                r = int(10 + ratio * 15)
                g = int(14 + ratio * 20)
                b = int(28 + ratio * 35)
                bg_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

            # রাউন্ডেড মাস্ক
            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (width, height)], radius=24, fill=255
            )

            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            img.paste(bg_gradient, (0, 0), mask)
            draw = ImageDraw.Draw(img)

            # সাইয়ান নিয়ন বর্ডার
            draw.rounded_rectangle(
                [(1, 1), (width - 2, height - 2)],
                radius=24,
                outline=(0, 210, 255, 180),
                width=2,
            )

            # ২. ফন্ট লোড
            font_num = get_bold_font(105)
            font_brand = get_bold_font(18)

            cx, cy = width // 2, (height // 2) + 12

            # ৩. ব্র্যান্ডিং টেক্সট (ইমোজি ছাড়া পরিষ্কার টেক্সট)
            brand_text = "SN BOT CREATOR"
            draw.text(
                (width // 2, 27),
                brand_text,
                fill=(0, 0, 0, 220),
                font=font_brand,
                anchor="mm",
            )
            draw.text(
                (width // 2, 25),
                brand_text,
                fill=(0, 225, 255, 255),
                font=font_brand,
                anchor="mm",
            )

            # ৪. ডার্ক স্ট্রোক (শার্পনেস বাড়াতে)
            stroke_radius = 3
            for dx in range(-stroke_radius, stroke_radius + 1):
                for dy in range(-stroke_radius, stroke_radius + 1):
                    if dx * dx + dy * dy <= stroke_radius * stroke_radius:
                        draw.text(
                            (cx + dx, cy + dy),
                            text,
                            fill=(5, 10, 20, 255),
                            font=font_num,
                            anchor="mm",
                        )

            # ৫. সলিড ৩D শ্যাডো
            shadow_color = (15, 25, 45, 255)
            for offset in [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]:
                draw.text(
                    (cx + offset[0], cy + offset[1]),
                    text,
                    fill=shadow_color,
                    font=font_num,
                    anchor="mm",
                )

            # ৬. সলিড ব্রাইট হোয়াইট ফ্রন্ট টেক্সট
            draw.text(
                (cx, cy),
                text,
                fill=(255, 255, 255, 255),
                font=font_num,
                anchor="mm",
            )

            # ৭. ইমেজ রেসপন্স
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="PNG", quality=100)

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
