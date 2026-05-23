import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from pytube import YouTube

# =========================
# TELEGRAM API DETAILS
# =========================
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw"

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
# DOWNLOADS FOLDER
# =========================
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# =========================
# START COMMAND
# =========================
@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        "🎵 Music Bot Online!\n\n"
        "Use:\n"
        "/play song name"
    )

# =========================
# PLAY COMMAND
# =========================
@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        await message.reply_text(
            "❌ Example:\n/play Golden Brown"
        )
        return

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching:\n{query}"
    )

    try:
        # Search YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            await msg.edit("❌ Song not found")
            return

        song = results[0]

        title = song["title"]
        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit(
            f"⬇️ Downloading:\n{title}"
        )

        # Download audio
        yt = YouTube(url)

        stream = yt.streams.filter(
            only_audio=True
        ).first()

        file_path = stream.download(
            output_path="downloads"
        )

        # Send audio
        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Music Bot",
            caption=f"🎵 {title}"
        )

        # Delete status message
        await msg.delete()

        # Delete downloaded file
        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        await msg.edit(
            f"❌ Error:\n{str(e)}"
        )

# =========================
# START BOT
# =========================
print("✅ Music Bot Started")

app.run()
