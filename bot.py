import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

#━━━━━━━━━━━━━━━━━━━#
# CONFIG
#━━━━━━━━━━━━━━━━━━━#

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "PremiumMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

#━━━━━━━━━━━━━━━━━━━#
# START
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 320KBPS
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 24/7 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🎵 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:

/play song name
/video song name
/ping

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
"""
    )

#━━━━━━━━━━━━━━━━━━━#
# PING
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("ping"))
async def ping(_, message: Message):

    start = time.time()

    msg = await message.reply_text("🏓 Pinging...")

    end = round((time.time() - start) * 1000)

    await msg.edit_text(
        f"""
🏓 𝗣𝗜𝗡𝗚!

⚡ 𝗦𝗣𝗘𝗘𝗗:
{end} ms

🚀 𝗦𝗘𝗥𝗩𝗘𝗥:
𝗢𝗡𝗟𝗜𝗡𝗘
"""
    )

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

    msg = await message.reply_text(
        f"🔍 Searching:\n{query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Song not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"⬇️ Downloading Audio:\n{title}"
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "geo_bypass": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text("📤 Uploading Audio...")

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot",
            caption=f"""
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
🏷 𝗦𝗢𝗡𝗚:
{title}

⚡ 𝗦𝗣𝗘𝗘𝗗:
𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧

🏓 𝗣𝗜𝗡𝗚:
{ping} ms

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━

🔥 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗘𝗥
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

    msg = await message.reply_text(
        f"🔍 Searching Video:\n{query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Video not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        ydl_opts = {
            "format": "best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "geo_bypass": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text("📤 Uploading Video...")

        await message.reply_video(
            video=file_path,
            caption=f"""
🎬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
🏷 𝗩𝗜𝗗𝗘𝗢:
{title}

⚡ 𝗦𝗣𝗘𝗘𝗗:
𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧

🏓 𝗣𝗜𝗡𝗚:
{ping} ms

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━

🔥 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗘𝗥
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

print("✅ Premium Music Bot Running")

app.run()
