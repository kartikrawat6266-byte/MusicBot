import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

# =========================
# CONFIG
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# BOT
# =========================

app = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        """
🎵 PREMIUM MUSIC BOT ACTIVE

━━━━━━━━━━━━━━━
⚡ Ultra Fast Download
🎧 HQ Audio + Video
🚀 Instant Upload
📡 Live Ping System
👑 Premium Server
━━━━━━━━━━━━━━━

🎵 Audio:
`/play song name`

🎬 Video:
`/video song name`

📌 Example:
`/play Golden Brown`
`/video Alan Walker`
"""
    )

# =========================
# PLAY AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching Audio...\n\n🎵 {query}"
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
            f"⬇️ Downloading Audio...\n\n🎵 {title}"
        )

        ydl_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "extractaudio": True,
    "audioformat": "mp3",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "320",
    }]
}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"📤 Uploading Audio...\n\n⚡ Ping: {ping} ms"
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot",
            caption=f"""
🎵 PREMIUM AUDIO DOWNLOADED

━━━━━━━━━━━━━━━
🏷 Title: {title}

⚡ Speed: Ultra Fast
📡 Ping: {ping} ms
🎧 Quality: HQ Audio
👑 Status: Premium
━━━━━━━━━━━━━━━
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

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/video Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching Video...\n\n🎬 {query}"
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
            f"⬇️ Downloading Video...\n\n🎬 {title}"
        )

ydl_opts = {
    "format": "best[ext=mp4]/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "nocheckcertificate": True
}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"📤 Uploading Video...\n\n⚡ Ping: {ping} ms"
        )

        await message.reply_video(
            video=file_path,
            caption=f"""
🎬 PREMIUM VIDEO DOWNLOADED

━━━━━━━━━━━━━━━
🏷 Title: {title}

⚡ Speed: Ultra Fast
📡 Ping: {ping} ms
🎧 Quality: HD Video
👑 Status: Premium
━━━━━━━━━━━━━━━
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
