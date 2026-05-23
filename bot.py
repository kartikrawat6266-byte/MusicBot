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

if not os.path.exists("downloads"):
    os.makedirs("downloads")


@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "🎵 Music Bot Online!\n\nUse:\n/play song name"
    )


@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        await message.reply_text("❌ Example:\n/play alone")
        return

    query = " ".join(message.command[1:])

    msg = await message.reply_text(f"🔍 Searching {query}")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            await msg.edit("❌ Song not found")
            return

        song = results[0]

        title = song["title"]
        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit(f"⬇️ Downloading\n{title}")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        await message.reply_audio(
            audio=file,
            title=title,
            performer="Music Bot"
        )

        os.remove(file)

        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error:\n{e}")


print("✅ Bot Started")

app.run()
