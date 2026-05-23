import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("8937999210:AAFMY6svP5Nc6k0stAt-HcFE0LcHOwlobAM")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found!")
    exit()

async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song_name = update.message.text

    searching = await update.message.reply_text(
        f"🎵 Searching:\n{song_name}"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"ytsearch1:{song_name}",
                download=True
            )

            video = info["entries"][0]

            filename = ydl.prepare_filename(video)

        await update.message.reply_audio(
            audio=open(filename, "rb"),
            title=video["title"],
            performer="MusicBot"
        )

        os.remove(filename)

        await searching.delete()

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        music_handler
    )
)

print("✅ Music Bot Started")

app.run_polling(drop_pending_updates=True)
