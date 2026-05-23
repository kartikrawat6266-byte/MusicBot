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

START_TEXT = """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗔𝗖𝗧𝗜𝗩𝗘

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 + 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🎵 𝗔𝗨𝗗𝗜𝗢:
`/play song name`

🎬 𝗩𝗜𝗗𝗘𝗢:
`/video song name`

📌 𝗘𝗫𝗔𝗠𝗣𝗟𝗘:
`/play Golden Brown`
`/video Alan Walker`

👑 𝗢𝗪𝗡𝗘𝗥:
@BeStChEaT_OwNeR
"""

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(START_TEXT)

# =========================
# PLAY AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ 𝗘𝘅𝗮𝗺𝗽𝗹𝗲:\n`/play Alan Walker`"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗔𝘂𝗱𝗶𝗼...\n\n🎵 {query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ 𝗦𝗼𝗻𝗴 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"⬇️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗔𝘂𝗱𝗶𝗼...\n\n🎵 {title}"
        )

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,

            # ===== FIX ADDED =====
            "extractor_args": {
                "youtube": {
                    "player_client": ["android_creator"]
                }
            },

            "http_headers": {
                "User-Agent": "com.google.android.youtube/"
            },

            "sleep_interval_requests": 1,
            "retries": 10,
            "fragment_retries": 10
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"📤 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗔𝘂𝗱𝗶𝗼...\n\n⚡ 𝗣𝗶𝗻𝗴: {ping} ms"
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot",
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

        error_text = str(e)

        if "Sign in to confirm you’re not a bot" in error_text:
            error_text = (
                "❌ YouTube temporary blocked request.\n\n"
                "🔄 Wait 20-30 seconds and try again."
            )

        await msg.edit_text(
            f"❌ 𝗘𝗿𝗿𝗼𝗿:\n{error_text}"
        )

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ 𝗘𝘅𝗮𝗺𝗽𝗹𝗲:\n`/video Alan Walker`"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗩𝗶𝗱𝗲𝗼...\n\n🎬 {query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text("❌ 𝗩𝗶𝗱𝗲𝗼 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱")

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"⬇️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗩𝗶𝗱𝗲𝗼...\n\n🎬 {title}"
        )

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,

            # ===== FIX ADDED =====
            "extractor_args": {
                "youtube": {
                    "player_client": ["android_creator"]
                }
            },

            "http_headers": {
                "User-Agent": "com.google.android.youtube/"
            },

            "sleep_interval_requests": 1,
            "retries": 10,
            "fragment_retries": 10
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"📤 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗩𝗶𝗱𝗲𝗼...\n\n⚡ 𝗣𝗶𝗻𝗴: {ping} ms"
        )

        await message.reply_video(
            video=file_path,
            caption=f"""
🎬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢 𝗕𝗢𝗧
━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎥 𝗙𝗨𝗟𝗟 𝗛𝗗 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━
🏷 𝗩𝗜𝗗𝗘𝗢:
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

        error_text = str(e)

        if "Sign in to confirm you’re not a bot" in error_text:
            error_text = (
                "❌ YouTube temporary blocked request.\n\n"
                "🔄 Wait 20-30 seconds and try again."
            )

        await msg.edit_text(
            f"❌ 𝗘𝗿𝗿𝗼𝗿:\n{error_text}"
        )

print("✅ Premium Music Bot Running")

app.run()
