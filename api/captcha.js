const { createCanvas, loadImage } = require('@napi-rs/canvas');
const path = require('path');

module.exports = async (req, res) => {
  const { text = '1234' } = req.query;

  try {
    // পাবলিক ফোল্ডার থেকে ব্যাকগ্রাউন্ড ছবি লোড করা
    const imagePath = path.join(process.cwd(), 'public', 'bg.jpg');
    const image = await loadImage(imagePath);

    // ক্যানভাস সাইজ নির্ধারণ
    const canvas = createCanvas(image.width, image.height);
    const ctx = canvas.getContext('2d');

    // ব্যাকগ্রাউন্ড ছবি ড্র করা
    ctx.drawImage(image, 0, 0);

    // ক্যাপচা টেক্সট ডিজাইন (Neon Blue + Glow Effect)
    ctx.font = 'bold 85px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // গ্লো ইফেক্ট
    ctx.shadowColor = '#00d4ff';
    ctx.shadowBlur = 20;
    ctx.fillStyle = '#00d4ff';

    // ক্যাপচা নম্বরটি ছবির মাঝখান থেকে একটু নিচে সুন্দরভাবে বসানো
    const x = canvas.width / 2;
    const y = canvas.height / 2 + 100;

    // টেক্সটের পেছনের হালকা ডার্ক বক্স (যাতে নম্বর স্পষ্ট পড়া যায়)
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
    ctx.shadowBlur = 0;
    ctx.roundRect(x - 160, y - 55, 320, 110, 20);
    ctx.fill();
    ctx.restore();

    // টেক্সট ড্র
    ctx.fillText(text, x, y);

    // ইমেজ রেসপন্স পাঠানো
    res.setHeader('Content-Type', 'image/jpeg');
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    res.status(200).send(canvas.toBuffer('image/jpeg'));
  } catch (error) {
    res.status(500).send('Error generating captcha: ' + error.message);
  }
};
