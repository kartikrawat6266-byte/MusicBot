import discord
from discord.ext import commands
from discord.ui import Button, View
import yt_dlp as youtube_dl
import asyncio
import aiohttp
from youtubesearchpython import VideosSearch
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ============== PREMIUM SETUP ==============
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Premium Colors
COLORS = {
    'music': 0x1DB954,     # Spotify Green
    'video': 0xFF0000,     # YouTube Red
    'movie': 0xFFD700,     # Gold
    'info': 0x00B4D8,      # Blue
    'error': 0xFF3366,     # Red
    'success': 0x00FF88    # Green
}

# Audio Setup
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_AUDIO = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': False
}

YDL_VIDEO = {
    'format': 'best[height<=1080]',
    'noplaylist': True,
    'quiet': True
}

# Queue System
queues = {}

# TMDB API (Free - Get from themoviedb.org)
TMDB_API_KEY = os.getenv('TMDB_API_KEY', 'your_key_here')
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# ============== PREMIUM EMBED FUNCTION ==============
def premium_embed(title, description, color, thumbnail=None, image=None):
    embed = discord.Embed(
        title=f"✨ {title} ✨",
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="🎬 Ultimate Entertainment Bot • Premium Quality")
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    return embed

# ============== SONG FUNCTIONS (AUDIO) ==============
async def get_song_audio(query):
    """Get audio stream URL from song name"""
    with youtube_dl.YoutubeDL(YDL_AUDIO) as ydl:
        try:
            if query.startswith('http'):
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            
            return {
                'url': info['url'],
                'title': info['title'],
                'artist': info.get('uploader', 'Unknown Artist'),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'video_url': f"https://youtube.com/watch?v={info['id']}"
            }
        except Exception as e:
            print(f"Audio Error: {e}")
            return None

async def play_next(ctx, server_id):
    if queues.get(server_id) and queues[server_id]:
        song = queues[server_id].pop(0)
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, server_id), bot.loop)
        )
        embed = premium_embed(
            "🎵 NOW PLAYING",
            f"**{song['title']}**\n👤 {song['artist']}\n⏱️ `{song['duration']//60}:{song['duration']%60:02d}`",
            COLORS['success'],
            thumbnail=song['thumbnail']
        )
        await ctx.send(embed=embed)

# ============== SONG FUNCTIONS (VIDEO) ==============
async def get_song_video(query):
    """Get video URL from song name"""
    with youtube_dl.YoutubeDL(YDL_VIDEO) as ydl:
        try:
            if query.startswith('http'):
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            
            return {
                'title': info['title'],
                'url': info['webpage_url'],
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'quality': info.get('resolution', '1080p')
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
                    'poster': f"https://image.tmdb.org/t/p/w500{details.get('poster_path', '')}" if details.get('poster_path') else None,
                    'backdrop': f"https://image.tmdb.org/t/p/original{details.get('backdrop_path', '')}" if details.get('backdrop_path') else None
                }

async def get_movie_video(movie_id, movie_title, year):
    """Get streaming links for movie"""
    streams = [
        f"🎬 **VidSrc (4K/1080p)**\n🔗 https://vidsrc.to/embed/movie/{movie_id}\n",
        f"🎥 **2Embed (1080p)**\n🔗 https://www.2embed.to/embed/tmdb/movie/{movie_id}\n",
        f"📺 **MovieWeb (HD)**\n🔗 https://movie-web.app/movie/{movie_id}\n"
    ]
    
    # Also search YouTube for full movie
    search = VideosSearch(f"{movie_title} {year} full movie", limit=2)
    results = search.result()
    
    youtube_links = []
    for video in results.get('result', []):
        duration = video.get('duration', '0:00')
        if 'hour' in video.get('title', '').lower() or ':' in duration and len(duration.split(':')) >= 2:
            youtube_links.append(f"📺 **YouTube**\n🔗 {video['link']}\n📹 {video['duration']}\n")
    
    return streams, youtube_links

