import os
import time
import json
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from youtube_search import YoutubeSearch
import yt_dlp

# =========================
# CONFIG
# =========================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 123456789  # <-- APNA TELEGRAM ID DAL

# =========================
# BOT
# =========================

app = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# FOLDERS
# =========================

os.makedirs("downloads", exist_ok=True)

USERS_FILE = "users.json"
BAN_FILE = "banned.json"

# =========================
# CREATE FILES
# =========================

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(BAN_FILE):
    with open(BAN_FILE, "w") as f:
        json.dump({
            "banned": [],
            "unbanned": []
        }, f)

# =========================
# SAVE USER
# =========================

def save_user(user):

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    ids = [u["id"] for u in users]

    if user.id not in ids:

        users.append({
            "id": user.id,
            "name": user.first_name,
            "username": user.username if user.username else "None",
            "join_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })

        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

# =========================
# CHECK BAN
# =========================

def is_banned(user_id):

    with open(BAN_FILE, "r") as f:
        data = json.load(f)

    banned_ids = [u["id"] for u in data["banned"]]

    return user_id in banned_ids

# =========================
# YTDLP OPTIONS
# =========================

audio_opts = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "geo_bypass": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

video_opts = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "geo_bypass": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}

# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    save_user(message.from_user)

    if is_banned(message.from_user.id):
        return await message.reply_text(
            """
🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗

━━━━━━━━━━━━━━━━━━━
❌ You Are Banned
👑 Contact Owner
━━━━━━━━━━━━━━━━━━━

👑 @BeStChEaT_OwNeR
"""
        )

    buttons = []

    if message.from_user.id == OWNER_ID:
        buttons.append(
            [
                InlineKeyboardButton(
                    "👑 AuRa OnlY KaRtiK ❄️",
                    callback_data="owner_panel"
                )
            ]
        )

    await message.reply_text(
        """
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 + 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🎵 AUDIO:
`/play song name`

🎬 VIDEO:
`/video song name`

📡 PING:
`/ping`

👑 OWNER:
@BeStChEaT_OwNeR
""",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

# =========================
# PING
# =========================

@app.on_message(filters.command("ping"))
async def ping(_, message: Message):

    start = time.time()

    msg = await message.reply_text("📡 Checking Premium Server...")

    end = time.time()

    ping_ms = round((end - start) * 1000)

    await msg.edit_text(
        f"""
🏓 𝗣𝗢𝗡𝗚

━━━━━━━━━━━━━━━━━━━
⚡ Speed: Ultra Fast
📡 Ping: {ping_ms} ms
🚀 Server: Online
👑 Status: Premium
━━━━━━━━━━━━━━━━━━━
"""
    )

# =========================
# PLAY AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    save_user(message.from_user)

    if is_banned(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text(
            """
❌ Example:

/play Alan Walker
"""
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢

🎵 {query}
"""
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text(
                "❌ Song Not Found"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢

🎵 {title}
"""
        )

        with yt_dlp.YoutubeDL(audio_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"""
📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢

⚡ Ping: {ping} ms
"""
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
Ultra Fast

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
            f"""
❌ 𝗘𝗥𝗥𝗢𝗥

{e}
"""
        )

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    save_user(message.from_user)

    if is_banned(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply_text(
            """
❌ Example:

/video Alan Walker
"""
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"""
🔍 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢

🎬 {query}
"""
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(query, max_results=1).to_dict()

        if not results:
            return await msg.edit_text(
                "❌ Video Not Found"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"""
⬇️ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢

🎬 {title}
"""
        )

        with yt_dlp.YoutubeDL(video_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await msg.edit_text(
            f"""
📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗩𝗜𝗗𝗘𝗢

⚡ Ping: {ping} ms
"""
        )

        await message.reply_video(
            video=file_path,
            caption=f"""
🎬 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗜𝗗𝗘𝗢 𝗕𝗢𝗧

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎥 𝗛𝗗 𝗩𝗜𝗗𝗘𝗢
📥 𝗜𝗡𝗦𝗧𝗔𝗡𝗧 𝗨𝗣𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
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
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await msg.edit_text(
            f"""
❌ 𝗘𝗥𝗥𝗢𝗥

{e}
"""
        )

# =========================
# OWNER PANEL
# =========================

@app.on_callback_query(filters.regex("owner_panel"))
async def owner_panel(client, query: CallbackQuery):

    if query.from_user.id != OWNER_ID:
        return

    buttons = [
        [
            InlineKeyboardButton(
                "👥 User History",
                callback_data="user_history"
            )
        ],
        [
            InlineKeyboardButton(
                "🚫 Ban User",
                callback_data="ban_user"
            ),
            InlineKeyboardButton(
                "✅ Unban User",
                callback_data="unban_user"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 Ban History",
                callback_data="ban_history"
            ),
            InlineKeyboardButton(
                "📜 Unban History",
                callback_data="unban_history"
            )
        ]
    ]

    await query.message.edit_text(
        """
👑 𝗔𝗨𝗥𝗔 𝗢𝗪𝗡𝗘𝗥 𝗣𝗔𝗡𝗘𝗟

━━━━━━━━━━━━━━━━━━━
⚡ Premium Control System
🛡 Full User Management
📡 Live User Database
🚫 Ban / Unban Access
━━━━━━━━━━━━━━━━━━━
""",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# USER HISTORY
# =========================

@app.on_callback_query(filters.regex("user_history"))
async def user_history(client, query: CallbackQuery):

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    text = f"""
👥 𝗨𝗦𝗘𝗥 𝗛𝗜𝗦𝗧𝗢𝗥𝗬

━━━━━━━━━━━━━━━━━━━
📊 Total Users: {len(users)}
━━━━━━━━━━━━━━━━━━━
"""

    for user in users[-20:]:

        text += f"""

👤 Name: {user['name']}
🔗 Username: @{user['username']}
🆔 ID: {user['id']}
📅 Joined: {user['join_date']}
━━━━━━━━━━━━━━━
"""

    await query.message.edit_text(text)

# =========================
# BAN
# =========================

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_user(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Usage:\n/ban user_id"
        )

    user_id = int(message.command[1])

    with open(BAN_FILE, "r") as f:
        data = json.load(f)

    banned_ids = [u["id"] for u in data["banned"]]

    if user_id in banned_ids:
        return await message.reply_text(
            "❌ Already Banned"
        )

    data["banned"].append({
        "id": user_id,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })

    with open(BAN_FILE, "w") as f:
        json.dump(data, f, indent=4)

    try:
        await client.send_message(
            user_id,
            """
🚫 YOU HAVE BEEN BANNED
"""
        )
    except:
        pass

    await message.reply_text(
        "✅ User Banned"
    )

# =========================
# UNBAN
# =========================

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_user(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Usage:\n/unban user_id"
        )

    user_id = int(message.command[1])

    with open(BAN_FILE, "r") as f:
        data = json.load(f)

    data["banned"] = [
        u for u in data["banned"]
        if u["id"] != user_id
    ]

    data["unbanned"].append({
        "id": user_id,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    })

    with open(BAN_FILE, "w") as f:
        json.dump(data, f, indent=4)

    try:
        await client.send_message(
            user_id,
            """
✅ YOU HAVE BEEN UNBANNED
"""
        )
    except:
        pass

    await message.reply_text(
        "✅ User Unbanned"
    )

print("✅ Premium Music Bot Running")

app.run()
