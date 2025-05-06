# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TOKEN = TOKEN.lstrip('{')
TOKEN = TOKEN.rstrip('}')
GUILD = os.getenv('DISCORD_GUILD')
GUILD = GUILD.lstrip('{')
GUILD = GUILD.rstrip('}')

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

client.run(TOKEN)