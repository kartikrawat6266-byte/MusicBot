# =========================
# IMPORTS
# =========================

import os
import time
import json

from datetime import datetime

from pyrogram import Client, filters, StopPropagation

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
# FILES
# =========================

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"

# =========================
# CREATE FILES
# =========================

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(BANNED_FILE):
    with open(BANNED_FILE, "w") as f:
        json.dump([], f)

# =========================
# LOAD SAVE
# =========================

def load_data(file):

    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):

    with open(file, "w") as f:
        json.dump(data, f, indent=4)

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
# START TEXT
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

# =========================
# MAIN MENU
# =========================

MAIN_MENU = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👑 AuRa KaRtiK CoNtRoL 👑",
                callback_data="owner_panel"
            )
        ]
    ]
)

# =========================
# CHECK BAN
# =========================

@app.on_message(filters.private, group=-1)
async def check_ban(client, message):

    banned = load_data(BANNED_FILE)

    for user in banned:

        if user["id"] == message.from_user.id:

            await message.reply_text(
                """
🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗

━━━━━━━━━━━━━━━━━━━
❌ You are banned from using this bot.
━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""
            )

            raise StopPropagation

# =========================
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    users = load_data(USERS_FILE)

    exists = False

    for user in users:

        if user["id"] == message.from_user.id:
            exists = True
            break

    if not exists:

        users.append(
            {
                "id": message.from_user.id,
                "name": message.from_user.first_name,
                "username": message.from_user.username,
                "join_date": datetime.now().strftime("%d-%m-%Y"),
                "join_time": datetime.now().strftime("%I:%M %p")
            }
        )

        save_data(USERS_FILE, users)

    await message.reply_text(
        START_TEXT,
        reply_markup=MAIN_MENU
    )

# =========================
# OWNER PANEL
# =========================

@app.on_callback_query(filters.regex("owner_panel"))
async def owner_panel(client, query: CallbackQuery):

    if query.from_user.id != OWNER_ID:
        return await query.answer(
            "❌ Only Owner Can Use This",
            show_alert=True
        )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👥 USER HISTORY",
                    callback_data="user_history"
                )
            ],

            [
                InlineKeyboardButton(
                    "🚫 BAN USER",
                    callback_data="ban_user"
                ),

                InlineKeyboardButton(
                    "✅ UNBAN USER",
                    callback_data="unban_user"
                )
            ],

            [
                InlineKeyboardButton(
                    "📜 BANNED HISTORY",
                    callback_data="banned_history"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ BACK",
                    callback_data="back_panel"
                ),

                InlineKeyboardButton(
                    "🏠 MAIN MENU",
                    callback_data="main_menu"
                )
            ]
        ]
    )

    await query.message.edit_text(
        """
👑 𝗔𝗨𝗥𝗔 𝗞𝗔𝗥𝗧𝗜𝗞 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 👑

━━━━━━━━━━━━━━━━━━━
⚡ PREMIUM OWNER PANEL
🛡 FULL USER CONTROL
📊 LIVE USER HISTORY
🚫 BAN / UNBAN SYSTEM
━━━━━━━━━━━━━━━━━━━
""",
        reply_markup=buttons
    )

# =========================
# MAIN MENU
# =========================

@app.on_callback_query(filters.regex("main_menu"))
async def main_menu(client, query: CallbackQuery):

    await query.message.edit_text(
        START_TEXT,
        reply_markup=MAIN_MENU
    )

# =========================
# BACK BUTTON
# =========================

@app.on_callback_query(filters.regex("back_panel"))
async def back_panel(client, query: CallbackQuery):

    await query.message.edit_text(
        START_TEXT,
        reply_markup=MAIN_MENU
    )

# =========================
# USER HISTORY
# =========================

@app.on_callback_query(filters.regex("user_history"))
async def user_history(client, query: CallbackQuery):

    users = load_data(USERS_FILE)

    text = f"""
👥 𝗧𝗢𝗧𝗔𝗟 𝗨𝗦𝗘𝗥𝗦: {len(users)}

━━━━━━━━━━━━━━━━━━━
"""

    for user in users[-50:]:

        username = user["username"]

        if username:
            username = f"@{username}"
        else:
            username = "No Username"

        text += f"""

👤 NAME: {user['name']}
🆔 ID: {user['id']}
📛 USERNAME: {username}

📅 JOIN DATE:
{user['join_date']}

⏰ JOIN TIME:
{user['join_time']}

━━━━━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ BACK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🏠 MAIN MENU",
                    callback_data="main_menu"
                )
            ]
        ]
    )

    await query.message.edit_text(
        text,
        reply_markup=buttons
    )

