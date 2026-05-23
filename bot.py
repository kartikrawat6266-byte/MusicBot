import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

#━━━━━━━━━━━━━━━━━━━#
#       CONFIG      #
#━━━━━━━━━━━━━━━━━━━#

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw"

OWNER = "@BeStChEaT_OwNeR"

#━━━━━━━━━━━━━━━━━━━#

app = Client(
    "PremiumMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

os.makedirs("downloads", exist_ok=True)

START_TIME = time.time()

#━━━━━━━━━━━━━━━━━━━#
#      /START       #
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    uptime = int(time.time() - START_TIME)

    text = f"""
✨━━━━━━━━━━━━━━━━━━✨
      🎵 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 🎵
✨━━━━━━━━━━━━━━━━━━✨

👋 𝗛𝗲𝗹𝗹𝗼 {message.from_user.mention}

⚡ 𝗨𝗹𝘁𝗿𝗮 𝗙𝗮𝘀𝘁 𝗬𝗼𝘂𝗧𝘂𝗯𝗲 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗿

🎧 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:

➥ High Quality Audio
➥ Fastest Download
➥ Instant Upload
➥ Unlimited Songs
➥ 24×7 Online
➥ Premium Server

━━━━━━━━━━━━━━━━━━

📥 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:

➤ /play Golden Brown
➤ /play Alan Walker
➤ /play Sidhu Moose Wala

━━━━━━━━━━━━━━━━━━

⏰ 𝗨𝗽𝘁𝗶𝗺𝗲: {uptime} sec
⚡ 𝗣𝗶𝗻𝗴: {round((time.time() - START_TIME)*1000)} ms

👑 𝗢𝘄𝗻𝗲𝗿: {OWNER}
💎 Premium Music Experience
"""

    await message.reply_text(text)

#━━━━━━━━━━━━━━━━━━━#
#       /PING       #
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("ping"))
async def ping(client, message: Message):

    start = time.time()

    msg = await message.reply_text("🏓 Pinging...")

    end = time.time()

    ping = round((end - start) * 1000)

    await msg.edit_text(
        f"""
🏓 𝗣𝗢𝗡𝗚 !

⚡ Ping: {ping} ms
🚀 Status: Online
💎 Server: Premium
"""
    )

#━━━━━━━━━━━━━━━━━━━#
#       /PLAY       #
#━━━━━━━━━━━━━━━━━━━#

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            """
❌ 𝗦𝗼𝗻𝗴 𝗡𝗮𝗺𝗲 𝗠𝗶𝘀𝘀𝗶𝗻𝗴

✅ Example:
/play Golden Brown
"""
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    searching = await message.reply_text(
        f"""
🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴...

🎵 Song: {query}
"""
    )

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await searching.edit_text(
                "❌ Song not found"
            )

        song = results[0]

        title = song["title"]

        duration = song["duration"]

        views = song["views"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await searching.edit_text(
            f"""
⬇️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴...

🎵 Title: {title}
⏱ Duration: {duration}
👁 Views: {views}

⚡ Speed: Ultra Fast
"""
        )

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await searching.edit_text(
                "❌ Download failed"
            )

        await searching.edit_text(
            f"""
📤 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴...

🎵 {title}

💎 Premium Upload Mode
"""
        )

        end_time = time.time()

        ping = round((end_time - start_time) * 1000)

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music",
            caption=f"""
✨━━━━━━━━━━━━━━━━━━✨
🎵 {title}
✨━━━━━━━━━━━━━━━━━━✨

⏱ Duration: {duration}
👁 Views: {views}

⚡ Ping: {ping} ms
🚀 Status: Fast Download
💎 Quality: High

👑 Owner: {OWNER}
"""
        )

        await searching.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await searching.edit_text(
            f"""
❌ Error Occurred

{e}
"""
        )

#━━━━━━━━━━━━━━━━━━━#

print("✅ Premium Music Bot Running")

app.run()
