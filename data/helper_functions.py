import re
import socket
import typing
import discord
import os
from supabase import create_client 
from dotenv import load_dotenv

load_dotenv()
url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Define references to each table
usersTable = supabase.table("users")
infoChannelsTable = supabase.table("info_channels")
vcGeneratorsTable = supabase.table("vcGenerators")
temporaryVCTable = supabase.table("temporaryVC")
leaderboardTable = supabase.table("leaderboard")
activeChallengesTable = supabase.table("activeChallenges")
lockedPlayersTable = supabase.table("lockedPlayers")
cooldownsTable = supabase.table("cooldowns")
statsTable = supabase.table("stats")
betsTable = supabase.table("bets")
walletsTable = supabase.table("wallets")

red = 0xFF5733
blue = 0x0CCFFF
green = 0x73ff00
infoEmbedColor = 0x03fc0b

osrl_Server = None # This is the OSRL Server ID
log_channel = None # This is the id of the log channel in the OSRL Server
ladder_channel = None # This is the id of the ladder channel in the OSRL Server

if (socket.gethostname() == "Lukas-Desktop" or socket.gethostname() == "Lukas-Laptop"):
    osrl_Server = 1150003077961756706
    log_channel = 1212470152000442429
    ladder_channel = 1212470890172780615
else:
    osrl_Server = 979020400765841462
    log_channel = 1199387324904112178
    ladder_channel = 1193288442260488402

bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

async def log(output: str, isError: bool = False):
    global bot_instance
    
    if bot_instance is None:
        raise ValueError("Bot instance not set. Call set_bot_instance with a valid bot instance.")

    guild = bot_instance.get_guild(osrl_Server)
    channel = guild.get_channel(log_channel)
    
    if isError:
        output = f"```Error``` \n<@381063088842997763>: \n ``` {output}```"
    else:
        output = f"```{output}```"
    
    await channel.send(output)

async def update_ladder(guild):
        channel = guild.get_channel(ladder_channel)

        if channel:
            # Find and delete the previous message and remove it
            async for message in channel.history(limit=3):
                if message.author == guild.me:
                    if message.content.startswith('>>>'):
                        await message.delete()
            
            # Send the active Challenges and current ladder
            await channel.send(await get_activeChallenges(guild))
            await channel.send(await get_ladder(guild))
            await channel.send(await get_wallets(guild))

        else:
            await log("Error: Channel not found.", isError=True)

async def get_activeChallenges(guild):
    # Standard output if no active challenges are found
    active_challenges = "No active challenges"

    # Your logic here to fetch and process active challenges

    return f">>> ## Active Challenges: \n### **First Player vs Second Player **\n ```ansi\n{active_challenges}```"

async def get_ladder(guild):
    # Standard output if no leaderboard data is available
    ladder_table = "No one on the ladder"

    # Your logic here to fetch and process the leaderboard

    return f">>> ## Current Ladder: \n ### **Rank ⚔️ Player **\n ```ansi\n{ladder_table}```"

async def get_wallets(guild):
    # Standard output if no wallet data is available
    walletOutput = "No wallets found"

    # Your logic here to fetch and process wallets

    return f">>> ## Wallets Leaderboard: \n### ** Coins | Name **\n ```ansi\n{walletOutput}```"

async def assign_mr_moneybags_role(guild):
    # Logic to reset or clear the "Mr. Moneybags" role assignment if needed
    return None  # Return None or appropriate value if necessary


def coloriseString(input: str, color: str): #typing.Literal["grey", "red", "green", "gold", "blue", "pink", "cyan", "white"]
    match color:
        case "grey":
            output = f"[2;30m{input}[0m"
        case "red":
            output = f"[2;31m{input}[0m"
        case "green":
            output = f"[2;32m{input}[0m"
        case "gold":
            output = f"[2;33m{input}[0m"
        case "blue":
            output = f"[2;34m{input}[0m"
        case "pink":
            output = f"[2;35m{input}[0m"
        case "cyan":
            output = f"[2;36m{input}[0m"
        case "white":
            output = f"[2;37m{input}[0m"
        case _:
            output = input

    return output

async def get_user_id(guild, person):
    userID = None

    try:
        if isinstance(person, (discord.Member, discord.User)):
            userID = person.id
        elif isinstance(person, str):
            if person.startswith("<@") and person.endswith(">"):
                person = person.strip("<@!>")
            userID = int(person)
        else:
            raise ValueError("Invalid person type")

        # Insert or update user in users table
        if userID:
            try:
                usersTable.upsert({"user_id": userID}, on_conflict=["user_id"]).execute()
                
                username = await get_username(guild, userID)
                if username:
                    usersTable.update({"user_name": username}).eq("user_id", userID).execute()

            except Exception as e:
                print(f"Error executing SQL operation: {e}")
    
    except Exception as e:
        print(f"Error fetching user ID: {e}")

    return str(userID)

async def get_username(guild, person):
    try:
        username = guild.get_member(int(person)).display_name
    except:
        username = f"no name found for: {person}"
        await log(f'Error while trying to get the username of one of these users: {person}', isError=True)

    return username



async def initialiseDatabasefromTextfiles():
    await log(f'Initialising database from textfiles')

    # SetChannels
    await log("Info Channels...")
    with open("./data/info/setchannels.txt", "r") as file:
        for line in file:
            channelName, channelID = line.split("=")
            infoChannelsTable.upsert({"channel_name": channelName, "channel_id": channelID}).execute()

    # Info Text
    await log("Info Text...")
    for filename in os.listdir('./data/info'):
        if filename.endswith('.txt') and filename != "setchannels.txt":
            text = open('./data/info/' + filename).read()
            filename = filename.removesuffix(".txt")
            channel_name = filename
            
            infoChannelsTable.update({"info_text": text}).eq("channel_name", channel_name).execute()
    return