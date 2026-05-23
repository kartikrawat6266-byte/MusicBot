import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
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

# Create downloads folder
os.makedirs("downloads", exist_ok=True)


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 Music Bot Active!\n\n"
        "Command:\n"
        "/play song name"
    )


@app.on_message(filters.command("play"))
async def play_command(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    status = await message.reply_text(
        f"🔍 Searching:\n{query}"
    )

    try:
        # Search song
        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await status.edit_text("❌ Song not found")

        song = results[0]

        title = song["title"]
        url = f"https://youtube.com/watch?v={song['id']}"

        await status.edit_text(f"⬇️ Downloading:\n{title}")

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Check file exists
        if not os.path.exists(file_path):
            return await status.edit_text("❌ Download failed")

        await status.edit_text("📤 Uploading audio...")

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="YouTube Music",
            caption=f"🎵 {title}"
        )

        await status.delete()

        # Delete file
        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{str(e)}")


async def main():
    await app.start()

    print("✅ Music Bot Running")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