# ============== INTERACTIVE BUTTONS ==============
class SongButtons(View):
    def __init__(self, song_data):
        super().__init__(timeout=60)
        self.song_data = song_data
    
    @discord.ui.button(label="🎵 PLAY AUDIO", style=discord.ButtonStyle.success, emoji="🔊")
    async def audio_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = premium_embed(
            "🎵 AUDIO COMMAND",
            f"Use `!play {self.song_data['title'][:50]}` to play in voice channel!\n\n💡 First join a voice channel, then use the command.",
            COLORS['music'],
            thumbnail=self.song_data['thumbnail']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📺 WATCH VIDEO", style=discord.ButtonStyle.primary, emoji="🎥")
    async def video_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = premium_embed(
            f"🎬 {self.song_data['title'][:50]}",
            f"**Watch on YouTube:**\n🔗 {self.song_data['video_url']}\n\n📺 Quality: `1080p HD`\n👤 Uploader: `{self.song_data['artist']}`\n👁️ Views: `{self.song_data['views']:,}`",
            COLORS['video'],
            thumbnail=self.song_data['thumbnail']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MovieButtons(View):
    def __init__(self, movie_id, movie_title, year):
        super().__init__(timeout=60)
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.year = year
    
    @discord.ui.button(label="🎬 WATCH MOVIE", style=discord.ButtonStyle.primary, emoji="🎥")
    async def watch_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        streams, youtube_links = await get_movie_video(self.movie_id, self.movie_title, self.year)
        
        description = "**🎥 STREAMING SOURCES (4K/1080p):**\n\n" + "\n".join(streams)
        if youtube_links:
            description += "\n**📺 YOUTUBE (Full Movie):**\n\n" + "\n".join(youtube_links[:2])
        
        embed = premium_embed(
            f"📺 {self.movie_title} ({self.year}) - WATCH ONLINE",
            description[:4000],
            COLORS['movie']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ============== BOT COMMANDS ==============

@bot.event
async def on_ready():
    print(f'✅ ULTIMATE BOT ONLINE!')
    print(f'🤖 {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="🎵 Songs & Movies"))

# ----- SONG AUDIO COMMAND -----
@bot.command(name='play', aliases=['p', 'audio'])
async def play_audio(ctx, *, query):
    """🎵 Play song audio in voice channel - !play song name"""
    
    if not ctx.author.voice:
        embed = premium_embed("❌ ERROR", "Join a voice channel first!", COLORS['error'])
        await ctx.send(embed=embed)
        return
    
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)
    
    loading = await ctx.send(embed=premium_embed("🔍 SEARCHING", f"Looking for `{query}`...", COLORS['info']))
    
    song = await get_song_audio(query)
    
    if not song:
        await loading.edit(embed=premium_embed("❌ ERROR", "Song not found!", COLORS['error']))
        return
    
    server_id = ctx.guild.id
    if server_id not in queues:
        queues[server_id] = []
    
    if not ctx.voice_client.is_playing():
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx, server_id), bot.loop)
        )
        await loading.delete()
        embed = premium_embed(
            "🎵 NOW PLAYING",
            f"**{song['title']}**\n👤 `{song['artist']}`\n⏱️ `{song['duration']//60}:{song['duration']%60:02d}`\n❤️ `{song['likes']:,}` likes",
            COLORS['success'],
            thumbnail=song['thumbnail']
        )
        await ctx.send(embed=embed, view=SongButtons(song))
    else:
        queues[server_id].append(song)
        await loading.edit(embed=premium_embed(
            "📝 ADDED TO QUEUE",
            f"**{song['title']}**\n📌 Position: `{len(queues[server_id])}`",
            COLORS['info']
        ))

# ----- SONG VIDEO COMMAND -----
@bot.command(name='video', aliases=['v', 'watchsong'])
async def song_video(ctx, *, query):
    """📺 Get song video link - !video song name"""
    
    loading = await ctx.send(embed=premium_embed("🔍 SEARCHING", f"Finding video for `{query}`...", COLORS['info']))
    
    video = await get_song_video(query)
    
    if not video:
        await loading.edit(embed=premium_embed("❌ ERROR", "Video not found!", COLORS['error']))
        return
    
    await loading.delete()
    
    duration = f"{video['duration']//60}:{video['duration']%60:02d}" if video['duration'] else "Unknown"
    
    embed = premium_embed(
        f"🎬 {video['title'][:100]}",
        f"**📺 Watch in High Quality:**\n🔗 {video['url']}\n\n"
        f"**Details:**\n⏱️ Duration: `{duration}`\n👤 Uploader: `{video['uploader']}`\n👁️ Views: `{video['views']:,}`\n❤️ Likes: `{video['likes']:,}`\n📹 Quality: `{video['quality']}`",
        COLORS['video'],
        thumbnail=video['thumbnail']
    )
    
    # Add audio option button
    view = View()
    audio_btn = Button(label="🎵 PLAY AUDIO ONLY", style=discord.ButtonStyle.success, emoji="🔊", custom_id="audio")
    
    async def audio_callback(interaction):
        embed2 = premium_embed(
            "🎵 AUDIO COMMAND",
            f"Use `!play {video['title'][:50]}` to play audio in voice channel!",
            COLORS['music']
        )
        await interaction.response.send_message(embed=embed2, ephemeral=True)
    
    audio_btn.callback = audio_callback
    view.add_item(audio_btn)
    
    await ctx.send(embed=embed, view=view)

