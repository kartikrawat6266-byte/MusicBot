import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("8937999210:AAFMY6svP5Nc6k0stAt-HcFE0LcHOwlobAM")

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Music Bot Online!\n\n"
        "Use:\n/song song name"
    )

# SONG COMMAND
async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n/song faded"
        )
        return

    query = " ".join(context.args)

    msg = await update.message.reply_text(
        f"🔍 Searching:\n{query}"
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
                f"ytsearch1:{query}",
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

        await msg.delete()

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )

# APP
app = Application.builder().token(BOT_TOKEN).build()

# COMMANDS
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("song", song))

print("✅ Music Bot Started")

app.run_polling(drop_pending_updates=True)
