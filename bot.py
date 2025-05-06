# bot.py
import os

import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TOKEN = TOKEN.lstrip('{')
TOKEN = TOKEN.rstrip('}')
GUILD = os.getenv('DISCORD_GUILD')
GUILD = GUILD.lstrip('{')
GUILD = GUILD.rstrip('}')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Entré al canal de voz: {channel.name}')
    else:
        await ctx.send('¡Tenés que estar en un canal de voz!')

song_queue = []
MAX_QUEUE_SIZE = 10
@bot.command(name='play')
async def play(ctx, url):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    if len(song_queue) >= MAX_QUEUE_SIZE:
        await ctx.send("❌ La cola está llena (máximo 10 canciones).")
        return

    song_queue.append(url)

    if not voice or not voice.is_playing():
        await play_next_song(ctx)
    else:
        await ctx.send(f"🎵 Se agregó a la cola: {url}")

async def play_next_song(ctx):
    if len(song_queue) == 0:
        await ctx.send("✅ La cola ha terminado.")
        return

    url = song_queue.pop(0)

    # Descargar y reproducir (usa tu código de yt_dlp aquí)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

    voice = await ctx.author.voice.channel.connect() if not discord.utils.get(bot.voice_clients, guild=ctx.guild) else discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio(filename), after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop))

    await ctx.send(f"▶️ Reproduciendo ahora: {info['title']}")

@bot.command(name='leave')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send('¡Me fui del canal de voz!')
    else:
        await ctx.send('No estoy en ningún canal de voz.')

bot.run(TOKEN)