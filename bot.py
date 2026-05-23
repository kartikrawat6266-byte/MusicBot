import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
import yt_dlp

API_ID = 35140329
API_HASH = "011f638e4acadee178c59afffc80193d"
BOT_TOKEN = "8917775888:AAHvVcNK1RG7ty6bR7OIRmCSGJcKAPWjirw"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "🎵 *Music Bot Active!*\n\n"
        "Commands:\n"
        "/play song_name - Play song\n"
        "/stream YT_LINK - Live stream\n\n"
        "Example: `/play Bala hatke`\n"
        "Live: `/stream https://youtu.be/abc123`",
        parse_mode="Markdown"
    )

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Song name likho!")
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply_text(f"🎵 Searching: {query}...")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await status.edit_text("❌ Song nahi mila!")
            return
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")
        return
    
    song = results[0]
    url = f"https://youtube.com/watch?v={song['id']}"
    title = song['title']
    
    await status.edit_text(f"🎵 Downloading: {title}...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    
    try:
        import os
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        await status.delete()
        await message.reply_audio(filename, title=title)
        
        # Cleanup
        try:
            os.remove(filename)
        except:
            pass
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")

async def main():
    await app.start()
    print("✅ Music Bot is running!")
    print("Send /play song_name")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
