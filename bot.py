import os
import asyncio
import yt_dlp
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import tempfile
import re

# ============== YOUR TOKENS ==============
TELEGRAM_TOKEN = "8867495388:AAHRhMzEyjM_29dykChsDlBlSBa4aRigteE"
TMDB_API_KEY = "dd704eb8a6d78d77566aea8269a44f37"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ============== SETUP ==============
DOWNLOAD_FOLDER = tempfile.mkdtemp()
print(f"📁 Download folder: {DOWNLOAD_FOLDER}")

# ============== YT-DLP OPTIONS WITH FIXES ==============
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'ignoreerrors': True,
    'no_check_certificate': True,
    'prefer_insecure': True,
    'cookiefile': None,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

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
    }],
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'nocheckcertificate': True
}

YDL_VIDEO = {
    'format': 'worst[ext=mp4]',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'nocheckcertificate': True
}

# ============== SONG FUNCTIONS WITH BETTER SEARCH ==============
async def download_audio(query):
    try:
        # Clean the query
        search_query = query.strip()
        
        # If it's not a URL, add search prefix
        if not search_query.startswith('http'):
            search_query = f"ytsearch5:{search_query}"
        
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search_query, download=False)
                
                # If search results, get first result
                if 'entries' in info:
                    if not info['entries']:
                        return None
                    info = info['entries'][0]
                
                # Now download with audio options
                with yt_dlp.YoutubeDL(YDL_AUDIO) as ydl_audio:
                    audio_info = ydl_audio.extract_info(info['webpage_url'], download=True)
                    
                    filename = ydl_audio.prepare_filename(audio_info)
                    filename = filename.rsplit('.', 1)[0] + '.mp3'
                    
                    if not os.path.exists(filename):
                        return None
                    
                    return {
                        'file': filename,
                        'title': audio_info.get('title', 'Song'),
                        'artist': audio_info.get('uploader', 'Unknown'),
                        'duration': audio_info.get('duration', 0)
                    }
            except Exception as e:
                print(f"Extract Error: {e}")
                return None
                
    except Exception as e:
        print(f"Audio Error: {e}")
        return None

async def download_video(query):
    try:
        search_query = query.strip()
        if not search_query.startswith('http'):
            search_query = f"ytsearch5:{search_query}"
        
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info:
                if not info['entries']:
                    return None
                info = info['entries'][0]
            
            with yt_dlp.YoutubeDL(YDL_VIDEO) as ydl_video:
                video_info = ydl_video.extract_info(info['webpage_url'], download=True)
                filename = ydl_video.prepare_filename(video_info)
                file_size = os.path.getsize(filename) / (1024 * 1024)
                
                return {
                    'file': filename,
                    'title': video_info.get('title', 'Video'),
                    'artist': video_info.get('uploader', 'Unknown'),
                    'duration': video_info.get('duration', 0),
                    'size_mb': file_size
                }
    except Exception as e:
        print(f"Video Error: {e}")
        return None

# ============== MOVIE FUNCTIONS ==============
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
        "`/audio song name` - Send MP3 audio\n"
        "`/video song name` - Send MP4 video\n\n"
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
        await update.message.reply_text("❌ Usage: `/audio song name`\nExample: `/audio Believer`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎵 Searching: `{query}`...\n⏳ Please wait (10-30 seconds)...")
    
    song = await download_audio(query)
    
    if not song or not os.path.exists(song['file']):
        await msg.edit_text(f"❌ Song not found: `{query}`\n\n💡 Tips:\n• Check spelling\n• Try: `/audio {query} song`\n• Try different song name")
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
                caption=f"🎵 *{song['title'][:50]}*\n👤 {song['artist']}\n⏱️ {duration}\n📦 {file_size:.1f} MB",
                parse_mode='Markdown'
            )
        await msg.delete()
        cleanup(song['file'])
    except Exception as e:
        await msg.edit_text(f"❌ Upload error: {str(e)[:100]}")
        cleanup(song['file'])

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/video song name`\nExample: `/video Believer`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎬 Searching: `{query}`...\n⏳ Please wait...")
    
    video = await download_video(query)
    
    if not video or not os.path.exists(video['file']):
        await msg.edit_text(f"❌ Video not found: `{query}`")
        return
    
    duration = f"{video['duration']//60}:{video['duration']%60:02d}"
    
    await msg.edit_text(f"📤 Uploading video... ({video['size_mb']:.1f} MB)")
    
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
            await msg.edit_text(f"⚠️ Video too large! ({video['size_mb']:.1f} MB)")
        
        cleanup(video['file'])
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:100]}")
        cleanup(video['file'])

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/movie Movie Name Year`\nExample: `/movie Inception 2010`", parse_mode='Markdown')
        return
    
    parts = query.rsplit(' ', 1)
    year = parts[1] if len(parts) > 1 and parts[1].isdigit() else None
    movie_name = parts[0] if year else query
    
    msg = await update.message.reply_text(f"🔍 Searching: `{movie_name}`...")
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await msg.edit_text(f"❌ Movie not found: `{query}`\n\n💡 Try:\n• Check spelling\n• Add year: `/movie {movie_name} 2010`")
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
        await update.message.reply_text("❌ Usage: `/watch Movie Name Year`\nExample: `/watch Avengers 2019`", parse_mode='Markdown')
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

# ============== MAIN ==============
def main():
    print("✅ Bot starting...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running! Send /start on Telegram")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
