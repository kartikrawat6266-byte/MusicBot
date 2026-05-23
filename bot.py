import os
import asyncio
import yt_dlp
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import tempfile

# ============== YOUR TOKENS ==============
TELEGRAM_TOKEN = "8867495388:AAHRhMzEyjM_29dykChsDlBlSBa4aRigteE"
TMDB_API_KEY = "dd704eb8a6d78d77566aea8269a44f37"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ============== SETUP ==============
DOWNLOAD_FOLDER = tempfile.mkdtemp()
print(f"📁 Download folder: {DOWNLOAD_FOLDER}")
print(f"🤖 Bot Token: {TELEGRAM_TOKEN[:15]}...")
print(f"🎬 TMDB Key: {TMDB_API_KEY[:15]}...")

# ============== YT-DLP OPTIONS ==============
YDL_AUDIO = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'extract_audio': True,
    'audio_format': 'mp3',
    'audio_quality': '128',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }]
}

YDL_VIDEO = {
    'format': 'worst[ext=mp4]',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

# ============== FUNCTIONS ==============
async def download_audio(query):
    try:
        with yt_dlp.YoutubeDL(YDL_AUDIO) as ydl:
            if query.startswith('http'):
                info = ydl.extract_info(query, download=True)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            
            filename = ydl.prepare_filename(info)
            filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            return {
                'file': filename,
                'title': info.get('title', 'Song'),
                'artist': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
            }
    except Exception as e:
        print(f"Audio Error: {e}")
        return None

async def download_video(query):
    try:
        with yt_dlp.YoutubeDL(YDL_VIDEO) as ydl:
            if query.startswith('http'):
                info = ydl.extract_info(query, download=True)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            
            filename = ydl.prepare_filename(info)
            file_size = os.path.getsize(filename) / (1024 * 1024)
            
            return {
                'file': filename,
                'title': info.get('title', 'Video'),
                'artist': info.get('uploader', 'Unknown'),
                'duration': info.get('duration', 0),
                'size_mb': file_size,
            }
    except Exception as e:
        print(f"Video Error: {e}")
        return None

async def get_movie_info(movie_name, year=None):
    async with aiohttp.ClientSession() as session:
        search_url = f"{TMDB_BASE_URL}/search/movie"
        params = {'api_key': TMDB_API_KEY, 'query': movie_name, 'language': 'en-US'}
        if year:
            params['year'] = year
        
        async with session.get(search_url, params=params) as resp:
            data = await resp.json()
            if not data.get('results'):
                return None
            
            movie = data['results'][0]
            movie_id = movie['id']
            
            detail_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
            async with session.get(detail_url, params={'api_key': TMDB_API_KEY}) as detail_resp:
                details = await detail_resp.json()
                
                rating = details.get('vote_average', 0)
                stars = "⭐" * int(rating/2) + "☆" * (5 - int(rating/2))
                
                return {
                    'id': movie_id,
                    'title': details.get('title'),
                    'year': details.get('release_date', 'Unknown')[:4],
                    'rating': rating,
                    'stars': stars,
                    'overview': details.get('overview', 'No description'),
                    'genres': [g['name'] for g in details.get('genres', [])],
                    'runtime': details.get('runtime', 'N/A'),
                    'poster': f"https://image.tmdb.org/t/p/w500{details.get('poster_path', '')}" if details.get('poster_path') else None
                }

def cleanup(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

# ============== COMMANDS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *✨ ULTIMATE MEDIA BOT ✨*\n\n"
        "*🎵 SONG COMMANDS*\n"
        "`/audio song` - Send MP3 audio\n"
        "`/video song` - Send MP4 video\n\n"
        "*🎬 MOVIE COMMANDS*\n"
        "`/movie name year` - Movie info + poster\n"
        "`/watch name year` - HD streaming links\n\n"
        "*Examples:*\n"
        "`/audio Believer`\n"
        "`/video Shape of You`\n"
        "`/movie Inception 2010`\n"
        "`/watch Avengers 2019`\n\n"
        "⚡ *Bot is Active!*",
        parse_mode='Markdown'
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/audio song name`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎵 Downloading: `{query}`... Please wait...")
    
    song = await download_audio(query)
    
    if not song or not os.path.exists(song['file']):
        await msg.edit_text("❌ Song not found!")
        return
    
    duration = f"{song['duration']//60}:{song['duration']%60:02d}"
    file_size = os.path.getsize(song['file']) / (1024 * 1024)
    
    await msg.edit_text(f"📤 Uploading... ({file_size:.1f} MB)")
    
    try:
        with open(song['file'], 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=song['title'][:100],
                performer=song['artist'],
                duration=song['duration'],
                caption=f"🎵 {song['title'][:50]}\n👤 {song['artist']}\n⏱️ {duration}"
            )
        await msg.delete()
        cleanup(song['file'])
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:100]}")
        cleanup(song['file'])

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/video song name`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎬 Downloading video: `{query}`... Please wait...")
    
    video = await download_video(query)
    
    if not video or not os.path.exists(video['file']):
        await msg.edit_text("❌ Video not found!")
        return
    
    duration = f"{video['duration']//60}:{video['duration']%60:02d}"
    
    await msg.edit_text(f"📤 Uploading video... ({video['size_mb']:.1f} MB)")
    
    try:
        if video['size_mb'] <= 50:
            with open(video['file'], 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"🎬 {video['title'][:100]}\n👤 {video['artist']}\n⏱️ {duration}"
                )
            await msg.delete()
        else:
            await msg.edit_text(f"⚠️ Video too large! ({video['size_mb']:.1f} MB)")
        
        cleanup(video['file'])
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:100]}")
        cleanup(video['file'])

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/movie Movie Name Year`")
        return
    
    parts = query.rsplit(' ', 1)
    year = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
    movie_name = parts[0] if year else query
    
    msg = await update.message.reply_text(f"🔍 Searching: `{movie_name}`...")
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await msg.edit_text(f"❌ Movie not found: `{query}`")
        return
    
    caption = (
        f"🎬 *{movie['title']} ({movie['year']})*\n\n"
        f"⭐ Rating: {movie['rating']}/10 {movie['stars']}\n"
        f"⏱️ Runtime: {movie['runtime']} min\n"
        f"🎭 Genres: {', '.join(movie['genres'][:3])}\n\n"
        f"📝 Overview: {movie['overview'][:300]}...\n\n"
        f"📺 `/watch {movie['title']} {movie['year']}`"
    )
    
    await msg.delete()
    
    if movie['poster']:
        await update.message.reply_photo(photo=movie['poster'], caption=caption, parse_mode='Markdown')
    else:
        await update.message.reply_text(caption, parse_mode='Markdown')

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/watch Movie Name Year`")
        return
    
    parts = query.rsplit(' ', 1)
    year = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
    movie_name = parts[0] if year else query
    
    msg = await update.message.reply_text(f"🔍 Getting links for: `{movie_name}`...")
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await msg.edit_text(f"❌ Movie not found: `{query}`")
        return
    
    streams = (
        f"🎬 *{movie['title']} ({movie['year']})* - HD LINKS\n\n"
        f"**4K Quality:**\n`https://vidsrc.to/embed/movie/{movie['id']}`\n\n"
        f"**1080p Quality:**\n`https://www.2embed.to/embed/tmdb/movie/{movie['id']}`\n\n"
        f"⭐ Rating: {movie['rating']}/10 {movie['stars']}\n"
        f"💡 Click link to watch in browser"
    )
    
    await msg.delete()
    
    if movie['poster']:
        await update.message.reply_photo(photo=movie['poster'], caption=streams, parse_mode='Markdown')
    else:
        await update.message.reply_text(streams, parse_mode='Markdown')

# ============== MAIN (FIXED FOR RAILWAY) ==============
def main():
    print("✅ Bot starting...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running! Send /start on Telegram")
    
    # Railway ke liye fix - run_polling directly
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
