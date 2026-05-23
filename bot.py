import os
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

# ============== FIXED YT-DLP OPTIONS ==============
# These options are tested and working
YDL_COMMON = {
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True,
    'extract_flat': False,
    'no_check_certificate': True,
    'prefer_insecure': True,
    'cookiefile': None,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    }
}

YDL_AUDIO = {
    **YDL_COMMON,
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',
    }],
}

# ============== SIMPLIFIED AUDIO FUNCTION ==============
async def download_audio(song_name):
    """Download audio from YouTube - Simplified and Reliable"""
    try:
        # Clean the song name
        song_name = song_name.strip()
        
        # Create search query
        search_query = f"ytsearch:{song_name} audio"
        
        print(f"Searching for: {song_name}")
        
        with yt_dlp.YoutubeDL(YDL_AUDIO) as ydl:
            # First, search and get info
            info = ydl.extract_info(search_query, download=False)
            
            # Check if we got results
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                video_url = video['webpage_url']
                
                print(f"Found: {video['title']}")
                
                # Now download the audio
                audio_info = ydl.extract_info(video_url, download=True)
                
                # Get the filename
                filename = ydl.prepare_filename(audio_info)
                filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                if os.path.exists(filename):
                    return {
                        'file': filename,
                        'title': audio_info.get('title', song_name),
                        'artist': audio_info.get('uploader', 'Unknown Artist'),
                        'duration': audio_info.get('duration', 0)
                    }
                else:
                    print(f"File not found: {filename}")
                    return None
            else:
                print("No results found")
                return None
                
    except Exception as e:
        print(f"Error in download_audio: {str(e)}")
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
            print(f"Cleaned up: {filepath}")
    except Exception as e:
        print(f"Cleanup error: {e}")

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
        "`/movie Inception 2010`\n"
        "`/watch Avengers 2019`\n\n"
        "⚡ *Bot is Active!*",
        parse_mode='Markdown'
    )

async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("❌ Usage: `/audio song name`\nExample: `/audio Golden Brown`", parse_mode='Markdown')
        return
    
    msg = await update.message.reply_text(f"🎵 Searching: `{query}`...\n⏳ Please wait (20-40 seconds)...")
    
    song = await download_audio(query)
    
    if not song or not os.path.exists(song['file']):
        await msg.edit_text(
            f"❌ Song not found: `{query}`\n\n"
            f"💡 Tips:\n"
            f"• Try: `/audio {query} song`\n"
            f"• Check spelling\n"
            f"• Try a different song\n\n"
            f"Example that works: `/audio Believer`"
        )
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
    print("✅ Bot starting...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running! Send /start on Telegram")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
