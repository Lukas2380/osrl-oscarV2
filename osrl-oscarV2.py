import os
import asyncio
import typing
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.tree.command(name="load", description="Load a cog")
async def load(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await bot.load_extension(f'cogs.{extension}')
    print(f'Bot loaded extension: {extension}')
    await interaction.response.send_message(f"Bot loaded extension: {extension}")

@bot.tree.command(name="unload", description="Unload a cog")
async def unload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await bot.unload_extension(f'cogs.{extension}')
    print(f'Bot unloaded extension: {extension}')
    await interaction.response.send_message(f"Bot unloaded extension: {extension}")

@bot.tree.command(name="reload", description="Reload a cog")
async def reload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await bot.reload_extension(f'cogs.{extension}')
    print(f'Bot reloaded extension: cogs.{extension}')
    await interaction.response.send_message(f"Bot reloaded extension: {extension}")

@bot.event
async def on_connect(): 
    await load_cogs()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        print("...Trying to sync the commands")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print("Couldnt load commands")
        
    bot.vc_generators = {
        bot.get_channel(1150003078796415055): "`s general VC"
    } # Initialize an empty dictionary to store VC generators

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'-- Bot loaded {filename} on startup')

async def main():
    await bot.start(TOKEN)

asyncio.run(main())