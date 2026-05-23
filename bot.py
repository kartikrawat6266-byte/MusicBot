import os
import time
import yt_dlp

from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch
import yt_dlp

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw"

app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)


@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        "🎵 Music Bot Active!\n\n"
        "Use:\n"
        "/play song name"
    )


@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Golden Brown"
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    msg = await message.reply_text(
        f"""
🔍 Searching...

🎵 {query}
"""
    )

    try:

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "default_search": "ytsearch1",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(query, download=True)

            if "entries" in info:
                info = info["entries"][0]

            title = info.get("title", "Unknown")
            duration = info.get("duration_string", "Unknown")

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await msg.edit_text(
                "❌ Download failed"
            )

        await msg.edit_text(
            f"""
📤 Uploading...

🎵 {title}

💎 Premium Quality
"""
        )

        ping = round((time.time() - start_time) * 1000)

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music",
            caption=f"""
✨━━━━━━━━━━━━━━━━━━✨
🎵 {title}
✨━━━━━━━━━━━━━━━━━━✨

⏱ Duration: {duration}

⚡ Ping: {ping} ms
🚀 Status: Online
💎 Quality: High

👑 Owner: @BeStChEaT_OwNeR
"""
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{e}"
        )


print("✅ Music Bot Running")

app.run()
