import os
import json
import time
import asyncio
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

import yt_dlp
from youtubesearchpython import VideosSearch

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

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

# =========================
# FILE CREATE
# =========================

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

        users[user_id] = {
            "name": user.first_name,
            "username": user.username or "No Username",
            "join_time": datetime.now().strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )
        }

        save_users(users)

# =========================
# TEXTS
# =========================

START_TEXT = """
🎧 PREMIUM MUSIC BOT ACTIVE

━━━━━━━━━━━━━━━━━━━
⚡ ULTRA FAST DOWNLOAD
🚀 HIGH SPEED SERVER
🎵 HQ AUDIO + VIDEO
📥 LIVE DOWNLOAD
📡 24/7 ONLINE
━━━━━━━━━━━━━━━━━━━

🎵 AUDIO:
/play song name

🎬 VIDEO:
/video song name

📚 HELP:
/help

👑 OWNER:
@BeStChEaT_OwNeR
"""

HELP_TEXT = """
📚 PREMIUM MUSIC BOT HELP

🎵 AUDIO:
/play song name

🎬 VIDEO:
/video song name

👑 OWNER:
@BeStChEaT_OwNeR
"""

BAN_TEXT = """
🚫 ACCESS BLOCKED

❌ You are banned from using this bot.

👑 OWNER:
@BeStChEaT_OwNeR
"""

UNBAN_TEXT = """
✅ ACCESS RESTORED

🎉 You can use the bot again.

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

@app.on_callback_query(filters.regex("help"))
async def help_callback(client, query: CallbackQuery):

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🏠 Main Menu",
                    callback_data="main_menu"
                )
            ]
        ])
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

    await query.message.edit_text(
        "👑 OWNER PANEL",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "👥 Users",
                    callback_data="users"
                )
            ],
            [
                InlineKeyboardButton(
                    "📜 Banned",
                    callback_data="banned"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Main Menu",
                    callback_data="main_menu"
                )
            ]
        ])
    )

# =========================
# USERS
# =========================

@app.on_callback_query(filters.regex("users"))
async def users(client, query: CallbackQuery):

    users = load_users()

    text = "👥 USERS LIST\n\n"

    for uid, data in users.items():

        text += f"""
👤 {data['name']}
🆔 {uid}
🔗 @{data['username']}

━━━━━━━━━━━━
"""

    await query.message.edit_text(
        text[:4000],
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="owner_panel"
                )
            ]
        ])
    )

# =========================
# BANNED USERS
# =========================

@app.on_callback_query(filters.regex("banned"))
async def banned_users(client, query: CallbackQuery):

    banned = load_banned()

    text = "📜 BANNED USERS\n\n"

    if not banned:
        text += "❌ No banned users"

    for uid in banned:
        text += f"🆔 {uid}\n"

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="owner_panel"
                )
            ]
        ])
    )

# =========================
# BAN
# =========================

@app.on_message(filters.command("ban"))
async def ban_user(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "/ban user_id"
        )

    user_id = str(message.command[1])

    banned = load_banned()

    banned[user_id] = {
        "time": datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )
    }

    save_banned(banned)

    await message.reply_text(
        "🚫 User banned successfully"
    )

    try:
        await app.send_message(
            int(user_id),
            BAN_TEXT
        )
    except:
        pass

# =========================
# UNBAN
# =========================

@app.on_message(filters.command("unban"))
async def unban_user(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "/unban user_id"
        )

    user_id = str(message.command[1])

    banned = load_banned()

    if user_id in banned:
        del banned[user_id]

    save_banned(banned)

    await message.reply_text(
        "✅ User unbanned successfully"
    )

    try:
        await app.send_message(
            int(user_id),
            UNBAN_TEXT
        )
    except:
        pass

# =========================
# SEARCH FUNCTION
# =========================

def search_youtube(query):

    search = VideosSearch(query, limit=1)
    result = search.result()

    if not result["result"]:
        return None

    video = result["result"][0]

    return {
        "title": video["title"],
        "link": video["link"]
    }

# =========================
# AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching...\n\n🎵 {query}"
    )

    try:

        data = search_youtube(query)

        if not data:
            return await msg.edit_text(
                "❌ Song not found"
            )

        title = data["title"]
        url = data["link"]

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        await msg.edit_text(
            "📥 Downloading audio..."
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        await msg.edit_text(
            "📤 Uploading audio..."
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot"
        )

        await msg.delete()

        os.remove(file_path)

    except Exception as e:

        await msg.edit_text(
            f"❌ DOWNLOAD FAILED\n\n{e}"
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
            "❌ Example:\n/video Faded"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching...\n\n🎬 {query}"
    )

    try:

        data = search_youtube(query)

        if not data:
            return await msg.edit_text(
                "❌ Video not found"
            )

        title = data["title"]
        url = data["link"]

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True
        }

        await msg.edit_text(
            "📥 Downloading video..."
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        await msg.edit_text(
            "📤 Uploading video..."
        )

        await message.reply_video(
            video=file_path,
            caption=title,
            supports_streaming=True
        )

        await msg.delete()

        os.remove(file_path)

    except Exception as e:

        await msg.edit_text(
            f"❌ DOWNLOAD FAILED\n\n{e}"
        )

print("✅ Bot Running")

app.run()
