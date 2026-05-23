import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8867495388:AAHRhMzEyjM_29dykChsDlBlSBa4aRigteE"

async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text("🎵 Song searching...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)

            video = info['entries'][0]
            filename = ydl.prepare_filename(video)

        await update.message.reply_audio(
            audio=open(filename, 'rb'),
            title=video['title']
        )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_song))

print("Bot Started...")
app.run_polling()
