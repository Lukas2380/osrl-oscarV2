import os
import asyncio
from random import randint
import typing
import discord
import traceback
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands
import requests
from cogs.ladder_betting_cog import Ladderbetting_cog
from data.helper_functions import *

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
set_bot_instance(bot)

#! todo: https://www.reddit.com/r/discordapp/comments/11qy3s8/how_do_i_stop_people_from_adding_reactions_to_a/ tell catharticcup to do that on the roleselect channel 

@bot.tree.command(name="cog-load", description="Load a cog", )
@commands.has_permissions(administrator=True)
async def load(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog", "ladder_admin_cog", "ladder_betting_cog"]):
    await interaction.response.defer()
    await bot.load_extension(f'cogs.{extension}')
    await log(f'Bot loaded extension: {extension}')
    await interaction.followup.send(f"Bot loaded extension: {extension}")

@bot.tree.command(name="cog-unload", description="Unload a cog")
@commands.has_permissions(administrator=True)
async def unload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog", "ladder_admin_cog", "ladder_betting_cog"]):
    await interaction.response.defer()
    await bot.unload_extension(f'cogs.{extension}')
    await log(f'Bot unloaded extension: {extension}')
    await interaction.followup.send(f"Bot unloaded extension: {extension}")

@bot.tree.command(name="cog-reload", description="Reload a cog")
@commands.has_permissions(administrator=True)
async def reload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog", "ladder_admin_cog", "ladder_betting_cog"]):
    await interaction.response.defer()
    await bot.reload_extension(f'cogs.{extension}')
    await log(f'Bot reloaded extension: cogs.{extension}')
    await interaction.followup.send(f"Bot reloaded extension: {extension}")

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = f"An error occurred in {event}: {args} {kwargs}\n\n"
    error_message += traceback.format_exc()
    await log(error_message, isError = True)

@bot.event
async def on_ready():
    #await clearLogChannel()
    await load_cogs()
    
    await log(f'Logged in as {bot.user.name}')

    # Print all the bot's permissions in the server
    guild = bot.get_guild(osrl_Server)
    bot_permissions = guild.me.guild_permissions
    permissions_str = ", ".join([perm[0].replace("_", " ").capitalize() for perm in bot_permissions if perm[1]])
    await log(f"Bot's Permissions in the Server: {permissions_str}")

    try:
        await log("...Trying to sync the commands")
        synced = await bot.tree.sync()
        await log(f"Synced {len(synced)} command(s)")
    except Exception as e:
        await log("Couldnt load commands")
        
    bot.vc_generators = {}

async def clearLogChannel():
    guild = bot.get_guild(osrl_Server)
    channel = guild.get_channel(log_channel)
    await channel.purge(limit=1000)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            await log(f'-- Bot loaded {filename} on startup')

# Bang insultment corner #? todo: make it happen to the person who last lost a 1v1 ladder match
@bot.event
async def on_message(message):
    # Check if the message is from the specific user (Bang)
    if message.author.id == 547595456650412052:
        # Check if the message is sent in the specific channel (General 1v1 discussion)
        if message.channel.id == 1063890145897615370:
            if False: #randint(1, 10) == 1
                # Fetch insult from the API
                insult_api_url = 'https://evilinsult.com/generate_insult.php?lang=en&type=pirate'
                response = requests.get(insult_api_url)
                insult = response.text.strip()

                # Reply with the insult
                await message.channel.send(f"{message.author.mention}, {insult}")

@bot.event
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    try:
        if isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(f"You're missing permissions to use that", ephemeral=True)
        else:
            # Log the error
            error_message = f"An error occurred in command tree: {error}\n\n"
            error_message += traceback.format_exc()
            await log(error_message, isError = True)
    except Exception as e:
        await log(f"An error occurred while handling a command tree error: {e}", isError = True)
bot.tree.on_error = on_tree_error

async def main():
    await bot.start(TOKEN)

asyncio.run(main())