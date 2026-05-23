import os
import aiohttp
import json
import re
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

# ============== YOUTUBE SEARCH WITHOUT YT-DLP ==============
async def search_youtube(song_name):
    """Search YouTube and get video URL using yt-dlp (but simpler)"""
    try:
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        search_query = f"ytsearch1:{song_name}"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                return video.get('url')
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None

async def download_audio_direct(song_name):
    """Download audio using yt-dlp with best settings"""
    try:
        import yt_dlp
        
        ydl_opts = {
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
            'default_search': 'ytsearch',
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'geo_bypass': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search and download directly
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                filename = ydl.prepare_filename(video)
                filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                if os.path.exists(filename):
                    return {
                        'file': filename,
                        'title': video.get('title', song_name),
                        'artist': video.get('uploader', 'Unknown'),
                        'duration': video.get('duration', 0)
                    }
        return None
    except Exception as e:
        print(f"Download error: {e}")
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
            print(f"Cleaned: {filepath}")
    except:
        pass

# ============== COMMANDS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *✨ ULTIMATE MEDIA BOT ✨*\n\n"
        "*🎵 SONG COMMANDS*\n"
        "`/audio song name` - Send MP3 audio\n\n"
        "*🎬 MOVIE COMMANDS*\n"
        "`/movie name year` - Movie info + poster\n"
        "`/watch name year` - HD streaming links\n\n"
        "*Examples:*\n"
        "`/audio Golden Brown`\n"
        "`/audio Believer`\n"
        "`/movie Inception 2010`\n\n"
        "⚡ *Bot is Active!*",
        parse_mode='Markdown'
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/audio song name`\nExample: `/audio Golden Brown`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎵 Processing: `{query}`...\n⏳ Please wait (30-60 seconds)...")
    
    try:
        song = await download_audio_direct(query)
        
        if not song or not os.path.exists(song['file']):
            await msg.edit_text(
                f"❌ Song not found: `{query}`\n\n"
                f"💡 Try these working examples:\n"
                f"• `/audio Believer`\n"
                f"• `/audio Shape of You`\n"
                f"• `/audio Blinding Lights`\n"
                f"• `/audio Kesariya`\n\n"
                f"Note: First time may take 60 seconds"
            )
            return
        
        duration = f"{song['duration']//60}:{song['duration']%60:02d}"
        file_size = os.path.getsize(song['file']) / (1024 * 1024)
        
        await msg.edit_text(f"📤 Uploading... ({file_size:.1f} MB)")
        
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
        await msg.edit_text(f"❌ Error: {str(e)[:100]}\n\nTry: `/audio Believer` first to test")
        print(f"Command error: {e}")

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
    print("=" * 50)
    print("🎬 ULTIMATE MEDIA BOT STARTING")
    print("=" * 50)
    
    # Test import
    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except Exception as e:
        print(f"❌ yt-dlp import error: {e}")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running! Send /start on Telegram")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
