import re
import socket
import typing
import discord
import os
from supabase import create_client

def connect_Supabase(url, key):
    global supabase
    supabase = create_client(url, key)

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

def load_data():
    # Read files and initialize a list for each one
    with open('./data/ladder/leaderboard.txt','r+') as file:
        data = file.read()
        leaderboard = data.split('\n')
        leaderboard.pop(-1)

    with open('./data/ladder/activeChallenges.txt','r+') as file:
        data = file.read()
        activeChallenges = data.split('\n')
        activeChallenges.pop(-1)

    with open('./data/ladder/lockedPlayers.txt','r+') as file:
        data = file.read()
        locked_players = data.split('\n')
        locked_players.pop(-1)

    with open('./data/ladder/stats.txt','r+') as file:
        data = file.read()
        stats = data.split('\n')
        stats.pop(-1)

    with open('./data/ladder/streaksLeaderboard.txt', 'r+') as file:
        data = file.read()
        streaksLeaderboard = data.split('\n')
        streaksLeaderboard.pop(-1)

    with open('./data/ladder/cooldowns.txt', 'r+') as file:
        data = file.read()
        cooldowns = data.split('\n')
        cooldowns.pop(-1)

    with open('./data/ladder/bets.txt', 'r+') as file:
        data = file.read()
        bets = data.split('\n')
        bets.pop(-1)

    with open('./data/ladder/wallets.txt', 'r+') as file:
        data = file.read()
        wallets = data.split('\n')
        wallets.pop(-1)

    with open('./data/ladder/wallets_activityBonusMessages.txt', 'r+') as file:
        data = file.read()
        activityBonusMessages = {}
        for line in data.split('\n'):
            if line != "":
                activityBonusMessages[line.split(' - ')[0]] = int(line.split(' - ')[1])

    with open('./data/ladder/wallets_activityBonusVCTime.txt', 'r+') as file:
        data = file.read()
        activityBonusVCTime = {}
        for line in data.split('\n'):
            if line != "":
                activityBonusVCTime[line.split(' - ')[0]] = int(line.split(' - ')[1])

    with open('./data/ladder/claimcoins_cooldown.txt', 'r+') as file:
        data = file.read()
        claimcoinsCooldown = {}
        for line in data.split('\n'):
            if line != "":
                claimcoinsCooldown[line.split(' - ')[0]] = line.split(' - ')[1]

    return leaderboard, activeChallenges, locked_players, stats, streaksLeaderboard, cooldowns, bets, wallets, activityBonusMessages, activityBonusVCTime, claimcoinsCooldown

leaderboard, activeChallenges, locked_players, stats, streaksLeaderboard, cooldowns, bets, wallets, activityBonusMessages, activityBonusVCTime, claimcoinsCooldown = load_data()

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

def writeToFile(file: str, mylist: list):
    with open(f'./data/ladder/{file}.txt', "w") as file:
        for entry in mylist:
            file.write(entry+'\n')

def writeDictToFile(file: str, myDict: dict):
    with open(f'./data/ladder/{file}.txt', "w") as file:
        for person, extraWallet in myDict.items():
            file.write(f"{person} - {extraWallet}\n")

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
        # Standard output if no one is on the active challenges list
        active_challenges = "No active challenges"
        
        if len(activeChallenges) > 0:
            # Clear the output and write the active challenges
            active_challenges = ""

            # Get the Mr. Moneybags
            highest_wallet = -float('inf')
            mr_moneybags = None
            
            # Iterate through wallets list to find the user with the highest wallet
            for wallet in wallets:
                user_id, user_wallet = wallet.split(" - ")
                user_wallet = int(user_wallet)
                if user_wallet > highest_wallet:
                    highest_wallet = user_wallet
                    mr_moneybags = user_id

            for challenge in activeChallenges:
                    symbol = "⚔️"
                    firstPlayerColor = "red"
                    secondPlayerColor = "red"
                    # Get the playernames, playerpositions and usernames of the players
                    firstPlayerID, secondPlayerID, date, isGuardianChal  = challenge.split(" - ") # ignore the date and if it is a guardian challenge 
                    ##firstPlayerPosition = leaderboard.index(firstPlayer) + 1 # !for positioning if wanted
                    firstPlayer = await get_username(guild, firstPlayerID)
                    secondPlayer = await get_username(guild, secondPlayerID)

                    if mr_moneybags == firstPlayerID:
                        firstPlayerColor = "green"
                    elif mr_moneybags == secondPlayerID:
                        secondPlayerColor = "green"

                    if isGuardianChal == "true":
                        symbol = "🗡️"
                        secondPlayerColor = "blue"

                    if secondPlayerID in leaderboard[0]:
                        secondPlayerColor = "gold"

                    if len(firstPlayer+secondPlayer) > 34: # This is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayer = firstPlayer[:17]
                        secondPlayer = secondPlayer[:17]

                    firstPlayer = coloriseString(firstPlayer, firstPlayerColor)
                    secondPlayer = coloriseString(secondPlayer, secondPlayerColor)

                    # Write and format the active challenges
                    active_challenges += f"{date}: {firstPlayer}{' '* (14 - len(firstPlayer))} {symbol} {secondPlayer}{' '* (14 - len(secondPlayer))}\n"
        
        return(f">>> ## Active Challenges: \n### **First Player vs Second Player **\n ```ansi\n{active_challenges}```")


