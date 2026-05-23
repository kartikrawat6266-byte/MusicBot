import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

#━━━━━━━━━━━━━━━━━━━
# CONFIG
#━━━━━━━━━━━━━━━━━━━

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

#━━━━━━━━━━━━━━━━━━━
# BOT CLIENT
#━━━━━━━━━━━━━━━━━━━

app = Client(
    "PremiumMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

#━━━━━━━━━━━━━━━━━━━
# START COMMAND
#━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧
━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 𝟯𝟮𝟬𝗞𝗕𝗣𝗦
🎬 𝗛𝗗 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🎵 𝗔𝗨𝗗𝗜𝗢:
/play song name

🎬 𝗩𝗜𝗗𝗘𝗢:
/video song name

📌 𝗘𝘅𝗮𝗺𝗽𝗹𝗲:
/play Golden Brown
/video Alan Walker

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
"""
    )

#━━━━━━━━━━━━━━━━━━━
# HELP COMMAND
#━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):

    await message.reply_text(
        """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦

━━━━━━━━━━━━━━━━━━━

🎵 /play song name
➜ Download Audio

🎬 /video song name
➜ Download Video

🏓 /ping
➜ Check Bot Speed

📜 /help
➜ Show Commands

━━━━━━━━━━━━━━━━━━━
👑 @BeStChEaT_OwNeR
"""
    )

#━━━━━━━━━━━━━━━━━━━
# PING COMMAND
#━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("ping"))
async def ping(client, message: Message):

    start = time.time()

    msg = await message.reply_text("🏓 Pinging...")

    end = time.time()

    pingms = round((end - start) * 1000)

    await msg.edit_text(
        f"""
🏓 𝗣𝗢𝗡𝗚!

━━━━━━━━━━━━━━━━━━━
⚡ 𝗦𝗣𝗘𝗘𝗗:
Ultra Fast

📡 𝗣𝗜𝗡𝗚:
{pingms} ms

🚀 𝗦𝗘𝗥𝗩𝗘𝗥:
Active 24/7
━━━━━━━━━━━━━━━━━━━
"""
    )

#━━━━━━━━━━━━━━━━━━━
# AUDIO COMMAND
#━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢...

🎵 {query}
"""
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
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢...

🎵 {title}
"""
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"""
📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢...

⚡ Ping: {ping} ms
"""
        )

        caption = f"""
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧
━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 𝟯𝟮𝟬𝗞𝗕𝗣𝗦
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🏷 𝗔𝗨𝗗𝗜𝗢:
{title}

⚡ 𝗦𝗣𝗘𝗘𝗗:
Ultra Fast

🏓 𝗣𝗜𝗡𝗚:
{ping} ms

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR

━━━━━━━━━━━━━━━━━━━
🔥 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗘𝗥
"""

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music",
            caption=caption
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

#━━━━━━━━━━━━━━━━━━━
# VIDEO COMMAND
#━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/video Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢...

🎬 {query}
"""
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Video not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢...

🎬 {title}
"""
        )

        ydl_opts = {
            "format": "mp4",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"""
📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢...

⚡ Ping: {ping} ms
"""
        )

        caption = f"""
🎬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢 𝗕𝗢𝗧
━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎥 𝗛𝗗 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🏷 𝗩𝗜𝗗𝗘𝗢:
{title}

⚡ 𝗦𝗣𝗘𝗘𝗗:
Ultra Fast

🏓 𝗣𝗜𝗡𝗚:
{ping} ms

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR

━━━━━━━━━━━━━━━━━━━
🔥 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗦𝗘𝗥𝗩𝗘𝗥
"""

        await message.reply_video(
            video=file_path,
            caption=caption
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
