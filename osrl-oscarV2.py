import os
import asyncio
import typing
import discord
import traceback
from discord.ext import commands
from dotenv import load_dotenv
from discord import app_commands
from data.helper_functions import *

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
set_bot_instance(bot)

@bot.tree.command(name="load", description="Load a cog")
async def load(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await interaction.response.defer()
    await bot.load_extension(f'cogs.{extension}')
    await log(f'Bot loaded extension: {extension}')
    await interaction.followup.send(f"Bot loaded extension: {extension}")

@bot.tree.command(name="unload", description="Unload a cog")
async def unload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await interaction.response.defer()
    await bot.unload_extension(f'cogs.{extension}')
    await log(f'Bot unloaded extension: {extension}')
    await interaction.followup.send(f"Bot unloaded extension: {extension}")

@bot.tree.command(name="reload", description="Reload a cog")
async def reload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog"]):
    await interaction.response.defer()
    await bot.reload_extension(f'cogs.{extension}')
    await log(f'Bot reloaded extension: cogs.{extension}')
    await interaction.followup.send(f"Bot reloaded extension: {extension}")

@bot.event
async def on_error(event, *args, **kwargs):
    try:
        error_message = f"An error occurred in {event}: {args} {kwargs}\n\n"
        error_message += traceback.format_exc()
        await log(error_message, isError = True)
    except Exception as e:
        await log(f"An error occurred while handling a command tree error: {e}")

@bot.event
async def on_ready():
    await clearLogChannel()
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
        
    bot.vc_generators = {
        bot.get_channel(1150003078796415055): "`s general VC" #todo:remove this testing thing
    }

async def clearLogChannel():
    guild = bot.get_guild(979020400765841462)
    channel = guild.get_channel(1199387324904112178)
    await channel.purge()

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            await log(f'-- Bot loaded {filename} on startup')

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