from datetime import datetime, timezone
import os
import asyncio
from random import randint
import random
import typing
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import discord
import traceback
from discord.ext import commands
from dotenv import load_dotenv
from discord import Embed, Interaction, app_commands
import requests
from cogs.ladder_admin_cog import LadderAdmin_cog
from cogs.ladder_betting_cog import Ladderbetting_cog
from data.helper_functions import *
import pytz
from pytz import UnknownTimeZoneError

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
set_bot_instance(bot)

@bot.tree.command(name="cog-load", description="Load a cog")
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

@bot.tree.command(name="cog-reload", description="Reload a co")
@commands.has_permissions(administrator=True)
async def reload(interaction, extension: typing.Literal["ladder_bot_cog", "vcGenerator_cog", "info_cog", "ladder_admin_cog", "ladder_betting_cog"]):
    await interaction.response.defer()
    await bot.reload_extension(f'cogs.{extension}')
    await log(f'Bot reloaded extension: cogs.{extension}')
    await interaction.followup.send(f"Bot reloaded extension: {extension}")

# Dictionary to map non-standard time zone names to valid pytz time zones
timezone_aliases = {
    "CEST": "Europe/Berlin",
    "PST": "US/Pacific",
    "PDT": "US/Pacific",
    "CST": "US/Central",
    # Add more custom mappings as needed
}

def localize_datetime(naive_datetime, timezone):
    # Convert the timezone alias to a valid timezone name if it exists
    timezone = timezone_aliases.get(timezone.upper(), timezone)

    # Get the pytz timezone object
    tz = pytz.timezone(timezone)
    
    # Localize the naive datetime
    return tz.localize(naive_datetime)

@bot.tree.command(name="timestamp", description="Generate a Discord timestamp")
@app_commands.describe(
    time="Time in HH:MM format (24-hour)",
    timezone="Your local timezone (e.g., 'UTC', 'America/New_York')",
    date="Date in YYYY-MM-DD format (default is today's date)"
)
async def timestamp(interaction: discord.Interaction, time: str, timezone: str, date: str = datetime.now().strftime("%Y-%m-%d")):
    try:
        # Parse the date and time
        naive_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        # Localize the naive datetime to the selected timezone
        localized_datetime = localize_datetime(naive_datetime, timezone)

        # Convert to UTC to get the UNIX timestamp
        utc_datetime = localized_datetime.astimezone(pytz.UTC)

        # Get the UNIX timestamp
        unix_timestamp = int(utc_datetime.timestamp())

        # Create the Discord timestamp string
        discord_timestamp = f"<t:{unix_timestamp}:F>"

        # Send the plain text message with the timestamp
        await interaction.response.send_message(
            f"The universal timestamp is: {discord_timestamp}."
        )
    except ValueError as e:
        await interaction.response.send_message(f"Error: {e}. Please use YYYY-MM-DD for date, HH:MM for time, and a valid timezone.")
    except UnknownTimeZoneError:
        await interaction.response.send_message(f"Invalid timezone '{timezone}'. Please provide a valid timezone name.")
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}")

@bot.event
async def on_ready():
    #await clearLogChannel()
    await load_cogs()

    #await temporaryWalletsFix(bot)

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

# This is for getting everybodies newest wallet amount if something breaks again (has the osrl ids)
""" async def temporaryWalletsFix(bot):
    commandChannel = 1098739590820540506
    channel = bot.get_channel(commandChannel)
    lostwallets = {}
    
    async for message in channel.history(limit=7000, oldest_first=False):
        if message.embeds:
            for embed in message.embeds:
                if embed.title == "Coins added":
                    # Get the interaction information
                    interaction_metadata = message.interaction_metadata
                    
                    if interaction_metadata and "**" in embed.description:
                        # Get the ID of the user who triggered the interaction
                        user_id = interaction_metadata.user.id
                        coins = embed.description.split("**")[1]

                        # Add to the lostwallets dictionary
                        if str(user_id) not in lostwallets:
                            lostwallets[str(user_id)] = coins

        elif "Your new balance is" in message.content and message.author.id == 1169606029844172932:
            coins = message.content.split(" new balance is ")[1].split(" ")[0]
            userId = message.content.split("<@")[1].split(">")[0]
            
            if userId not in lostwallets:
                lostwallets[userId] = coins

    for lostwallet in lostwallets:
        print(f"User ID: {lostwallet}, coins: {lostwallets[lostwallet]}")

    for lostwallet in lostwallets:
        username = await get_username(bot.get_guild(osrl_Server), lostwallet)
        print(f"Username: {username}, coins: {lostwallets[lostwallet]}") """


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
    # Check if the message is from the specific user (Bang: 547595456650412052, James: 697451352753963069)
    if message.author.id == 697451352753963069:
        # Check if the message is sent in the specific channel (General 1v1 discussion: 1063890145897615370, ISO Private: 1166508496578170951)
        if message.channel.id == 1166508496578170951:
            if randint(1, 1) == 1: 
                """ # Fetch insult from the API
                insult_api_url = 'https://evilinsult.com/generate_insult.php?lang=en&type=pirate'
                response = requests.get(insult_api_url)
                insult = response.text.strip() """

                if "<@&1083592526847545364>" in message.content: # Private Matches role ID: 1083592526847545364
                    replies = ["Maybe","Depends","I guess","Hmmm, I could partake","Perhaps","Possibly", "Perchance"]

                    # Reply with the insult
                    #await message.channel.send(f"{message.author.mention}, {insult}")
                    await asyncio.sleep(120)
                    await message.channel.send(f"{random.choice(replies)}", reference = message)

@bot.event
async def on_member_remove(member):
    # Find the player and remove them from the leaderboard
    for leaderboardEntry in leaderboard:
        if str(member.id) in leaderboardEntry:
            playerIndex = leaderboard.index(str(member.id))
            leaderboard.pop(playerIndex)

            writeToFile('leaderboard', leaderboard)

            # Remove the active challenge if one with the player is found
            for challenge in activeChallenges:
                if str(member.id) in challenge:
                    await Ladderbetting_cog.removeAllBetsFromChallenge(challenge=challenge, guild=member.guild, bot=bot)
                    activeChallenges.remove(challenge)
                    break
            writeToFile('activeChallenges', activeChallenges)
            
            await update_ladder(member.guild)
            channel = bot.get_channel(1063890145897615370) # General 1v1 discussion channel
            embed = discord.Embed(title="Player Left", description=f"Player **{member.display_name}** ({str(member.id)}) has been removed from the ladder due to leaving the server.", color=discord.Color.red())
            await log(f"Player {member.display_name} ({str(member.id)}) has been removed from the ladder due to leaving the server.")
            return await channel.send(embed=embed)
            break

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

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = f"An error occurred in {event}: {args} {kwargs}\n\n"
    error_message += traceback.format_exc() 
    await log(error_message, isError = True)

async def main():
    await bot.start(TOKEN)

asyncio.run(main())