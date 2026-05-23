import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8937999210:AAFhMDKRMs5yIIaO9QtU1zWzjYhAPz5iRCo"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if not os.path.exists("downloads"):
    os.makedirs("downloads")

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
    
    results = YoutubeSearch(query, max_results=1).to_dict()
    if not results:
        await status.edit_text(f"❌ *Song nahi mila:* `{query}`", parse_mode="Markdown")
        return
    
    song = results[0]
    url = f"https://youtube.com/watch?v={song['id']}"
    title = song['title']
    duration = song.get('duration', 'Unknown')
    
    await status.edit_text(f"🎵 *Downloading:* `{title}`...\n⏱️ Duration: {duration}", parse_mode="Markdown")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        await status.delete()
        await message.reply_audio(
            filename,
            title=title,
            performer="YouTube",
            caption=f"🎵 *{title}*\n⏱️ {duration}"
        )
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        await status.edit_text(f"❌ *Error:* {str(e)[:100]}", parse_mode="Markdown")

async def main():
    await app.start()
    print("="*40)
    print("✅ MUSIC BOT IS RUNNING!")
    print("Send /play song_name")
    print("="*40)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
