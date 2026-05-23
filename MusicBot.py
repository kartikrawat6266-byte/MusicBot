import os
import asyncio
import yt_dlp
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import tempfile
import shutil

load_dotenv()

# ============== TOKENS ==============
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ============== TEMP FOLDER FOR RAILWAY ==============
# Railway has limited storage, use temp folder
DOWNLOAD_FOLDER = tempfile.mkdtemp()
print(f"📁 Download folder: {DOWNLOAD_FOLDER}")

# Audio download options (lower quality for faster download)
YDL_AUDIO = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'extract_audio': True,
    'audio_format': 'mp3',
    'audio_quality': '128',  # Lower quality for faster download
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }]
}

# Video download options (lowest quality for Railway)
YDL_VIDEO = {
    'format': 'worst[ext=mp4]',  # Smallest size for Railway
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

# ============== SONG AUDIO ==============
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
                'thumbnail': info.get('thumbnail', ''),
                'video_url': f"https://youtube.com/watch?v={info['id']}"
            }
    except Exception as e:
        print(f"Audio Error: {e}")
        return None

# ============== SONG VIDEO ==============
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
                'video_url': f"https://youtube.com/watch?v={info['id']}"
            }
    except Exception as e:
        print(f"Video Error: {e}")
        return None

# ============== MOVIE INFO ==============
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

# ============== CLEANUP ==============
def cleanup(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned: {filepath}")
    except:
        pass

# ============== BOT COMMANDS ==============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *✨ ULTIMATE MEDIA BOT ✨*\n\n"
        "*Commands:*\n\n"
        "🎵 *SONG COMMANDS*\n"
        "`/audio song name` - Send MP3 audio\n"
        "`/video song name` - Send MP4 video\n\n"
        "🎬 *MOVIE COMMANDS*\n"
        "`/movie name year` - Movie info + poster\n"
        "`/watch name year` - HD streaming links\n\n"
        "*Examples:*\n"
        "`/audio Believer`\n"
        "`/video Believer`\n"
        "`/movie Inception 2010`\n"
        "`/watch Avengers 2019`\n\n"
        "⚡ *Powered by Railway*",
        parse_mode='Markdown'
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ *Usage:* `/audio song name`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎵 *Downloading:* `{query}`...\n⏳ Please wait...", parse_mode='Markdown')
    
    song = await download_audio(query)
    
    if not song or not os.path.exists(song['file']):
        await msg.edit_text("❌ *Error:* Song not found!", parse_mode='Markdown')
        return
    
    duration = f"{song['duration']//60}:{song['duration']%60:02d}"
    file_size = os.path.getsize(song['file']) / (1024 * 1024)
    
    await msg.edit_text(f"📤 *Uploading...* ({file_size:.1f} MB)")
    
    try:
        with open(song['file'], 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=song['title'][:100],
                performer=song['artist'],
                duration=song['duration'],
                caption=f"🎵 *{song['title'][:50]}*\n👤 {song['artist']}\n⏱️ {duration}\n📦 {file_size:.1f} MB",
                parse_mode='Markdown'
            )
        await msg.delete()
        cleanup(song['file'])
    except Exception as e:
        await msg.edit_text(f"❌ *Error:* {str(e)[:100]}", parse_mode='Markdown')
        cleanup(song['file'])

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ *Usage:* `/video song name`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎬 *Downloading video:* `{query}`...\n⏳ Please wait...", parse_mode='Markdown')
    
    video = await download_video(query)
    
    if not video or not os.path.exists(video['file']):
        await msg.edit_text("❌ *Error:* Video not found!", parse_mode='Markdown')
        return
    
    duration = f"{video['duration']//60}:{video['duration']%60:02d}"
    
    await msg.edit_text(f"📤 *Uploading video...* ({video['size_mb']:.1f} MB)")
    
    try:
        if video['size_mb'] <= 50:
            with open(video['file'], 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"🎬 *{video['title'][:100]}*\n👤 {video['artist']}\n⏱️ {duration}\n📦 {video['size_mb']:.1f} MB",
                    parse_mode='Markdown'
                )
            await msg.delete()
        else:
            await msg.edit_text(f"⚠️ *Video too large!* ({video['size_mb']:.1f} MB)\n📺 [Watch on YouTube]({video['video_url']})", parse_mode='Markdown')
        
        cleanup(video['file'])
    except Exception as e:
        await msg.edit_text(f"❌ *Error:* {str(e)[:100]}", parse_mode='Markdown')
        cleanup(video['file'])

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ *Usage:* `/movie Movie Name Year`", parse_mode='Markdown')
        return
    
    parts = query.rsplit(' ', 1)
    year = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
    movie_name = parts[0] if year else query
    
    msg = await update.message.reply_text(f"🔍 *Searching:* `{movie_name}`...", parse_mode='Markdown')
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await msg.edit_text(f"❌ *Movie not found:* `{query}`", parse_mode='Markdown')
        return
    
    caption = (
        f"🎬 *{movie['title']} ({movie['year']})*\n\n"
        f"⭐ *Rating:* {movie['rating']}/10 {movie['stars']}\n"
        f"⏱️ *Runtime:* {movie['runtime']} min\n"
        f"🎭 *Genres:* `{'`, `'.join(movie['genres'][:3])}`\n\n"
        f"📝 *Overview:* {movie['overview'][:300]}...\n\n"
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
        await update.message.reply_text("❌ *Usage:* `/watch Movie Name Year`", parse_mode='Markdown')
        return
    
    parts = query.rsplit(' ', 1)
    year = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
    movie_name = parts[0] if year else query
    
    msg = await update.message.reply_text(f"🔍 *Getting links for:* `{movie_name}`...", parse_mode='Markdown')
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await msg.edit_text(f"❌ *Movie not found:* `{query}`", parse_mode='Markdown')
        return
    
    streams = (
        f"🎬 *{movie['title']} ({movie['year']})* - *HD LINKS*\n\n"
        f"**Source 1 (4K):**\n`https://vidsrc.to/embed/movie/{movie['id']}`\n\n"
        f"**Source 2 (1080p):**\n`https://www.2embed.to/embed/tmdb/movie/{movie['id']}`\n\n"
        f"⭐ *Rating:* {movie['rating']}/10 {movie['stars']}\n"
        f"💡 *Click link to watch in browser*"
    )
    
    await msg.delete()
    
    if movie['poster']:
        await update.message.reply_photo(photo=movie['poster'], caption=streams, parse_mode='Markdown')
    else:
        await update.message.reply_text(streams, parse_mode='Markdown')

# ============== MAIN ==============
async def main():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running on Railway!")
    print(f"📁 Temp folder: {DOWNLOAD_FOLDER}")
    
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
