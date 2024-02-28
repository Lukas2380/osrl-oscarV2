import re
import socket
import discord


red = 0xFF5733
blue = 0x0CCFFF
infoEmbedColor = 0x03fc0b

osrl_Server = None # This is the OSRL Server ID
log_channel = None # This is the id of the log channel in the OSRL Server
ladder_channel = None # This is the id of the ladder channel in the OSRL Server

if (socket.gethostname() == "Lukas-Desktop"):
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

    return leaderboard, activeChallenges, locked_players, stats, streaksLeaderboard, cooldowns

leaderboard, activeChallenges, locked_players, stats, streaksLeaderboard, cooldowns = load_data()

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

async def update_ladder(guild):
        channel = guild.get_channel(ladder_channel)

        if channel:
            # Find and delete the previous message and remove it
            async for message in channel.history(limit=2):
                if message.author == guild.me:
                    if message.content.startswith('>>>'):
                        await message.delete()
            
            # Send the active Challenges and current ladder
            await channel.send(await get_activeChallenges(guild))
            await channel.send(await get_ladder(guild))

        else:
            await log("Error: Channel not found.", isError=True)

async def get_activeChallenges(guild):
        # Standard output if no one is on the active challenges list
        active_challenges = "No active challenges"
        
        if len(activeChallenges) > 0:
            # Clear the output and write the active challenges
            active_challenges = ""

            for challenge in activeChallenges:
                    # Get the playernames, playerpositions and usernames of the players
                    firstPlayer, secondPlayer, date, _  = challenge.split(" - ") # ignore the date and if it is a guardian challenge 
                    ##firstPlayerPosition = leaderboard.index(firstPlayer) + 1 # !for positioning if wanted
                    firstPlayer = await get_username(guild, firstPlayer)
                    secondPlayer = await get_username(guild, secondPlayer)
                    
                    if len(firstPlayer+secondPlayer) > 34: # This is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayer = firstPlayer[:17]
                        secondPlayer = secondPlayer[:17]
                    
                    # Write and format the active challenges
                    active_challenges += f"{date}: {firstPlayer}{' '* (14 - len(firstPlayer))} ⚔️ {secondPlayer}{' '* (14 - len(secondPlayer))}\n"
        
        return(f">>> ## Active Challenges: \n### **First Player vs Second Player **\n ```{active_challenges}```")


async def get_ladder(guild):
        # Standard output if no one is on the ladder
        ladder_table = 'No one on the ladder'

        if len(leaderboard) > 0:
                # Clear the output and write the ladder
                ladder_table = ""
                rank = 0

                for person in leaderboard:
                    symbol = ''
                    rank += 1

                    # Check if the person is in the activeChallenges list
                    for element in activeChallenges:
                        # Different symbol if they are in a guardian challenge (element.split(" - "):  first person is the attacker, second the defender)
                        if person in element.split(" - ")[0]:
                            if element.split(" - ")[3] == "true":
                                symbol = "[🗡️]"
                            else:
                                symbol = "[⚔️]"
                        elif person in element.split(" - ")[1]:
                            if element.split(" - ")[3] == "true":
                                symbol = "[🛡️]"
                            else:
                                symbol = "[⚔️]"

                    # Write and format the ladder
                    username = await get_username(guild, person)
                    ladder_table += "{:>}. {} {:<}\n".format(rank, symbol, username)

        return(f">>> ## Current Ladder: \n ### **Rank - Player - ⚔️ **\n ```{ladder_table}```")

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