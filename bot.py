import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch
import yt_dlp

API_ID = int(os.getenv("35140329"))
API_HASH = os.getenv("011f638e4acadee178c59afffc80193d")
BOT_TOKEN = os.getenv("8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw")

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
        f"""
🎵 **Premium Music Bot Active!**

✨ Fast Download
⚡ Ultra Speed
📥 HQ Audio
🏓 Ping System
👑 Owner: @BeStChEaT_OwNeR

💡 Usage:
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
            "❌ Example:\n`/play Golden Brown`"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching:\n`{query}`"
    )

    start_time = time.time()

    try:
        # SEARCH SONG
        search = VideosSearch(query, limit=1)
        result = search.result()["result"][0]

        title = result["title"]
        url = result["link"]

        await msg.edit_text(
            f"""
🎧 Found Song

🏷 Name: {title}
📥 Downloading...
"""
        )

        # DOWNLOAD OPTIONS
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "music.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "cookiefile": "cookies.txt"
        }

        # DOWNLOAD SONG
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        # SEND AUDIO
        await message.reply_audio(
            audio=file_path,
            title=title,
            caption=f"""
🎵 Download Complete

🏷 Song: {title}
⚡ Ping: {ping} ms
👑 Powered By: @BeStChEaT_OwNeR
"""
        )

        # DELETE FILE
        os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n`{e}`")

print("🎵 Music Bot Started!")

bot.run()
