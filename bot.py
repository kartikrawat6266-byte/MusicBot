import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

#━━━━━━━━━━━━━━━━━━━#
# VARIABLES
#━━━━━━━━━━━━━━━━━━━#

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

#━━━━━━━━━━━━━━━━━━━#
# BOT CLIENT
#━━━━━━━━━━━━━━━━━━━#

app = Client(
    "PremiumMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

#━━━━━━━━━━━━━━━━━━━#
# FOLDERS
#━━━━━━━━━━━━━━━━━━━#

os.makedirs("downloads", exist_ok=True)

#━━━━━━━━━━━━━━━━━━━#
# START COMMAND
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    text = """
🎧 𝗨𝗟𝗧𝗥𝗔 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
⚡ Ultra Fast Download
🚀 High Speed Server
🎵 HQ Music 320KBPS
📹 HD Video Download
📡 24/7 Online
🏓 Low Ping System
━━━━━━━━━━━━━━━━━━━

💡 COMMANDS

🎵 /play song name
📹 /video song name

📌 EXAMPLES

/play Alan Walker
/video Alan Walker

👑 OWNER
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━
"""

    await message.reply_text(text)

#━━━━━━━━━━━━━━━━━━━#
# PLAY AUDIO
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚

🎵 {query}

⚡ Please Wait...
"""
    )

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Song not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢

🎵 {title}

⚡ Ultra Fast Speed...
"""
        )

        ydl_opts = {
            "format": "140/bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music",
            caption=f"""
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖

━━━━━━━━━━━━━━━━━━━
🏷 SONG:
{title}

⚡ SPEED:
Ultra Fast

🏓 PING:
{ping} ms

👑 OWNER:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━
"""
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await msg.edit_text(f"❌ Error:\n{e}")

#━━━━━━━━━━━━━━━━━━━#
# VIDEO DOWNLOAD
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/video Alan Walker"
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢

📹 {query}

⚡ Please Wait...
"""
    )

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Video not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢

📹 {title}

⚡ Ultra Fast Speed...
"""
        )

        ydl_opts = {
            "format": "mp4",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await message.reply_video(
            video=file_path,
            caption=f"""
📹 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢

━━━━━━━━━━━━━━━━━━━
🏷 TITLE:
{title}

⚡ SPEED:
Ultra Fast

🏓 PING:
{ping} ms

👑 OWNER:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━
"""
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await msg.edit_text(f"❌ Error:\n{e}")

#━━━━━━━━━━━━━━━━━━━#

print("✅ Ultra Premium Music Bot Running")

app.run()
