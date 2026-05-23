import os
import yt_dlp
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import tempfile
import time

# ============== YOUR TOKENS ==============
TELEGRAM_TOKEN = "8867495388:AAHRhMzEyjM_29dykChsDlBlSBa4aRigteE"
TMDB_API_KEY = "dd704eb8a6d78d77566aea8269a44f37"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ============== SETUP ==============
DOWNLOAD_FOLDER = tempfile.mkdtemp()
print(f"📁 Download folder: {DOWNLOAD_FOLDER}")

# ============== YT-DLP CONFIGURATION ==============
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
    'noplaylist': True,
    'default_search': 'ytsearch',
}

def download_audio_sync(song_name):
    """Download audio from YouTube"""
    try:
        print(f"Searching: {song_name}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search and download
            search_query = f"ytsearch:{song_name}"
            info = ydl.extract_info(search_query, download=True)
            
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                
                # Get the downloaded file path
                filename = ydl.prepare_filename(video)
                mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                if os.path.exists(mp3_filename):
                    return {
                        'file': mp3_filename,
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
        "🎵 *✨ MUSIC BOT ✨*\n\n"
        "*COMMANDS:*\n"
        "`/play song name` - Download and send MP3 audio\n\n"
        "*MOVIE COMMANDS:*\n"
        "`/movie name year` - Movie info + poster\n"
        "`/watch name year` - HD streaming links\n\n"
        "*EXAMPLES:*\n"
        "`/play Golden Brown`\n"
        "`/play Believer`\n"
        "`/movie Inception 2010`\n\n"
        "⚡ *Bot is Ready!*",
        parse_mode='Markdown'
    )

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download and send audio"""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text(
            "❌ *Usage:* `/play song name`\n"
            "*Example:* `/play Golden Brown`",
            parse_mode='Markdown'
        )
        return
    
    msg = await update.message.reply_text(
        f"🎵 *Searching & Downloading:* `{query}`...\n"
        f"⏳ Please wait (20-40 seconds)...",
        parse_mode='Markdown'
    )
    
    # Download audio
    result = download_audio_sync(query)
    
    if not result or not os.path.exists(result['file']):
        await msg.edit_text(
            f"❌ *Song not found:* `{query}`\n\n"
            f"💡 *Try:* `/play {query} song`\n"
            f"✅ *Working:* `/play Believer`",
            parse_mode='Markdown'
        )
        return
    
    duration = f"{result['duration']//60}:{result['duration']%60:02d}"
    file_size = os.path.getsize(result['file']) / (1024 * 1024)
    
    await msg.edit_text(f"📤 *Uploading...* ({file_size:.1f} MB)", parse_mode='Markdown')
    
    try:
        with open(result['file'], 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=result['title'][:100],
                performer=result['artist'],
                duration=result['duration'],
                caption=f"🎵 *{result['title'][:50]}*\n👤 {result['artist']}\n⏱️ {duration}\n📦 {file_size:.1f} MB",
                parse_mode='Markdown'
            )
        
        await msg.delete()
        cleanup(result['file'])
        
    except Exception as e:
        await msg.edit_text(f"❌ *Error:* {str(e)[:100]}", parse_mode='Markdown')
        cleanup(result['file'])

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text(
            "❌ *Usage:* `/movie Movie Name Year`\n"
            "*Example:* `/movie Inception 2010`",
            parse_mode='Markdown'
        )
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
        f"🎭 *Genres:* {', '.join(movie['genres'][:3])}\n\n"
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
        await update.message.reply_text(
            "❌ *Usage:* `/watch Movie Name Year`\n"
            "*Example:* `/watch Avengers 2019`",
            parse_mode='Markdown'
        )
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
        f"🎬 *{movie['title']} ({movie['year']})* - HD LINKS\n\n"
        f"**4K Quality:**\n`https://vidsrc.to/embed/movie/{movie['id']}`\n\n"
        f"**1080p Quality:**\n`https://www.2embed.to/embed/tmdb/movie/{movie['id']}`\n\n"
        f"⭐ *Rating:* {movie['rating']}/10 {movie['stars']}\n"
        f"💡 *Click link to watch in browser*"
    )
    
    await msg.delete()
    
    if movie['poster']:
        await update.message.reply_photo(photo=movie['poster'], caption=streams, parse_mode='Markdown')
    else:
        await update.message.reply_text(streams, parse_mode='Markdown')

# ============== MAIN ==============
def main():
    print("=" * 50)
    print("🎵 MUSIC BOT STARTING...")
    print("=" * 50)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running!")
    print("📁 Download folder:", DOWNLOAD_FOLDER)
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
