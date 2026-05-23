import os
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

# ================= CONFIG =================

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "YOUR_BOT_TOKEN"

# ==========================================

app = Client(
    "PremiumMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

# ================= START =================

START_TEXT = """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━

⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 320𝗞𝗕𝗣𝗦
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 24/7 𝗢𝗡𝗟𝗜𝗡𝗘

━━━━━━━━━━━━━━━━━━━

📌 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:

/play song name
/video song name
/ping

━━━━━━━━━━━━━━━━━━━

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
"""

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(START_TEXT)

# ================= PING =================

@app.on_message(filters.command("ping"))
async def ping(client, message: Message):

    ping = random.randint(20, 80)

    await message.reply_text(
        f"""
🏓 𝗣𝗜𝗡𝗚: {ping} ms

⚡ 𝗦𝗘𝗥𝗩𝗘𝗥 𝗦𝗧𝗔𝗧𝗨𝗦:
🟢 ONLINE
🚀 FAST RESPONSE
📡 PREMIUM SPEED
"""
    )

# ================= AUDIO =================

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
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "nocheckcertificate": True,
            "ignoreerrors": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            if not info:
                return await msg.edit_text(
                    "❌ Download failed.\nTry another song."
                )

            if "entries" in info:
                info = info["entries"][0]

            if not info:
                return await msg.edit_text(
                    "❌ Song unavailable."
                )

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await msg.edit_text("❌ Audio file missing")

        await msg.edit_text("📤 Uploading Audio...")

        ping = random.randint(20, 80)

        caption = f"""
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━

⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 320𝗞𝗕𝗣𝗦
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 24/7 𝗢𝗡𝗟𝗜𝗡𝗘

━━━━━━━━━━━━━━━━━━━

🏷 𝗦𝗢𝗡𝗚:
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
            performer="Premium Music Bot",
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

# ================= VIDEO =================

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

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ Video not found")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"⬇️ Downloading Video:\n{title}"
        )

        ydl_opts = {
            "format": "best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "nocheckcertificate": True,
            "ignoreerrors": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            if not info:
                return await msg.edit_text(
                    "❌ Download failed.\nTry another video."
                )

            if "entries" in info:
                info = info["entries"][0]

            if not info:
                return await msg.edit_text(
                    "❌ Video unavailable."
                )

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await msg.edit_text("❌ Video file missing")

        await msg.edit_text("📤 Uploading Video...")

        ping = random.randint(20, 80)

        caption = f"""
🎬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━

⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎥 𝗛𝗗 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 24/7 𝗢𝗡𝗟𝗜𝗡𝗘

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
