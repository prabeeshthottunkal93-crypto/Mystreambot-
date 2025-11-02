from flask import Flask, request, jsonify, render_template_string
import os
import time
import threading

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_AGE_DAYS = 3  # Auto-delete files after 3 days

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎬 {{ title or "Stream Video" }}</title>
<style>
body {
    background: #0f0f0f;
    color: #fff;
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
}
header {
    width: 100%;
    background: #1a1a1a;
    padding: 12px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 2px solid #ff0000;
}
header img { height: 40px; margin-right: 10px; }
header h1 { font-size: 22px; color: #ff3d3d; margin: 0; }
.container { width: 90%; max-width: 900px; margin-top: 20px; }
video { width: 100%; border-radius: 10px; background: #000; }
.ad { width: 100%; margin-top: 20px; text-align: center; }
.footer { margin-top: 30px; font-size: 14px; color: #888; }
.footer a { color: #ff3d3d; text-decoration: none; }
</style>
</head>
<body>

<header>
  <img src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png" alt="Logo">
  <h1>MyStream</h1>
</header>

<div class="container">
  <video controls poster="https://i.ibb.co/g43Mj8n/video-thumbnail.jpg">
    <source src="{{ video_url }}" type="video/mp4">
    Your browser does not support HTML5 video.
  </video>

  <div class="ad">
    <iframe src="https://your-ad-network.com/ad-banner"
            width="728" height="90"></iframe>
  </div>
</div>

<div class="footer">
  <p>Powered by <a href="https://t.me/YOUR_TELEGRAM_USERNAME" target="_blank">@YourBot</a></p>
</div>

</body>
</html>
"""

def cleanup_old_files():
    now = time.time()
    cutoff = now - (MAX_FILE_AGE_DAYS * 86400)
    for filename in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            os.remove(path)
            print("🧹 Deleted old file:", filename)

def background_cleanup():
    while True:
        cleanup_old_files()
        time.sleep(86400)  # Run once a day

threading.Thread(target=background_cleanup, daemon=True).start()

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    filename = f.filename
    path = os.path.join(UPLOAD_DIR, filename)
    f.save(path)
    url = request.url_root.strip("/") + f"/watch/{filename}"
    return jsonify({"url": url})

@app.route("/watch/<filename>")
def watch(filename):
    video_url = f"/static/{filename}"
    return render_template_string(HTML_TEMPLATE, video_url=video_url)

app.static_folder = UPLOAD_DIR

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
