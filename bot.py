import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8937999210:AAFhMDKRMs5yIIaO9QtU1zWzjYhAPz5iRCo"

app = Client("music_bot", api_id=API_ID, api_hash=API_app = Client(\"music_bot\", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 *Music Bot Active!*\n\n"
        "Jo song name bologe woh audio file bhej dunga!\n\n"
        "*Commands:*\n"
        "`/play song_name` - Song bhejega\n"
        "`/song song_name` - Song download karega\n\n"
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
    
    # YouTube search
    results = YoutubeSearch(query, max_results=1).to_dict()
    if not results:
        await status.edit_text(f"❌ *Song nahi mila:* `{query}`", parse_mode="Markdown")
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
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Convert to mp3 if needed
            if filename.endswith('.webm'):
                filename = filename.replace('.webm', '.mp3')
        
        await status.delete()
        await message.reply_audio(
            filename,
            title=title,
            performer="YouTube",
            caption=f"🎵 *{title}*\n⏱️ {duration}\n\n✅ Requested by: {message.from_user.first_name}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await status.edit_text(f"❌ *Error:* {str(e)[:100]}", parse_mode="Markdown")

@app.on_message(filters.command("song"))
async def song_command(client, message: Message):
    # Same as play command
    await play_command(client, message)

async def main():
    import os
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    await app.start()
    print("🎵 Music Bot is running!")
    print("✅ Send /play song_name to get audio")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
