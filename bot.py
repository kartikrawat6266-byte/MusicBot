import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
        """
🎵 Premium Music Bot Active!

━━━━━━━━━━━━━━
⚡ Fast Download
🎧 HQ Audio
📥 Instant Upload

👑 Owner:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━

Use:
/play song name
"""
    )


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

        await msg.edit_text(f"⬇️ Downloading:\n{title}")

        ydl_opts = {
            "format": "140/bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "cookiefile": None
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await msg.edit_text("❌ Download failed")

        await msg.edit_text("📤 Uploading Audio...")

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="YouTube Music",
            caption=f"""
🎵 Download Complete

🏷 Song:
{title}

👑 Owner:
@BeStChEaT_OwNeR
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
