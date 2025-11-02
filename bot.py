from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
UPLOAD_API = os.getenv("UPLOAD_API")  # e.g., https://yourapp.onrender.com/upload

def shorten_url(long_url: str) -> str:
    """Shorten a link using TinyURL API."""
    try:
        api = "https://tinyurl.com/api-create.php"
        resp = requests.get(api, params={"url": long_url})
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        print("TinyURL failed:", e)
    return long_url  # fallback

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("Please send a video file!")
        return

    file = await video.get_file()
    file_path = f"downloads/{video.file_id}.mp4"
    os.makedirs("downloads", exist_ok=True)
    await file.download_to_drive(file_path)
    await update.message.reply_text("⏳ Uploading your video...")

    with open(file_path, "rb") as f:
        resp = requests.post(UPLOAD_API, files={"file": f})

    if resp.status_code == 200:
        long_url = resp.json().get("url")
        short_url = shorten_url(long_url)
        await update.message.reply_text(f"🎬 Your streamable video:\n{short_url}")
    else:
        await update.message.reply_text("Upload failed 😢")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
app.run_polling()