async def get_ladder(guild):
        # Standard output if no one is on the ladder
        ladder_table = 'No one on the ladder'

        if len(leaderboard) > 0:
            # Clear the output and write the ladder
            ladder_table = ""
            rank = 0
            mr_moneybags = await assign_mr_moneybags_role(guild)

            for person in leaderboard:
                symbol = ''
                rank += 1

                # Write and format the ladder
                username = await get_username(guild, person)
                makeColor = ""

                # Check if the person is in the activeChallenges list
                for element in activeChallenges:
                    # Different symbol if they are in a guardian challenge (element.split(" - "):  first person is the attacker, second the defender)
                    if person in element.split(" - ")[0]:
                        makeColor = "red"
                        if element.split(" - ")[3] == "true":
                            symbol = "🗡️"
                        else:
                            symbol = "⚔️"
                    elif person in element.split(" - ")[1]:
                        makeColor = "red"
                        if element.split(" - ")[3] == "true":
                            symbol = "🗡️"
                        else:
                            symbol = "⚔️"

                lst = [3] + [i for i in range(5, len(leaderboard)+1, 5)]
                if (leaderboard.index(person) + 1) in lst:
                    symbol += "🛡️"
                    makeColor = "blue"

                if person == mr_moneybags:
                    symbol += "💰"
                    makeColor = "green"

                if rank == 1:
                    symbol += "👑"
                    makeColor = "gold"

                username = coloriseString(username, makeColor)

                if symbol != "":
                    symbol = f"[{symbol}]"

                ladder_table += "{:>}. {} {:<}\n".format(rank, symbol, username)

        return(f">>> ## Current Ladder: \n ### **Rank ⚔️ Player **\n ```ansi\n{ladder_table}```")

async def get_wallets(guild):
    walletOutput = "No wallets found"

    if len(wallets) > 0:
        walletOutput = ""
        # Step 1: Split the list and sort by coins in descending order
        sorted_wallets = sorted((entry.split(' - ') for entry in wallets if str(bot_instance.user.id) not in entry), key=lambda x: int(x[1]), reverse=True)
        # Step 3: Take top 20 entries
        top_20_wallets = sorted_wallets[:20]
        # Step 4: Format the output string
        for userId, coins in top_20_wallets:
            username = await get_username(guild, userId)
            if userId in top_20_wallets[0] and userId in leaderboard[0]:
                username = "[👑💰] " + coloriseString(username, "green")
            elif userId in top_20_wallets[0]:
                username = "[💰] " + coloriseString(username, "green")
            elif userId in leaderboard[0]:
                username = "[👑] " + coloriseString(username, "gold")
            walletOutput += "{:<6} | {}\n".format(coins, username)

    return (f">>> ## Wallets Leaderboard: \n### ** Coins | Name **\n ```ansi\n{walletOutput}```")

async def assign_mr_moneybags_role(guild):
    if len(wallets) == 0:
        return

    # Define the name of the role you want to assign
    role_name = "Mr. Moneybags"
    
    # Find the role in the guild
    role = discord.utils.get(guild.roles, name=role_name)

    # Get Mr. Moneybags
    highest_wallet = -float('inf')
    mr_moneybags = None
    
    # Iterate through wallets list to find the user with the highest wallet
    for wallet in wallets:
        user_name, user_wallet = wallet.split(" - ")
        user_wallet = int(user_wallet)
        if user_wallet > highest_wallet:
            highest_wallet = user_wallet
            mr_moneybags = user_name

    mr_moneybags_user = await guild.fetch_member(mr_moneybags)

    # If the role is found
    if role:
        # Check if the user already has the "Mr. Moneybags" role
        if role not in mr_moneybags_user.roles:
            # Iterate through all the members of the guild
            for member in guild.members:
                # Remove the "Mr. Moneybags" role from all members
                if role in member.roles:
                    await member.remove_roles(role)
        
            # Add the role to the user if they do not already have it
            await mr_moneybags_user.add_roles(role)
            await log(f"Assigned 'Mr. Moneybags' role to {mr_moneybags_user.display_name}")
        else:
            await log(f"{mr_moneybags_user.display_name} already has the 'Mr. Moneybags' role")

    return str(mr_moneybags_user.id)


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
        if person.startswith("<@"):
            person = re.search(r'\d+', person).group()

        attributes_to_search = ['name', 'nick', 'display_name', 'id']
        for attribute in attributes_to_search:
            try:
                if attribute == "id":
                    try:
                        person = int(person)
                    except:
                        pass
                user = discord.utils.get(guild.members, **{attribute: person})
                if user:
                    return str(user.id)  # Found user, return user ID
            except Exception as e:
                await log(f"Exception: {e}")

        return person
    
async def get_username(guild, person):
    try:
        username = guild.get_member(int(person)).display_name
    except:
        username = f"no name found for: {person}"
        await log(f'Error while trying to get the username of one of these users: {person}', isError=True)

    return username