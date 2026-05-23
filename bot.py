# =========================
# MUSIC BOT
# FULL FIXED VERSION
# AUDIO + VIDEO FIXED
# LIVE DOWNLOAD PROGRESS
# =========================

import os
import time
import json
import asyncio
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

OWNER_ID = 1987818347

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
# FILES
# =========================

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(BANNED_FILE):
    with open(BANNED_FILE, "w") as f:
        json.dump({}, f)

# =========================
# FUNCTIONS
# =========================

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_banned():
    with open(BANNED_FILE, "r") as f:
        return json.load(f)

def save_banned(data):
    with open(BANNED_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_banned(user_id):

    if int(user_id) == OWNER_ID:
        return False

    banned = load_banned()

    return str(user_id) in banned

def save_user(user):

    users = load_users()

    user_id = str(user.id)

    if user_id not in users:

        join_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        users[user_id] = {
            "name": user.first_name,
            "username": user.username if user.username else "No Username",
            "join_time": join_time
        }

        save_users(users)

# =========================
# TEXTS
# =========================

START_TEXT = """
🎧 MUSIC BOT ACTIVE

━━━━━━━━━━━━━━━━━━━
⚡ FAST DOWNLOAD
🚀 HIGH SPEED SERVER
🎵 HQ AUDIO + VIDEO
📥 LIVE DOWNLOAD
📡 24/7 ONLINE
━━━━━━━━━━━━━━━━━━━

🎵 AUDIO:
`/play song name`

🎬 VIDEO:
`/video song name`

📚 HELP:
`/help`
"""

HELP_TEXT = """
📚 MUSIC BOT HELP

━━━━━━━━━━━━━━━━━━━

🎵 AUDIO:
`/play song name`

🎬 VIDEO:
`/video song name`

📚 HELP:
`/help`

━━━━━━━━━━━━━━━━━━━

⚡ FEATURES:
• HQ Audio
• HD Video
• Live Download Speed
• Live Progress
• Live Ping
• Instant Upload
• 24/7 Online
"""

BAN_TEXT = """
🚫 ACCESS BLOCKED
"""

UNBAN_TEXT = """
✅ ACCESS RESTORED
"""

# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    if is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    save_user(message.from_user)

    buttons = []

    if message.from_user.id == OWNER_ID:
        buttons.append([
            InlineKeyboardButton(
                "👑 OWNER PANEL",
                callback_data="owner_panel"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "📚 Help",
            callback_data="help"
        )
    ])

    await message.reply_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# HELP
# =========================

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="main_menu"
            )
        ]
    ])

    await message.reply_text(
        HELP_TEXT,
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("help"))
async def help_callback(client, query: CallbackQuery):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="main_menu"
            )
        ]
    ])

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=buttons
    )

# =========================
# MAIN MENU
# =========================

@app.on_callback_query(filters.regex("main_menu"))
async def main_menu(client, query: CallbackQuery):

    buttons = []

    if query.from_user.id == OWNER_ID:
        buttons.append([
            InlineKeyboardButton(
                "👑 OWNER PANEL",
                callback_data="owner_panel"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "📚 Help",
            callback_data="help"
        )
    ])

    await query.message.edit_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# OWNER PANEL
# =========================

@app.on_callback_query(filters.regex("owner_panel"))
async def owner_panel(client, query: CallbackQuery):

    if query.from_user.id != OWNER_ID:
        return

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👥 Users",
                callback_data="users"
            )
        ],
        [
            InlineKeyboardButton(
                "🚫 Ban",
                callback_data="ban_info"
            ),
            InlineKeyboardButton(
                "✅ Unban",
                callback_data="unban_info"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 Banned",
                callback_data="banned_history"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="main_menu"
            )
        ]
    ])

    await query.message.edit_text(
        "👑 OWNER CONTROL PANEL",
        reply_markup=buttons
    )

# =========================
# USERS
# =========================

@app.on_callback_query(filters.regex("users"))
async def users(client, query: CallbackQuery):

    users = load_users()

    text = "👥 USER HISTORY\n\n"

    for user_id, data in users.items():

        text += f"""
👤 NAME:
{data['name']}

🔗 USERNAME:
@{data['username']}

🆔 ID:
{user_id}

📅 JOIN TIME:
{data['join_time']}

━━━━━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="owner_panel"
            )
        ]
    ])

    await query.message.edit_text(
        text[:4000],
        reply_markup=buttons
    )

# =========================
# BAN INFO
# =========================

@app.on_callback_query(filters.regex("ban_info"))
async def ban_info(client, query: CallbackQuery):

    await query.message.edit_text(
        "🚫 USE:\n`/ban user_id`"
    )

# =========================
# UNBAN INFO
# =========================

@app.on_callback_query(filters.regex("unban_info"))
async def unban_info(client, query: CallbackQuery):

    await query.message.edit_text(
        "✅ USE:\n`/unban user_id`"
    )

# =========================
# BANNED USERS
# =========================

@app.on_callback_query(filters.regex("banned_history"))
async def banned_history(client, query: CallbackQuery):

    banned = load_banned()

    text = "📜 BANNED USERS\n\n"

    for user_id, data in banned.items():

        text += f"""
