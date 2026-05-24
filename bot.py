# =========================
# PREMIUM MUSIC BOT
# FULLY FIXED FINAL VERSION
# INDIA TIMEZONE FIXED
# JOIN TIME FIXED
# BAN TIME FIXED
# HISTORY TIME FIXED
# =========================

import os
import re
import time
import json
import asyncio
import pytz

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
# INDIA TIMEZONE
# =========================

IST = pytz.timezone("Asia/Kolkata")

def get_ist_time():
    return datetime.now(IST).strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

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

    current_time = get_ist_time()

    if user_id not in users:

        users[user_id] = {
            "name": user.first_name,
            "username": user.username if user.username else "No Username",
            "join_time": current_time,
            "last_active": current_time
        }

    else:

        users[user_id]["last_active"] = current_time

save_users(users)

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# =========================
# TEXTS
# =========================

START_TEXT = """
✨ Welcome To Advanced Music Downloader Bot ✨

Download your favorite songs and videos in premium quality directly from YouTube with super fast speed 🚀

━━━━━━━━━━━━━━━
🎵 Audio Command
➥ "/audio Song Name"

🎬 Video Command
➥ "/video Video Name"
━━━━━━━━━━━━━━━

⚡ What You Get:

✅ Crystal Clear Audio
✅ HD Video Quality
✅ Fast & Smooth Downloads
✅ Optimized Low Size Files
✅ Clean Premium Interface
✅ Instant Results Anytime

💡 Just send the command with any song or video name and the bot will handle the rest automatically.

🛠 Need A Custom Telegram Bot?
📩 Contact The Owner For More Details

👑 Owner : @BeStChEaT_OwNeR
📞 Help & Support : http://BESTCHEAT_OWNER.t.me
"""

HELP_TEXT = """
🎵✨ New Premium Telegram Music Bot ✨🎬

Fast, smooth, and high quality downloads powered by YouTube 🚀

━━━━━━━━━━━━━━━
🎧 Audio Example
➥ "/audio Golden Brown"

🎥 Video Example
➥ "/video Saiyaara"
━━━━━━━━━━━━━━━

🔥 Features:

✅ High Quality Audio
✅ HD Video Downloads
✅ Low MB Size
✅ Fast Download Speed
✅ Premium Interface
✅ Instant Results

⚡ Built for users who want speed, quality, and a premium music experience in one bot.

🤖 Want Your Own Custom Bot?
📩 Contact The Owner For Setup & Details.

👑 Owner : http://BESTCHEAT_OWNER.t.me
📞 Support & Queries: @BeStChEaT_OwNeR
"""

BAN_TEXT = """
🚫 ACCESS BLOCKED

━━━━━━━━━━━━━━━━━━━

❌ YOU ARE BANNED
FROM USING THIS BOT

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
@BeStChEaT_OwNeR
"""

UNBAN_TEXT = """
✅ ACCESS RESTORED

━━━━━━━━━━━━━━━━━━━

🎉 YOU CAN USE
THE BOT AGAIN

━━━━━━━━━━━━━━━━━━━

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
                "👑 AuRa KaRtiK FaTheR ❄️",
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
                "👑 AuRa KaRTiK FaTheR ❄️",
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
        "👑 AuRa KaRtiK FaTheR ❄️",
        reply_markup=buttons
    )

# =========================
# USERS
# =========================

@app.on_callback_query(filters.regex("users"))
async def users(client, query: CallbackQuery):

    users = load_users()

    text = "👥 USER HISTORY\n\n"

    if not users:
        text += "❌ NO USERS"

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
# BANNED USERS
# =========================

@app.on_callback_query(filters.regex("banned_history"))
async def banned_history(client, query: CallbackQuery):

    banned = load_banned()
    users = load_users()

    text = "📜 BANNED USERS\n\n"

    if not banned:
        text += "❌ NO BANNED USERS"

    for user_id, data in banned.items():

        user_data = users.get(str(user_id), {})

        username = user_data.get(
            "username",
            "No Username"
        )

        if username != "No Username":
            username = f"@{username}"

        text += f"""
👤 Telegram Name :
{user_data.get('name', 'Unknown')}

