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
def download_audio(song_name):
    """Download audio from YouTube - Working version"""
    try:
        # Options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_audio': True,
            'audio_format': 'mp3',
            'audio_quality': '128',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search for the song
            search_query = f"ytsearch:{song_name}"
            info = ydl.extract_info(search_query, download=True)
            
            # Get the first result
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                
                # Get the filename
                base_filename = ydl.prepare_filename(video)
                mp3_filename = base_filename.rsplit('.', 1)[0] + '.mp3'
                
                # Check if file exists
                if os.path.exists(mp3_filename):
                    duration = video.get('duration', 0)
                    if duration:
                        minutes = duration // 60
                        seconds = duration % 60
                        duration_str = f"{minutes}:{seconds:02d}"
                    else:
                        duration_str = "Unknown"
                    
                    return {
                        'file': mp3_filename,
                        'title': video.get('title', song_name),
                        'artist': video.get('uploader', 'Unknown'),
                        'duration': duration_str,
                        'duration_seconds': duration
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
        "🎵 *✨ MUSIC & MOVIE BOT ✨*\n\n"
        "*🎵 COMMANDS:*\n"
        "`/play song name` - Download MP3 audio\n\n"
        "*🎬 MOVIE COMMANDS:*\n"
        "`/movie name year` - Movie info + poster\n"
        "`/watch name year` - HD streaming links\n\n"
        "*📝 EXAMPLES:*\n"
        "`/play Golden Brown`\n"
        "`/play Believer`\n"
        "`/movie Inception 2010`\n"
        "`/watch Avengers 2019`\n\n"
        "⚡ *Bot is Active!*\n"
        "⏳ *Please wait 30-60 seconds for audio*",
        parse_mode='Markdown'
    )

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download and send audio"""
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text(
            "❌ *Usage:* `/play song name`\n"
            "*Example:* `/play Golden Brown`\n"
            "*Example:* `/play Believer`",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        f"🎵 *Searching & Downloading:* `{query}`...\n"
        f"⏳ *Please wait 30-60 seconds...*",
        parse_mode='Markdown'
    )
    
    # Download audio
    result = download_audio(query)
    
    if not result or not os.path.exists(result['file']):
        await status_msg.edit_text(
            f"❌ *Song not found:* `{query}`\n\n"
            f"💡 *Try these:*\n"
            f"• `/play {query} song`\n"
            f"• `/play {query} audio`\n"
            f"• `/play {query} official`\n\n"
            f"✅ *Working examples:*\n"
            f"• `/play Believer`\n"
            f"• `/play Shape of You`\n"
            f"• `/play Blinding Lights`",
            parse_mode='Markdown'
        )
        return
    
    file_size = os.path.getsize(result['file']) / (1024 * 1024)
    
    await status_msg.edit_text(
        f"📤 *Uploading...* ({file_size:.1f} MB)\n"
        f"⏳ *Please wait...*",
        parse_mode='Markdown'
    )
    
    try:
        # Send the audio file
        with open(result['file'], 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=result['title'][:100],
                performer=result['artist'],
                duration=result['duration_seconds'],
                caption=f"🎵 *{result['title'][:50]}*\n"
                       f"👤 *Artist:* {result['artist']}\n"
                       f"⏱️ *Duration:* {result['duration']}\n"
                       f"📦 *Size:* {file_size:.1f} MB",
                parse_mode='Markdown'
            )
        
        await status_msg.delete()
        cleanup(result['file'])
        
    except Exception as e:
        await status_msg.edit_text(f"❌ *Error:* {str(e)[:200]}", parse_mode='Markdown')
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
        f"📺 *Watch:* `/watch {movie['title']} {movie['year']}`"
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
    print(f"Bot Token: {TELEGRAM_TOKEN[:15]}...")
    print(f"Download folder: {DOWNLOAD_FOLDER}")
    print("=" * 50)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("movie", movie_command))
    app.add_handler(CommandHandler("watch", watch_command))
    
    print("✅ Bot is running! Send /start on Telegram")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