🆔 USER ID:
{user_id}

📅 BANNED:
{data['time']}

━━━━━━━━━━━━━━━━━━━
"""

    await query.message.edit_text(text[:4000])

# =========================
# BAN
# =========================

@app.on_message(filters.command("ban"))
async def ban(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ USE:\n`/ban user_id`"
        )

    user_id = int(message.command[1])

    banned = load_banned()

    banned[str(user_id)] = {
        "time": datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    }

    save_banned(banned)

    await message.reply_text(
        "🚫 USER BANNED"
    )

# =========================
# UNBAN
# =========================

@app.on_message(filters.command("unban"))
async def unban(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ USE:\n`/unban user_id`"
        )

    user_id = int(message.command[1])

    banned = load_banned()

    if str(user_id) in banned:
        del banned[str(user_id)]

    save_banned(banned)

    await message.reply_text(
        "✅ USER UNBANNED"
    )

# =========================
# PROGRESS FUNCTION
# =========================

async def progress_message(
    msg,
    title,
    downloaded,
    total,
    percent,
    speed,
    eta,
    ping,
    mode
):

    try:
        await msg.edit_text(f"""
📥 {mode} DOWNLOAD

━━━━━━━━━━━━━━━━━━━

🎵 TITLE:
{title}

📦 DOWNLOADED:
{downloaded} / {total}

📊 PROGRESS:
{percent}

⚡ SPEED:
{speed}

⏳ ETA:
{eta}

🏓 PING:
{ping} ms
""")
    except:
        pass

# =========================
# AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n`/play Alan Walker`"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 SEARCHING...\n\n🎵 {query}"
    )

    try:

        results = YoutubeSearch(
            query,
            max_results=1
        ).to_dict()

        if not results:
            return await msg.edit_text(
                "❌ SONG NOT FOUND"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        start_time = time.time()

        def hook(d):

            if d['status'] == 'downloading':

                downloaded = d.get(
                    '_downloaded_bytes_str',
                    '0MB'
                )

                total = d.get(
                    '_total_bytes_str',
                    'Unknown'
                )

                speed = d.get(
                    '_speed_str',
                    '0MB/s'
                )

                percent = d.get(
                    '_percent_str',
                    '0%'
                )

                eta = d.get(
                    '_eta_str',
                    '0s'
                )

                ping = round(
                    (time.time() - start_time) * 1000
                )

                asyncio.run_coroutine_threadsafe(
                    progress_message(
                        msg,
                        title,
                        downloaded,
                        total,
                        percent,
                        speed,
                        eta,
                        ping,
                        "AUDIO"
                    ),
                    app.loop
                )

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 20,
            "fragment_retries": 20,
            "extractor_retries": 20,
            "progress_hooks": [hook],
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0"
                )
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        await msg.edit_text(
            "📤 UPLOADING AUDIO..."
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Music Bot",
            caption=f"🎵 {title}"
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        print(e)

        await msg.edit_text(
            f"❌ ERROR:\n{e}"
        )

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n`/video Faded`"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 SEARCHING...\n\n🎬 {query}"
    )

    try:

        results = YoutubeSearch(
            query,
            max_results=1
        ).to_dict()

        if not results:
            return await msg.edit_text(
                "❌ VIDEO NOT FOUND"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        start_time = time.time()

        def hook(d):

            if d['status'] == 'downloading':

                downloaded = d.get(
                    '_downloaded_bytes_str',
                    '0MB'
                )

                total = d.get(
                    '_total_bytes_str',
                    'Unknown'
                )

                speed = d.get(
                    '_speed_str',
                    '0MB/s'
                )

                percent = d.get(
                    '_percent_str',
                    '0%'
                )

                eta = d.get(
                    '_eta_str',
                    '0s'
                )

                ping = round(
                    (time.time() - start_time) * 1000
                )

                asyncio.run_coroutine_threadsafe(
                    progress_message(
                        msg,
                        title,
                        downloaded,
                        total,
                        percent,
                        speed,
                        eta,
                        ping,
                        "VIDEO"
                    ),
                    app.loop
                )

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 20,
            "fragment_retries": 20,
            "extractor_retries": 20,
            "progress_hooks": [hook],
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0"
                )
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        await msg.edit_text(
            "📤 UPLOADING VIDEO..."
        )

        await message.reply_video(
            video=file_path,
            caption=f"🎬 {title}"
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        print(e)

        await msg.edit_text(
            f"❌ ERROR:\n{e}"
        )

print("✅ Music Bot Running")

app.run()