# =========================
# BANNED HISTORY
# =========================

@app.on_callback_query(filters.regex("banned_history"))
async def banned_history(client, query: CallbackQuery):

    banned = load_data(BANNED_FILE)

    text = f"""
🚫 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥𝗦: {len(banned)}

━━━━━━━━━━━━━━━━━━━
"""

    for user in banned[-50:]:

        username = user["username"]

        if username:
            username = f"@{username}"
        else:
            username = "No Username"

        text += f"""

👤 NAME: {user['name']}
🆔 ID: {user['id']}
📛 USERNAME: {username}

📅 JOIN DATE:
{user['join_date']}

⏰ JOIN TIME:
{user['join_time']}

🚫 BANNED:
{user['ban_time']}

━━━━━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ BACK",
                    callback_data="owner_panel"
                ),

                InlineKeyboardButton(
                    "🏠 MAIN MENU",
                    callback_data="main_menu"
                )
            ]
        ]
    )

    await query.message.edit_text(
        text,
        reply_markup=buttons
    )

# =========================
# BAN USER
# =========================

@app.on_message(filters.command("ban"))
async def ban_user(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/ban user_id"
        )

    user_id = int(message.command[1])

    banned = load_data(BANNED_FILE)
    users = load_data(USERS_FILE)

    for x in banned:
        if x["id"] == user_id:
            return await message.reply_text(
                "❌ User Already Banned"
            )

    for user in users:

        if user["id"] == user_id:

            user["ban_time"] = datetime.now().strftime(
                "%d-%m-%Y %I:%M %p"
            )

            banned.append(user)

            save_data(BANNED_FILE, banned)

            await app.send_message(
                user_id,
                """
🚫 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗕𝗔𝗡𝗡𝗘𝗗

━━━━━━━━━━━━━━━━━━━
❌ Access Removed
🛡 Security Action Applied
━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""
            )

            return await message.reply_text(
                "✅ User Banned Successfully"
            )

# =========================
# UNBAN USER
# =========================

@app.on_message(filters.command("unban"))
async def unban_user(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/unban user_id"
        )

    user_id = int(message.command[1])

    banned = load_data(BANNED_FILE)

    new_list = []

    removed = False

    for user in banned:

        if user["id"] == user_id:

            removed = True

            await app.send_message(
                user_id,
                """
✅ 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗

━━━━━━━━━━━━━━━━━━━
🎉 Access Restored
⚡ Premium Services Active
━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""
            )

        else:
            new_list.append(user)

    save_data(BANNED_FILE, new_list)

    if removed:
        await message.reply_text(
            "✅ User Unbanned Successfully"
        )
    else:
        await message.reply_text(
            "❌ User Not Found"
        )

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
            return await msg.edit_text(
                "❌ 𝗦𝗼𝗻𝗴 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 15,
            "fragment_retries": 15,
            "extractor_retries": 15,
            "sleep_interval_requests": 3,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "ios"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        ping = round((time.time() - start_time) * 1000)

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="Premium Music Bot",
            caption=f"""
🎧 PREMIUM MUSIC BOT

🏷 SONG:
{title}

🏓 PING:
{ping} ms

👑 OWNER:
@BeStChEaT_OwNeR
"""
        )

        await msg.delete()

    except Exception as e:

        await msg.edit_text(
            f"❌ 𝗘𝗿𝗿𝗼𝗿:\n{e}"
        )

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n/video Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 Searching Video...\n\n🎬 {query}"
    )

    try:

        results = YoutubeSearch(
            query,
            max_results=1
        ).to_dict()

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "retries": 15,
            "fragment_retries": 15,
            "extractor_retries": 15,
            "sleep_interval_requests": 3,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "ios"
                    ]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)

            file_path = ydl.prepare_filename(info)

        await message.reply_video(
            video=file_path,
            caption=f"""
🎬 PREMIUM VIDEO BOT

🏷 VIDEO:
{title}

👑 OWNER:
@BeStChEaT_OwNeR
"""
        )

        await msg.delete()

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{e}"
        )

print("✅ Premium Music Bot Running")

app.run()
