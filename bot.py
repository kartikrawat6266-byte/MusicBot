# =========================
# PREMIUM MUSIC BOT
# FULL FIXED VERSION
# REAL DOWNLOAD PROGRESS
# YOUTUBE ERROR FIXED
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
🎧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗔𝗖𝗧𝗜𝗩𝗘

━━━━━━━━━━━━━━━━━━━
⚡ 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
🚀 𝗛𝗜𝗚𝗛 𝗦𝗣𝗘𝗘𝗗 𝗦𝗘𝗥𝗩𝗘𝗥
🎵 𝗛𝗤 𝗔𝗨𝗗𝗜𝗢 + 𝗩𝗜𝗗𝗘𝗢
📥 𝗟𝗜𝗩𝗘 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗
📡 𝟮𝟰/𝟳 𝗢𝗡𝗟𝗜𝗡𝗘
━━━━━━━━━━━━━━━━━━━

🎵 AUDIO:
`/play song name`

🎬 VIDEO:
`/video song name`

📚 HELP:
`/help`

👑 OWNER:
@BeStChEaT_OwNeR
"""

HELP_TEXT = """
📚 PREMIUM MUSIC BOT HELP

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
• Live Download Progress
• Live Ping
• Instant Upload
• 24/7 Online

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""

BAN_TEXT = """
🚫 ACCESS BLOCKED

━━━━━━━━━━━━━━━━━━━
❌ Your access suspended.

👑 OWNER:
@BeStChEaT_OwNeR
"""

UNBAN_TEXT = """
✅ ACCESS RESTORED

━━━━━━━━━━━━━━━━━━━
🎉 You can use bot again.

👑 OWNER:
@BeStChEaT_OwNeR
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
            ),
            InlineKeyboardButton(
                "🏠 Main Menu",
                callback_data="main_menu"
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

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="owner_panel"
            )
        ]
    ])

    await query.message.edit_text(
        "🚫 USE:\n`/ban user_id`",
        reply_markup=buttons
    )

# =========================
# UNBAN INFO
# =========================

@app.on_callback_query(filters.regex("unban_info"))
async def unban_info(client, query: CallbackQuery):

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="owner_panel"
            )
        ]
    ])

    await query.message.edit_text(
        "✅ USE:\n`/unban user_id`",
        reply_markup=buttons
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

    if user_id == OWNER_ID:
        return await message.reply_text(
            "❌ OWNER CANNOT BE BANNED"
        )

    banned = load_banned()

    banned[str(user_id)] = {
        "time": datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    }

    save_banned(banned)

    await message.reply_text(
        "🚫 USER BANNED SUCCESSFULLY"
    )

    try:
        await app.send_message(
            user_id,
            BAN_TEXT
        )
    except:
        pass

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
        "✅ USER UNBANNED SUCCESSFULLY"
    )

    try:
        await app.send_message(
            user_id,
            UNBAN_TEXT
        )
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

    start_time = time.time()

    msg = await message.reply_text(
        f"🔍 SEARCHING AUDIO...\n\n🎵 {query}"
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

        async def update_progress(text):
            try:
                await msg.edit_text(text)
            except:
                pass

        def progress_hook(d):

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
                    update_progress(
                        f"""
📥 PREMIUM AUDIO DOWNLOAD

━━━━━━━━━━━━━━━━━━━

🎵 SONG:
{title}

📦 DOWNLOADED:
{downloaded} / {total}

📊 PROGRESS:
{percent}

⚡ SPEED:
{speed}

⏳ TIME LEFT:
{eta}

🏓 LIVE PING:
{ping} ms

━━━━━━━━━━━━━━━━━━━
👑 OWNER:
@BeStChEaT_OwNeR
"""
                    ),
                    app.loop
                )

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 30,
            "fragment_retries": 30,
            "extractor_retries": 30,
            "skip_unavailable_fragments": True,
            "progress_hooks": [progress_hook],
            "extract_flat": False,

            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0"
                )
            },

            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "ios",
                        "web"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        ping = round(
            (time.time() - start_time) * 1000
        )

        await msg.edit_text(
            "📤 UPLOADING AUDIO..."
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot",
            caption=f"""
🎧 PREMIUM MUSIC

━━━━━━━━━━━━━━━━━━━

🎵 SONG:
{title}

🏓 PING:
{ping} ms

📡 SERVER:
ONLINE

━━━━━━━━━━━━━━━━━━━
👑 OWNER:
@BeStChEaT_OwNeR
"""
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

    start_time = time.time()

    msg = await message.reply_text(
        f"🔍 SEARCHING VIDEO...\n\n🎬 {query}"
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

        async def update_progress(text):
            try:
                await msg.edit_text(text)
            except:
                pass

        def progress_hook(d):

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
                    update_progress(
                        f"""
📥 PREMIUM VIDEO DOWNLOAD

━━━━━━━━━━━━━━━━━━━

🎬 VIDEO:
{title}

📦 DOWNLOADED:
{downloaded} / {total}

📊 PROGRESS:
{percent}

⚡ SPEED:
{speed}

⏳ TIME LEFT:
{eta}

🏓 LIVE PING:
{ping} ms

━━━━━━━━━━━━━━━━━━━
👑 OWNER:
@BeStChEaT_OwNeR
"""
                    ),
                    app.loop
                )

        ydl_opts = {
            "format": "best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 30,
            "fragment_retries": 30,
            "extractor_retries": 30,
            "skip_unavailable_fragments": True,
            "progress_hooks": [progress_hook],
            "extract_flat": False,

            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0"
                )
            },

            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "ios",
                        "web"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        ping = round(
            (time.time() - start_time) * 1000
        )

        await msg.edit_text(
            "📤 UPLOADING VIDEO..."
        )

        await message.reply_video(
            video=file_path,
            supports_streaming=True,
            caption=f"""
🎬 PREMIUM VIDEO

━━━━━━━━━━━━━━━━━━━

🎥 VIDEO:
{title}

🏓 PING:
{ping} ms

📡 SERVER:
ONLINE

━━━━━━━━━━━━━━━━━━━
👑 OWNER:
@BeStChEaT_OwNeR
"""
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

print("✅ Premium Music Bot Running")

app.run()