# ----- MOVIE INFO + VIDEO COMMAND -----
@bot.command(name='movie', aliases=['film', 'm'])
async def movie_info(ctx, *, query):
    """🎬 Get movie info + watch links - !movie name year"""
    
    parts = query.rsplit(' ', 1)
    year = None
    movie_name = query
    
    if len(parts) > 1 and parts[1].isdigit() and 1900 <= int(parts[1]) <= 2026:
        year = parts[1]
        movie_name = parts[0]
    
    loading = await ctx.send(embed=premium_embed("🔍 SEARCHING", f"Finding `{movie_name}`...", COLORS['info']))
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await loading.edit(embed=premium_embed("❌ ERROR", "Movie not found! Try different name.", COLORS['error']))
        return
    
    await loading.delete()
    
    embed = premium_embed(
        f"🎬 {movie['title']} ({movie['year']})",
        f"*{movie['overview'][:300]}...*\n\n"
        f"⭐ **Rating:** `{movie['rating']}/10` {movie['stars']}\n"
        f"⏱️ **Runtime:** `{movie['runtime']}` min\n"
        f"🎭 **Genres:** `{'`, `'.join(movie['genres'][:3])}`\n"
        f"📅 **Released:** `{movie['year']}`",
        COLORS['movie'],
        thumbnail=movie['poster'],
        image=movie['backdrop']
    )
    
    view = MovieButtons(movie['id'], movie['title'], movie['year'])
    await ctx.send(embed=embed, view=view)

# ----- MOVIE ONLY WATCH COMMAND -----
@bot.command(name='watch', aliases=['w', 'stream'])
async def movie_watch(ctx, *, query):
    """📺 Get direct movie streaming links - !watch movie name year"""
    
    parts = query.rsplit(' ', 1)
    year = None
    movie_name = query
    
    if len(parts) > 1 and parts[1].isdigit():
        year = parts[1]
        movie_name = parts[0]
    
    loading = await ctx.send(embed=premium_embed("🔍 SEARCHING", f"Getting streaming links for `{movie_name}`...", COLORS['info']))
    
    movie = await get_movie_info(movie_name, year)
    
    if not movie:
        await loading.edit(embed=premium_embed("❌ ERROR", "Movie not found!", COLORS['error']))
        return
    
    streams, youtube_links = await get_movie_video(movie['id'], movie['title'], movie['year'])
    
    await loading.delete()
    
    description = "**🎥 HD STREAMING LINKS (4K/1080p):**\n\n" + "\n".join(streams)
    if youtube_links:
        description += "\n**📺 YOUTUBE FULL MOVIE:**\n\n" + "\n".join(youtube_links)
    
    embed = premium_embed(
        f"📺 {movie['title']} ({movie['year']}) - WATCH ONLINE",
        description[:4000],
        COLORS['video'],
        thumbnail=movie['poster']
    )
    
    await ctx.send(embed=embed)

# ----- QUEUE COMMANDS -----
@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send(embed=premium_embed("⏭️ SKIPPED", "Current song skipped!", COLORS['info']))

@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send(embed=premium_embed("⏸️ PAUSED", "Use `!resume` to continue", COLORS['info']))

@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send(embed=premium_embed("▶️ RESUMED", "Playback continued", COLORS['success']))

@bot.command(name='stop', aliases=['dc'])
async def stop(ctx):
    if ctx.voice_client:
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
        await ctx.voice_client.disconnect()
        await ctx.send(embed=premium_embed("👋 DISCONNECTED", "Queue cleared! Bye bye!", COLORS['success']))

@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    server_id = ctx.guild.id
    if server_id not in queues or not queues[server_id]:
        await ctx.send(embed=premium_embed("📭 QUEUE EMPTY", "No songs in queue!", COLORS['info']))
        return
    
    queue_list = queues[server_id][:10]
    queue_text = "\n".join([f"{i+1}. {song['title'][:50]}" for i, song in enumerate(queue_list)])
    
    await ctx.send(embed=premium_embed("📋 SONG QUEUE", queue_text, COLORS['info']))

# ----- HELP COMMAND -----
@bot.command(name='help', aliases=['h', 'commands'])
async def help_command(ctx):
    embed = premium_embed(
        "🎯 ULTIMATE BOT - ALL COMMANDS",
        "**🎵 SONG COMMANDS**\n"
        "`!play <song>` - Play audio in voice channel\n"
        "`!video <song>` - Get YouTube video link\n\n"
        
        "**🎬 MOVIE COMMANDS**\n"
        "`!movie <name> <year>` - Get info + watch links\n"
        "`!watch <name> <year>` - Direct streaming links\n\n"
        
        "**🎮 QUEUE CONTROLS**\n"
        "`!skip` - Skip current song\n"
        "`!pause/resume` - Playback control\n"
        "`!stop` - Stop and disconnect\n"
        "`!queue` - Show queue\n\n"
        
        "**📋 EXAMPLES**\n"
        "`!play Believer` - Audio only\n"
        "`!video Believer` - Video link\n"
        "`!movie Inception 2010` - Movie info\n"
        "`!watch Avengers 2019` - Direct stream",
        COLORS['success']
    )
    await ctx.send(embed=embed)

# ============== RUN BOT ==============
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERROR: Set DISCORD_TOKEN in .env file!")
    else:
        bot.run(TOKEN)
