import asyncio
import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8937999210:AAFhMDKRMs5yIIaO9QtU1zWzjYhAPz5iRCo"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Search function using yt-dlp
async def search_youtube(query):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch1',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            return info['entries'][0]
        return info

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 *Music Bot Active!*\n\n"
        "*Commands:*\n"
        "`/play song_name` - Song bhejega\n\n"
        "*Example:* `/play Bala hatke`",
        parse_mode="Markdown"
    )

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Song name likho! Example: `/play Bala hatke`")
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply_text(f"🎵 *Searching:* `{query}`...", parse_mode="Markdown")
    
    try:
        # Search using yt-dlp
        song = await search_youtube(query)
        if not song:
            await status.edit_text(f"❌ *Song nahi mila:* `{query}`", parse_mode="Markdown")
            return
        
        # Get video URL
        if song.get('url'):
            video_url = song['url']
        else:
            video_url = f"https://youtube.com/watch?v={song['id']}"
        
        title = song.get('title', query)
        
        await status.edit_text(f"🎵 *Downloading:* `{title}`...", parse_mode="Markdown")
        
        # Download audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
        
        await status.delete()
        await message.reply_audio(
            filename,
            title=title,
            performer="YouTube",
            caption=f"🎵 *{title}*"
        )
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        await status.edit_text(f"❌ *Error:* {str(e)[:150]}", parse_mode="Markdown")

async def main():
    await app.start()
    print("="*40)
    print("✅ MUSIC BOT IS RUNNING!")
    print("Send /play song_name")
    print("="*40)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
