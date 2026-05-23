import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

# ENV VARIABLES
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# BOT CLIENT
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# DOWNLOAD FOLDER
os.makedirs("downloads", exist_ok=True)


# START COMMAND
@app.on_message(filters.command("start"))
async def start(client, message: Message):

    await message.reply_text(
        """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗔𝗖𝗧𝗜𝗩𝗘

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝟯𝟮𝟬𝗞𝗕𝗣𝗦 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗔𝗖𝗧𝗜𝗩𝗘
🏓 𝗟𝗢𝗪 𝗣𝗜𝗡𝗚 𝗦𝗬𝗦𝗧𝗘𝗠
━━━━━━━━━━━━━━━━━━━

💡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦:

/play song name

📌 𝗘𝗫𝗔𝗠𝗣𝗟𝗘:
/play Alan Walker

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
━━━━━━━━━━━━━━━━━━━
"""
    )


# PLAY COMMAND
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
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚

🎵 {title}

⚡ Ultra Fast Server...
"""
        )

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

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"""
📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚

🎵 {title}

⚡ Speed: Ultra Fast
"""
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music",
            caption=f"""
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 𝟯𝟮𝟬𝗞𝗕𝗣𝗦
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🏷 𝗦𝗢𝗡𝗚:
{title}

⚡ 𝗦𝗣𝗘𝗘𝗗:
𝗨𝗹𝘁𝗿𝗮 𝗙𝗮𝘀𝘁

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