🆔 Telegram ID :
{user_id}

🔗 TG Username :
{username}

🚫 Ban Time :
{data.get('time', 'Unknown')}

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
        "🚫 USE:\n`/ban user_id`",
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
# UNBAN INFO
# =========================

@app.on_callback_query(filters.regex("unban_info"))
async def unban_info(client, query: CallbackQuery):

    await query.message.edit_text(
        "✅ USE:\n`/unban user_id`",
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
        "time": get_ist_time()
    }

    save_banned(banned)

    await message.reply_text(
        "🚫 USER BANNED SUCCESSFULLY"
    )

    try:
        await client.send_message(
            user_id,
            f"""
🚫 ACCESS BLOCKED

━━━━━━━━━━━━━━━━━━━

❌ YOUR ACCESS TO THIS
BOT HAS BEEN SUSPENDED

━━━━━━━━━━━━━━━━━━━

⚡ STATUS :
➜ BANNED FROM BOT

📅 Ban Time :
➜ {get_ist_time()}

━━━━━━━━━━━━━━━━━━━

👑 OWNER :
@BeStChEaT_OwNeR

📞 SUPPORT :
http://BESTCHEAT_OWNER.t.me
"""
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
        await client.send_message(
            user_id,
            f"""
✅ ACCESS RESTORED

━━━━━━━━━━━━━━━━━━━

🎉 YOUR ACCESS HAS
BEEN RESTORED

━━━━━━━━━━━━━━━━━━━

⚡ STATUS :
➜ UNBANNED SUCCESSFULLY

📅 Unban Time :
➜ {get_ist_time()}

━━━━━━━━━━━━━━━━━━━

👑 OWNER :
@BeStChEaT_OwNeR

📞 SUPPORT :
http://BESTCHEAT_OWNER.t.me
"""
        )
    except:
        pass
        
# =========================
# AUDIO
# =========================

@app.on_message(filters.command("audio"))
async def play(client, message: Message):

    if is_banned(message.from_user.id):
        return await message.reply_text(BAN_TEXT)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Example:\n`/audio Golden Brown`"
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    msg = await message.reply_text(
        f"""
╔════════════════════╗
  🔍 SEARCHING AUDIO 🔍
╚════════════════════╝

🎵 SONG:
➜ {query}

⚡ STATUS:
➜ SEARCHING...
"""
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

        title = clean_filename(song["title"])

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
╔══════════════════════╗
    🎧 PREMIUM MUSIC 🎧
╚══════════════════════╝

🎵 SONG NAME:
➜ {title}

━━━━━━━━━━━━━━━━━━━

📥 DOWNLOADED:
➜ {downloaded} / {total}

📊 PROGRESS:
➜ {percent}

🚀 DOWNLOAD SPEED:
➜ {speed}

⏳ TIME LEFT:
➜ {eta}

🏓 LIVE PING:
➜ {ping} ms

━━━━━━━━━━━━━━━━━━━

⚡ STATUS:
➜ DOWNLOADING AUDIO...

📡 SERVER:
➜ ONLINE 24/7

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
➜ @BeStChEaT_OwNeR

💎 POWERED BY:
➜ 〝 𝐇𝐞𝐚𝐕𝐞𝐧 〞
"""
                    ),
                    app.loop
                )

        ydl_opts = {

            "format": "bestaudio/best",

            "outtmpl": "downloads/%(title)s.%(ext)s",

            "cookiefile": "cookies.txt",

            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,

            "retries": 10,
            "extractor_retries": 10,
            "fragment_retries": 10,

            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],

            "prefer_ffmpeg": True,
            "keepvideo": False,

            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },

            "progress_hooks": [progress_hook]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            downloaded_file = ydl.prepare_filename(info)

            file_path = os.path.splitext(
                downloaded_file
            )[0] + ".mp3"

        if not os.path.exists(file_path):
            return await msg.edit_text(
                "❌ AUDIO DOWNLOAD FAILED"
            )

        await msg.edit_text(
            """
╔════════════════════╗
    📤 UPLOADING AUDIO
╚════════════════════╝

⚡ STATUS:
➜ SENDING AUDIO...
"""
        )

        await message.reply_audio(
            audio=file_path,
            title=title,
            performer="⌬ Ｉｍ ➛ 🜲 𝐅𝐚𝐓𝐡𝐞𝐑 𝐊𝐚𝐑𝐭𝐢𝐊 🜲",
            caption=f"""
╔══════════════════╗
  🎧 PREMIUM MUSIC 🎧
╚══════════════════╝

🎵 SONG NAME:
➜ {title}

⚡ STATUS:
➜ SUCCESSFULLY DOWNLOADED

🚀 SERVER:
➜ ULTRA FAST

📡 QUALITY:
➜ HIGH AUDIO

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
➜ @BeStChEaT_OwNeR

💎 POWERED BY:
⌬ Ｉｍ ➛ 🜲 𝐅𝐚𝐓𝐡𝐞𝐑 𝐊𝐚𝐑𝐭𝐢𝐊 🜲
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
            "❌ Example:\n`/video Faded`"
        )

    query = " ".join(message.command[1:])

    start_time = time.time()

    msg = await message.reply_text(
        f"""
╔════════════════════╗
  🔍 SEARCHING VIDEO 🔍
╚════════════════════╝

🎬 VIDEO:
➜ {query}

⚡ STATUS:
➜ SEARCHING...
"""
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

        title = clean_filename(song["title"])

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
╔══════════════════════╗
    🎬 PREMIUM VIDEO 🎬
╚══════════════════════╝

🎥 VIDEO NAME:
➜ {title}

━━━━━━━━━━━━━━━━━━━

📥 DOWNLOADED:
➜ {downloaded} / {total}

📊 PROGRESS:
➜ {percent}

🚀 DOWNLOAD SPEED:
➜ {speed}

⏳ TIME LEFT:
➜ {eta}

🏓 LIVE PING:
➜ {ping} ms

━━━━━━━━━━━━━━━━━━━

⚡ STATUS:
➜ DOWNLOADING VIDEO...

📡 SERVER:
➜ ONLINE 24/7

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
➜ @BeStChEaT_OwNeR

💎 POWERED BY:
➜  〝 𝐇𝐞𝐚𝐕𝐞𝐧 〞
"""
                    ),
                    app.loop
                )

        ydl_opts = {

            "format": "best[ext=mp4]/best",

            "outtmpl": f"downloads/{title}.%(ext)s",

            "cookiefile": "cookies.txt",

            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "nocheckcertificate": True,

            "retries": 10,
            "extractor_retries": 10,
            "fragment_retries": 10,

            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },

            "progress_hooks": [progress_hook]
        }

        await msg.edit_text(
            """
╔════════════════════╗
    📥 DOWNLOADING 📤
╚════════════════════╝

⚡ STATUS:
➜ FETCHING VIDEO...
"""
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            file_path = ydl.prepare_filename(info)

        if not os.path.exists(file_path):
            return await msg.edit_text(
                "❌ VIDEO DOWNLOAD FAILED"
            )

        await msg.edit_text(
            """
╔════════════════════╗
  📤 UPLOADING VIDEO 📤
╚════════════════════╝

⚡ STATUS:
➜ SENDING VIDEO...
"""
        )

        await message.reply_video(
            video=file_path,
            supports_streaming=True,
            caption=f"""
╔══════════════════╗
  🎬 PREMIUM VIDEO 🎬
╚══════════════════╝

🎥 VIDEO NAME:
➜ {title}

⚡ STATUS:
➜ SUCCESSFULLY DOWNLOADED

🚀 SERVER:
➜ ULTRA FAST

📡 QUALITY:
➜ HD VIDEO

━━━━━━━━━━━━━━━━━━━

👑 OWNER:
➜ @BeStChEaT_OwNeR

💎 POWERED BY:
⌬ Ｉｍ ➛ 🜲 𝐅𝐚𝐓𝐡𝐞𝐑 𝐊𝐚𝐑𝐭𝐢𝐊 🜲
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
            f"❌ DOWNLOAD FAILED\n\n{e}"
        )

# =========================
# RUN
# =========================

print("✅ Premium Music Bot Running")

app.run()
