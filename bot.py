import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

# =============== CONFIGURATION ===============
API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Create downloads folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 *Music Bot Active!*\n\n"
        "*Commands:*\n"
        "`/play song_name` - Song download karo\n"
        "`/song song_name` - Same as /play\n\n"
        "*Example:* `/play Bala hatke`\n\n"
        "*Note:* Live VC ke liye @KurumiMusicRobot use karo",
        parse_mode="Markdown"
    )

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Song name likho! Example: `/play Bala hatke`")
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply_text(f"🎵 *Searching:* `{query}`...", parse_mode="Markdown")
    
    # Search YouTube
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await status.edit_text(f"❌ *Song nahi mila:* `{query}`", parse_mode="Markdown")
            return
    except Exception as e:
        await status.edit_text(f"❌ *Search error:* {e}", parse_mode="Markdown")
        return
    
    song = results[0]
    url = f"https://youtube.com/watch?v={song['id']}"
    title = song['title']
    duration = song.get('duration', 'Unknown')
    
    await status.edit_text(f"🎵 *Downloading:* `{title}`...\n⏱️ Duration: {duration}", parse_mode="Markdown")
    
    # Download audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Send audio file
        await status.delete()
        await message.reply_audio(
            filename,
            title=title,
            performer="YouTube Music",
            duration=int(duration) if duration != 'Unknown' else 0,
            caption=f"🎵 *{title}*\n⏱️ Duration: {duration}\n\nRequested by: {message.from_user.first_name}",
            parse_mode="Markdown"
        )
        
        # Clean up
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        await status.edit_text(f"❌ *Error:* {str(e)[:200]}", parse_mode="Markdown")

@app.on_message(filters.command("song"))
async def song_command(client, message: Message):
    await play_command(client, message)

async def main():
    await app.start()
    print("="*50)
    print("🎵 MUSIC BOT IS RUNNING!")
    print("✅ Send /play song_name to get audio")
    print("="*50)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
