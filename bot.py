import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

# =========================
# TELEGRAM API DETAILS
# =========================
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8937999210:AAFhMDKRMs5yIIaO9QtU1zWzjYhAPz5iRCo"

# =========================
# BOT CLIENT
# =========================
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# DOWNLOAD FOLDER
# =========================
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# =========================
# START COMMAND
# =========================
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 Music Bot Active!\n\n"
        "Commands:\n"
        "/play song_name - Download song\n\n"
        "Example:\n"
        "/play Bala Hatke"
    )

# =========================
# PLAY COMMAND
# =========================
@app.on_message(filters.command("play"))
async def play_command(client, message: Message):

    if len(message.command) < 2:
        await message.reply_text(
            "❌ Song name likho!\nExample:\n/play Bala Hatke"
        )
        return

    query = " ".join(message.command[1:])

    status = await message.reply_text(
        f"🔍 Searching:\n{query}"
    )

    try:
        # Search YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            await status.edit_text("❌ Song nahi mila")
            return

        song = results[0]

        title = song["title"]
        duration = song.get("duration", "Unknown")

        url = f"https://youtube.com/watch?v={song['id']}"

        await status.edit_text(
            f"⬇️ Downloading:\n{title}\n⏱ {duration}"
        )

        # Download settings
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Send audio
        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="YouTube",
            caption=f"🎵 {title}\n⏱ {duration}"
        )

        await status.delete()

        # Delete downloaded file
        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{str(e)}")

# =========================
# MAIN
# =========================
async def main():
    await app.start()

    print("=" * 40)
    print("✅ MUSIC BOT RUNNING")
    print("🎵 Use: /play song_name")
    print("=" * 40)

    await asyncio.Event().wait()

# =========================
# START BOT
# =========================
if __name__ == "__main__":
    asyncio.run(main())
