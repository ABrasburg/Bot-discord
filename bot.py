# bot.py
import os
import asyncio
import threading
import http.server
import socketserver

import discord
from discord.ext import commands
import yt_dlp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN', '').strip('{}')
GUILD = os.getenv('DISCORD_GUILD', '').strip('{}')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Mantener vivo para Render
def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Servidor HTTP funcionando en el puerto {port}")
        httpd.serve_forever()

# Iniciar el hilo del servidor web
t = threading.Thread(target=keep_alive)
t.start()

@bot.event
async def on_ready():
    print(f'{bot.user} está conectado a:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

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
    print(f"Comando !play recibido con URL: {url}")  # Agregar log aquí
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

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'geo_bypass': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice:
        voice = await ctx.author.voice.channel.connect()

    ffmpeg_options = {
        'options': '-vn'
    }

    voice.play(
        discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
        after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop)
    )

    await ctx.send(f"▶️ Reproduciendo ahora: {info['title']}")


@bot.command()
async def queue(ctx):
    if not song_queue:
        await ctx.send("📭 La cola está vacía.")
        return
    message = "\n".join([f"{i+1}. {url}" for i, url in enumerate(song_queue)])
    await ctx.send(f"🎶 Cola de reproducción:\n{message}")

@bot.command(name='leave')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send('¡Me fui del canal de voz!')
    else:
        await ctx.send('No estoy en ningún canal de voz.')

# Iniciar el bot
bot.run(TOKEN)
