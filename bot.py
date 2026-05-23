import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL

# VARIABLES
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# BOT CLIENT
bot = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# START COMMAND
@bot.on_message(filters.command("start"))
async def start(_, message: Message):

    await message.reply_text(
        """
🎵 Premium Music Bot Active!

━━━━━━━━━━━━━━
⚡ Ultra Fast Download
🎧 HQ Music
📥 Instant Audio
🏓 Live Ping
👑 Owner:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━

💡 Commands:

/play song name

📌 Example:
/play Golden Brown
"""
    )

# PLAY COMMAND
@bot.on_message(filters.command("play"))
async def play(_, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Golden Brown"
        )

    query = " ".join(message.command[1:])

    searching = await message.reply_text(
        f"🔍 Searching:\n`{query}`"
    )

    start_time = time.time()

    try:

try:
    ydl_opts = {
        "format": "best",
        "outtmpl": "music.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
        "cookiefile": "cookies.txt",
        "geo_bypass": True
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(query, download=True)

        if "entries" in info:
            info = info["entries"][0]

        title = info["title"]
        file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await message.reply_audio(
            audio=file_path,
            title=title,
            caption=f"""
🎵 Download Complete

━━━━━━━━━━━━━━
🏷 Song:
{title}

⚡ Ping:
{ping} ms

👑 Owner:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━
"""
        )

        os.remove(file_path)

        await searching.delete()

    except Exception as e:
        await searching.edit_text(
            f"❌ Error:\n`{e}`"
        )

print("🎵 Music Bot Started!")

bot.run()
