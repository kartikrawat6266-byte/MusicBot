import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch
import yt_dlp

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
        f"""
🎵 **Premium Music Bot Active!**

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
            "❌ Example:\n`/play Golden Brown`"
        )

    query = " ".join(message.command[1:])

    searching = await message.reply_text(
        f"""
🔍 Searching Song...

🎵 Query:
`{query}`
"""
    )

    start_time = time.time()

    try:
        # SEARCH VIDEO
        search = VideosSearch(query, limit=1)
        result = search.result()["result"][0]

        title = result["title"]
        url = result["link"]

        await searching.edit_text(
            f"""
🎧 Song Found!

🏷 Title:
`{title}`

📥 Downloading Audio...
"""
        )

        # YT-DLP OPTIONS
        ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "outtmpl": "music.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "extractaudio": True,
    "audioformat": "mp3",
    "default_search": "ytsearch",
    "geo_bypass": True
}
        

        # DOWNLOAD AUDIO
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

        # DELETE FILE
        os.remove(file_path)

        await searching.delete()

    except Exception as e:
        await searching.edit_text(
            f"❌ Error:\n`{e}`"
        )

print("🎵 Music Bot Started!")

bot.run()
