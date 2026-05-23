# =========================
# IMPORTS
# =========================

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

OWNER_ID = 1987818347  # APNA TELEGRAM ID DAALO

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
        json.dump({}, f)

# =========================
# LOAD / SAVE
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

# =========================
# CHECK BAN
# =========================

def is_banned(user_id):
    return False

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
# START
# =========================

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    user_id = message.from_user.id

    if is_banned(user_id):

        return await message.reply_text(
            """
🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗

❌ You are banned from using this bot.

👑 OWNER:
@BeStChEaT_OwNeR
"""
        )

    users = load_users()

    exists = False

    for u in users:

        if u["id"] == user_id:
            exists = True
            break

    if not exists:

        local_time = datetime.utcnow().astimezone()

        users.append(
            {
                "id": user_id,
                "name": message.from_user.first_name,
                "username": message.from_user.username,
                "join_date": local_time.strftime("%d-%m-%Y"),
                "join_time": local_time.strftime("%I:%M:%S %p")
            }
        )

        save_users(users)

    buttons = []

    if user_id == OWNER_ID:

        buttons.append(
            [
                InlineKeyboardButton(
                    "👑 AuRa KaRtiK CoNtRoL 👑",
                    callback_data="owner_panel"
                )
            ]
        )

    await message.reply_text(
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

    text = """
👑 𝗔𝗨𝗥𝗔 𝗞𝗔𝗥𝗧𝗜𝗞 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 👑

━━━━━━━━━━━━━━━━━━━
⚡ PREMIUM OWNER PANEL
🚀 FULL USER CONTROL
📊 LIVE USER HISTORY
🛡 BAN / UNBAN SYSTEM
━━━━━━━━━━━━━━━━━━━
"""

    buttons = [
        [
            InlineKeyboardButton(
                "👥 USER HISTORY",
                callback_data="users"
            )
        ],

        [
            InlineKeyboardButton(
                "🚫 BAN USER",
                callback_data="ban_info"
            ),

            InlineKeyboardButton(
                "✅ UNBAN USER",
                callback_data="unban_info"
            )
        ],

        [
            InlineKeyboardButton(
                "📜 BANNED HISTORY",
                callback_data="banhistory"
            )
        ],

        [
            InlineKeyboardButton(
                "🏠 MAIN MENU",
                callback_data="mainmenu"
            )
        ]
    ]

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# MAIN MENU
# =========================

@app.on_callback_query(filters.regex("mainmenu"))
async def mainmenu(client, query: CallbackQuery):

    buttons = []

    if query.from_user.id == OWNER_ID:

        buttons.append(
            [
                InlineKeyboardButton(
                    "👑 AuRa KaRtiK CoNtRoL 👑",
                    callback_data="owner_panel"
                )
            ]
        )

    await query.message.edit_text(
        START_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# USER HISTORY
# =========================

@app.on_callback_query(filters.regex("users"))
async def users_data(client, query: CallbackQuery):

    users = load_users()

    text = f"""
👥 TOTAL USERS: {len(users)}

━━━━━━━━━━━━━━━━━━━
"""

    for u in users[-50:]:

        username = u["username"]

        if username:
            username = f"@{username}"
        else:
            username = "No Username"

        text += f"""

👤 NAME: {u['name']}
📛 USERNAME: {username}
🆔 ID: {u['id']}

📅 JOINED DATE:
{u['join_date']}

⏰ JOINED TIME:
{u['join_time']}

━━━━━━━━━━━━━━━━━━━
"""

    buttons = [
        [
            InlineKeyboardButton(
                "⬅️ BACK",
                callback_data="owner_panel"
            )
        ]
    ]

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# BAN INFO
# =========================

@app.on_callback_query(filters.regex("ban_info"))
async def ban_info(client, query: CallbackQuery):

    await query.answer(
        "Use: /ban user_id",
        show_alert=True
    )

# =========================
# UNBAN INFO
# =========================

@app.on_callback_query(filters.regex("unban_info"))
async def unban_info(client, query: CallbackQuery):

    await query.answer(
        "Use: /unban user_id",
        show_alert=True
    )

# =========================
# BAN USER
# =========================

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_user(client, message: Message):

    if len(message.command) < 2:

        return await message.reply_text(
            "❌ Usage:\n/ban user_id"
        )

    user_id = message.command[1]

    banned = load_banned()

    banned[user_id] = {
        "ban_date": datetime.utcnow().astimezone().strftime("%d-%m-%Y"),
        "ban_time": datetime.utcnow().astimezone().strftime("%I:%M:%S %p")
    }

    save_banned(banned)

    try:

        await app.send_message(
            int(user_id),
            """
🚫 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗕𝗔𝗡𝗡𝗘𝗗

━━━━━━━━━━━━━━━━━━━
❌ Access Removed
🛡 Premium Security Active
━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""
        )

    except:
        pass

    await message.reply_text(
        "✅ USER BANNED SUCCESSFULLY"
    )

# =========================
# UNBAN USER
# =========================

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_user(client, message: Message):

    if len(message.command) < 2:

        return await message.reply_text(
            "❌ Usage:\n/unban user_id"
        )

    user_id = message.command[1]

    banned = load_banned()

    if user_id in banned:

        del banned[user_id]

        save_banned(banned)

        try:

            await app.send_message(
                int(user_id),
                """
✅ 𝗬𝗢𝗨 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗

━━━━━━━━━━━━━━━━━━━
🎉 Access Restored
⚡ Premium Features Enabled
━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""
            )

        except:
            pass

        await message.reply_text(
            "✅ USER UNBANNED SUCCESSFULLY"
        )

    else:

        await message.reply_text(
            "❌ USER NOT FOUND"
        )

# =========================
# BANNED HISTORY
# =========================

@app.on_callback_query(filters.regex("banhistory"))
async def ban_history(client, query: CallbackQuery):

    banned = load_banned()

    text = f"""
🚫 TOTAL BANNED USERS: {len(banned)}

━━━━━━━━━━━━━━━━━━━
"""

    if not banned:

        text += "\n❌ No banned users"

    for user_id, data in banned.items():

        text += f"""

🆔 USER ID:
{user_id}

📅 BANNED DATE:
{data['ban_date']}

⏰ BANNED TIME:
{data['ban_time']}

━━━━━━━━━━━━━━━━━━━
"""

    buttons = [
        [
            InlineKeyboardButton(
                "⬅️ BACK",
                callback_data="owner_panel"
            )
        ]
    ]

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# PLAY AUDIO
# =========================

@app.on_message(filters.command("play"))
async def play(client, message: Message):

    if is_banned(message.from_user.id):
        return

    if len(message.command) < 2:

        return await message.reply_text(
            "❌ 𝗘𝘅𝗮𝗺𝗽𝗹𝗲:\n/play Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗔𝘂𝗱𝗶𝗼...\n\n🎵 {query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(
            query,
            max_results=1
        ).to_dict()

        if not results:

            return await msg.edit_text(
                "❌ 𝗦𝗼𝗻𝗴 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱"
            )

        song = results[0]

        title = song["title"]

        url = f"https://youtube.com/watch?v={song['id']}"

        await msg.edit_text(
            f"⬇️ 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗔𝘂𝗱𝗶𝗼...\n\n🎵 {title}"
        )

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
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
            f"❌ 𝗘𝗿𝗿𝗼𝗿:\n{e}"
        )

# =========================
# VIDEO
# =========================

@app.on_message(filters.command("video"))
async def video(client, message: Message):

    if is_banned(message.from_user.id):
        return

    if len(message.command) < 2:

        return await message.reply_text(
            "❌ 𝗘𝘅𝗮𝗺𝗽𝗹𝗲:\n/video Alan Walker"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"🔍 𝗦𝗲𝗮𝗿𝗰𝗵𝗶𝗻𝗴 𝗩𝗶𝗱𝗲𝗼...\n\n🎬 {query}"
    )

    start_time = time.time()

    try:

        results = YoutubeSearch(
            query,
            max_results=1
        ).to_dict()

        if not results:

            return await msg.edit_text(
                "❌ 𝗩𝗶𝗱𝗲𝗼 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱"
            )

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
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
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
            f"❌ 𝗘𝗿𝗿𝗼𝗿:\n{e}"
        )

# =========================
# RUN
# =========================

print("✅ Premium Music Bot Running")

app.run()
