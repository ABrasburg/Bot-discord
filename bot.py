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

@bot.command(name='play')
async def play(ctx, url):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice or not voice.is_connected():
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send('Tenés que estar en un canal de voz.')
            return

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        source = discord.FFmpegPCMAudio("song.mp3")
        voice.play(source)

    await ctx.send(f'Reproduciendo: {info["title"]}')

@bot.command(name='leave')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send('¡Me fui del canal de voz!')
    else:
        await ctx.send('No estoy en ningún canal de voz.')

bot.run(TOKEN)