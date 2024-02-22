import asyncio
import random
import re
import typing
import unicodedata
import discord
from discord.ext import commands
from discord import app_commands, Embed
from datetime import datetime, timedelta
from data.helper_functions import *

class LadderBot_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_data()
        asyncio.create_task(self.custom_on_ready())

        #*Info: the The current ladder will not be displayed after more than 123 people join because of the limit of 2000 symbols per message? So maybe make it multiple messages
        # things to do before launching
        #? todo: buttons under the automatic ladder for further information like winstreaks and shit like that
        #? todo: make /results and /confirm_results command for equilibrium
        #? todo: maybe show diffrent symbols in /active when guardianchallenge
        #? todo: make the txt files more readable with having the names displayed aswell and just ignore them in the code
        # todo: update the info txt files
        # todo: make command for setting the amount of guardian challenges
        # todo: make command for editing txt files
        #? todo: betting?
        #? todo: winloss ratio in playerinfo?
        # todo: fix function names

    async def custom_on_ready(self):
        #await asyncio.sleep(10)
        #await log("Bot is active in these guilds:")
        for guild in self.bot.guilds:
            #await log(str(guild))
            if len(self.stats) == 0:
                await self.getoldstats(guild)
            await self.update_ladder(guild)

    def load_data(self):
        # Read files and initialize a list for each one
        with open('./data/ladder/leaderboard.txt','r+') as file:
            data = file.read()
            self.leaderboard = data.split('\n')
            self.leaderboard.pop(-1)

        with open('./data/ladder/activeChallenges.txt','r+') as file:
            data = file.read()
            self.activeChallenges = data.split('\n')
            self.activeChallenges.pop(-1)

        with open('./data/ladder/lockedPlayers.txt','r+') as file:
            data = file.read()
            self.locked_players = data.split('\n')
            self.locked_players.pop(-1)

        with open('./data/ladder/stats.txt','r+') as file:
            data = file.read()
            self.stats = data.split('\n')
            self.stats.pop(-1)

        with open('./data/ladder/streaksLeaderboard.txt', 'r+') as file:
            data = file.read()
            self.streaksLeaderboard = data.split('\n')
            self.streaksLeaderboard.pop(-1)

        with open('./data/ladder/cooldowns.txt', 'r+') as file:
            data = file.read()
            self.cooldowns = data.split('\n')
            self.cooldowns.pop(-1)

    def writeToFile(self, file: str, mylist: list):
        with open(f'./data/ladder/{file}.txt', "w") as file:
            for entry in mylist:
                file.write(entry+'\n')

    async def update_ladder(self, guild):
        channel = guild.get_channel(ladder_channel)

        if channel:
            # Find and delete the previous message and remove it
            async for message in channel.history(limit=2):
                if message.author == guild.me:
                    if message.content.startswith('>>>'):
                        await message.delete()
            
            # Send the active Challenges and current ladder
            await channel.send(await self.get_activeChallenges(guild))
            await channel.send(await self.get_ladder(guild))

        else:
            await log("Error: Channel not found.", isError=True)

    def update_streak(self, player: str, win:bool, currentStreak: int):
        # This is called everytime the stats are updated
        playerInstreaksLeaderboard = False
        for entry in self.streaksLeaderboard:
            if player in entry:
                # Update the streak for the player entry
                playerInstreaksLeaderboard = True
                player, highestLossStreak, highestWinStreak = entry.split(" - ") 
                if win:
                    highestWinStreak = str(max(int(highestWinStreak), currentStreak))
                else:
                    highestLossStreak = str(max(int(highestLossStreak), abs(currentStreak)))

                # Update the streaks leaderboard
                self.streaksLeaderboard[self.streaksLeaderboard.index(entry)] = (f'{player} - {highestLossStreak} - {highestWinStreak}') 
                

        if not playerInstreaksLeaderboard:
            # Create a new entry for the player
            if win:
                self.streaksLeaderboard.append(f'{player} - 0 - 1') 
            else:
                self.streaksLeaderboard.append(f'{player} - 1 - 0') 

        self.writeToFile('streaksLeaderboard', self.streaksLeaderboard)

    def update_stats(self, player: str, win: bool):
        # This is called for each player everytime a challenge was finished
        playerInStats = False
        for stat in self.stats:
            if player in stat:
                # Update the stats for the player entry
                playerInStats = True
                player, wins, losses, streak = stat.split(' - ') 
                if win:
                    wins = int(wins) + 1
                    if int(streak) < 0:
                        streak = 1
                    else:
                        streak = int(streak) + 1
                else:
                    losses = int(losses) + 1
                    if int(streak) > 0:
                        streak = -1
                    else:
                        streak = int(streak) - 1

                self.update_streak(player, win, streak)

                # Update the streaks leaderboard 
                self.stats[self.stats.index(stat)] = (f'{player} - {str(wins)} - {str(losses)} - {str(streak)}') 
                break

        if not playerInStats:
            # Create a new entry for the player
            if win:
                self.stats.append(f'{player} - 1 - 0 - 1') 
                self.streaksLeaderboard.append(f'{player} - 0 - 1') 
            else:
                self.stats.append(f'{player} - 0 - 1 - -1') 
                self.streaksLeaderboard.append(f'{player} - 1 - 0') 

        self.writeToFile('stats', self.stats)
        self.writeToFile('streaksLeaderboard', self.streaksLeaderboard)

    @app_commands.command(name="show-cooldowns", description="Show all the cooldowns of the people in the ladder")
    async def show_cooldowns(self, interaction):
        await interaction.response.defer()

        if len(self.cooldowns) > 0:
            output = ""

            for cooldown in self.cooldowns:
                time = datetime.strptime(cooldown.split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                remaining_time = time + timedelta(days=2) - datetime.now()
                
                if remaining_time < timedelta(0):
                    self.cooldowns.remove(cooldown)
                else:
                    player = await self.get_username(interaction.guild, cooldown.split(" - ")[0])

                    _, seconds = divmod(remaining_time.seconds, 86400)
                    days = remaining_time.days
                    seconds = remaining_time.seconds
                    hours, seconds = divmod(seconds, 3600)
                    minutes, seconds = divmod(seconds, 60)

                    output += f"{player}: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds\n"

        if output == "":
            output = 'There are currently no cooldowns'

        await interaction.followup.send(f">>> ## Current Cooldowns: \n ```{output}```")

    @app_commands.command(name="show-ladder", description="Show the current ladder")
    async def ladder(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await self.get_ladder(interaction.guild))

    async def get_ladder(self, guild):
        # Standard output if no one is on the ladder
        ladder_table = 'No one on the ladder'

        if len(self.leaderboard) > 0:
                # Clear the output and write the ladder
                ladder_table = ""
                rank = 0

                for person in self.leaderboard:
                    symbol = ''
                    rank += 1

                    # Check if the person is in the activeChallenges list
                    for element in self.activeChallenges:
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
                    username = await self.get_username(guild, person)
                    ladder_table += "{:>}. {} {:<}\n".format(rank, symbol, username)

        return(f">>> ## Current Ladder: \n ### **Rank - Player - ⚔️ **\n ```{ladder_table}```")

    @app_commands.command(name="active", description="Show active challenges")
    async def active(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await self.get_activeChallenges(interaction.guild))

    async def get_activeChallenges(self, guild):
        # Standard output if no one is on the active challenges list
        active_challenges = "No active challenges"
        
        if len(self.activeChallenges) > 0:
            # Clear the output and write the active challenges
            active_challenges = ""

            for challenge in self.activeChallenges:
                    # Get the playernames, playerpositions and usernames of the players
                    firstPlayer, secondPlayer, _, _  = challenge.split(" - ") # ignore the date and if it is a guardian challenge 
                    firstPlayerPosition = self.leaderboard.index(firstPlayer) + 1
                    secondPlayerPosition = self.leaderboard.index(secondPlayer) + 1
                    firstPlayer = await self.get_username(guild, firstPlayer)
                    secondPlayer = await self.get_username(guild, secondPlayer)
                    
                    if len(firstPlayer+secondPlayer) > 40: # 28 is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayer = firstPlayer[:20]
                        secondPlayer = secondPlayer[:20]
                    
                    # Write and format the active challenges
                    active_challenges += "{:^}. {} ⚔️ {}. {}\n".format(firstPlayerPosition, firstPlayer, secondPlayerPosition, secondPlayer)
        
        return(f">>> ## Active Challenges: \n### **First Player vs Second Player **\n ```{active_challenges}```")

    @app_commands.command(name="show-stats", description="Show the stats for the 1s ladder")
    async def show_stats(self, interaction):
        await interaction.response.defer()
        
        # Standard output if no stat is found
        stats = 'No stats found'
        playerindex = None
        sortedStatlist = {}

        if len(self.stats) > 0:
            stats = ""
            for stat in self.stats:
                player, wins, losses, streak = stat.split(" - ") 

                # Only get the stats if the player is on the leaderboard
                try:
                    playerindex = self.leaderboard.index(player) + 1 # Plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    playername = await self.get_username(interaction.guild, player)

                    # Write and format the stats
                    line = "W: {:<3} | L: {:<3} | S: {:<3} | {}\n".format(str(wins), str(losses), str(streak), playername[:21])
                    sortedStatlist[playerindex] = line
                
                playerindex = None

        # Sort the list
        for person in dict(sorted(sortedStatlist.items())):
            stats += sortedStatlist[person]
        
        await interaction.followup.send(f">>> ## Ladder Stats: \n### **Wins | Losses | Current Streak | Player **\n ```{stats}```")

    @app_commands.command(name="streaks", description="Shows the highest win and lossstreaks of the ladder")
    async def streaks(self, interaction):
        await interaction.response.defer()
        streaksLB = "No streaks found"
        playerindex = None
        sortedStatlist = {}
        
        if len(self.streaksLeaderboard) > 0:
            streaksLB = ''
            for entry in self.streaksLeaderboard:
                player, lossStreak, winStreak = entry.split(' - ') 

                try:
                    playerindex = self.leaderboard.index(player) + 1 #plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    playername = await self.get_username(interaction.guild, player)

                    # Write and format the streak stats
                    line = "W: {:<3} | L: {:<3} | {}\n".format(str(winStreak), str(lossStreak), playername[:30])
                    sortedStatlist[playerindex] = line
                
                playerindex = None

        for person in dict(sorted(sortedStatlist.items())):
            streaksLB += sortedStatlist[person]
        
        await interaction.followup.send(f">>> ## Ladder Streaks: \n### **Highest Winstreak | Highest Lossstreak | Player **\n ```{streaksLB}```")

    @app_commands.command(name="player-info", description="Get all the ladder information for one player")
    async def player_info(self, interaction, player: discord.User):
        await interaction.response.defer()
        playerID = str(player.id)
        playerIsLocked = False
        lockedStatus = ""
        playerRank = "/"

        # Show if person is locked
        for lockedPlayer in self.locked_players:
            if playerID in lockedPlayer:
                playerIsLocked = True
                lockedStatus = "Player is currently locked"
                playerRank = lockedPlayer.split(" - ")[0]

        if not playerIsLocked:
            # Show Position on the ladder
            for ladderEntry in self.leaderboard:
                if playerID in ladderEntry:
                    playerRank = self.leaderboard.index(ladderEntry)

            # Show if person is in an active challenge
            active_challenge_info = None
            for active_challenge in self.activeChallenges:
                if playerID in active_challenge:
                    firstPlayer, secondPlayer, date, isGuardian  = active_challenge.split(" - ") 
                    firstPlayerPosition = self.leaderboard.index(firstPlayer) + 1
                    secondPlayerPosition = self.leaderboard.index(secondPlayer) + 1

                    firstPlayerName = await self.get_username(interaction.guild, firstPlayer)
                    secondPlayerName = await self.get_username(interaction.guild, secondPlayer)
                    
                    if len(firstPlayerName+secondPlayerName) > 40: # 28 is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayerName = firstPlayerName[:20]
                        secondPlayerName = secondPlayerName[:20]
                    
                    # Write and format the output
                    active_challenge_info = "{:^}. {} ⚔️ {}. {}\n".format(firstPlayerPosition, firstPlayerName, secondPlayerPosition, secondPlayerName)

        # Show Wins/Losses/Current Streak
        player_stats = None
        for entry in self.stats:
            if playerID in entry:
                player_stats = entry

        # Show Highest Win Streak/Highest Loss Streak
        player_streaks = None
        for streak in self.streaksLeaderboard:
            if playerID in streak:
                player_streaks = streak

        # Create the embed
        embed = discord.Embed(title=f"Stats for {player.display_name}", color=blue)
        embed.set_thumbnail(url=player.avatar.url)

        if playerIsLocked:
            embed.add_field(name="Locked Status", value=f"{lockedStatus}", inline=False)

        embed.add_field(name="Ladder Position", value=f"```{playerRank}```", inline=False)

        if active_challenge_info:
            embed.add_field(name="Current Challenge", value=f"```{active_challenge_info}```", inline=False)

        if player_stats:
            _, wins, losses, current_streak = player_stats.split(' - ')  
            embed.add_field(name="Wins: ", value=f"```{wins}```", inline=True)
            embed.add_field(name="Losses: ", value=f"```{losses}```", inline=True)
            embed.add_field(name="Streak: ", value=f"```{current_streak}```", inline=True)

        if player_streaks:
            _, highest_loss_streak, highest_win_streak = player_streaks.split(' - ') 
            embed.add_field(name="Highest Win Streak", value=f"```{highest_win_streak}```", inline=True)
            embed.add_field(name="Highest Loss Streak", value=f"```{highest_loss_streak}```", inline=True)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="challenge", description="Challenge the player above you")  
    async def challenge(self, interaction):
        await interaction.response.defer()

        # Init variables
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        playerAboveAlreadyInChallenge = False
        playerIsFirst = False
        player = interaction.user

        # Check if player has a cooldown
        response = self.handleCooldowns(player)
        if response:
            return await interaction.followup.send(embed=response)

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True

                playerRank = self.leaderboard.index(str(player.id))

                if playerRank == 0:
                    playerIsFirst = True
                    break

                playerAboveId = self.leaderboard[playerRank - 1]
                
                # Check if anyone is already in a challenge
                for activeChallenge in self.activeChallenges:
                    if str(player.id) in activeChallenge:
                        playerAlreadyInChallenge = True
                        response = Embed(title="Error", description="Don't be scared, you're already in a challenge.", color=red)
                        break
                    elif playerAboveId in activeChallenge:
                        playerAboveAlreadyInChallenge = True
                        response = Embed(title="Error", description="The player above is already in a challenge", color=red)
                        break
                
                if not playerAlreadyInChallenge and not playerAboveAlreadyInChallenge:
                    # Schedule the challenge
                    date = datetime.now() + timedelta(days=7)
                    date = date.strftime("%x")
                    
                    self.activeChallenges.append(f'{str(player.id)} - {playerAboveId} - {date} - false') 
                    self.writeToFile('activeChallenges', self.activeChallenges)
                    
                    self.cooldowns.append(f'{str(player.id)} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}') 
                    self.writeToFile('cooldowns', self.cooldowns)

                    response = Embed(title="Challenge scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(playerAboveId)).mention} \n\nis scheduled to be completed by: {date}', color=blue)

                    await self.update_ladder(interaction.guild)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        if playerIsFirst:
            response = Embed(title="Error", description=f'{player.mention} there is no one left to challenge for you!')
        await interaction.followup.send(embed=response)

    def handleCooldowns(self, player):
        # This is called for the player who put in /challenge or /challenge-guardian
        for cooldown in self.cooldowns:
            if str(player.id) in cooldown:
                time = datetime.strptime(cooldown.split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                remaining_time = time + timedelta(days=2) - datetime.now()

                # If cooldown ran out
                if remaining_time < timedelta(0):
                    self.cooldowns.remove(cooldown)
                else:
                    # Get the remaining time and format the output
                    _, seconds = divmod(remaining_time.seconds, 86400)
                    days = remaining_time.days
                    seconds = remaining_time.seconds
                    hours, seconds = divmod(seconds, 3600)
                    minutes, seconds = divmod(seconds, 60)

                    response = Embed(
                        title="Cooldown Reminder",
                        description=f"Your challenge cooldown has not run out yet, you still have to wait: \n**{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds** before you can challenge again",
                        color=red
                    )
                    return response

    @app_commands.command(name="challenge-guardian", description="Challenge the guardian above you")
    async def challenge_guardian(self, interaction):
        await interaction.response.defer()

        # Init variables
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        guardianAlreadyInChallenge = False        
        player = interaction.user

        # Check if player has a cooldown
        response = self.handleCooldowns(player=player)
        if response:
            return await interaction.followup.send(embed=response)

        # Restricting amount of guardian-challenges:
        maxGuardianChallenges = 1
        guardianChallenges = 0

        for challenge in self.activeChallenges:
            if challenge.split(" - ")[3] == "true":
                guardianChallenges += 1

        if guardianChallenges >= maxGuardianChallenges:
            response = Embed(title="Error", description=f"{player.mention}, you can't guardian-challenge! \nThere is already the maximum amount of **{maxGuardianChallenges}** active guardian-challenges.", color=red)
            await interaction.followup.send(embed=response)

        # Set the guardianpositions to 3, and then in steps of five so 5,10... and so on
        guardian_positions = [3] + [i for i in range(5, len(self.leaderboard), 5)]

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True

                # Get the next guardian in the ladder
                playerRank = self.leaderboard.index(str(player.id))
                nearest_guardian = next((guardian_pos for guardian_pos in sorted(guardian_positions, reverse=True) if guardian_pos <= playerRank), None) 

                if nearest_guardian is not None:
                    guardianId = self.leaderboard[nearest_guardian - 1]

                    # Check if anyone is already in a challenge
                    for activeChallenge in self.activeChallenges:
                        if str(player.id) in activeChallenge:
                            playerAlreadyInChallenge = True
                            response = Embed(title="Error", description="Don't be scared, you're already in a challenge.", color=red)
                            break
                        elif guardianId in activeChallenge:
                            guardianAlreadyInChallenge = True
                            response = Embed(title="Error", description="The guardian you are trying to challenge is already in a challenge", color=red)
                            break

                    if not playerAlreadyInChallenge and not guardianAlreadyInChallenge:
                        # Schedule the challenge
                        date = datetime.now() + timedelta(days=7)
                        date = date.strftime("%x")

                        self.activeChallenges.append(f'{str(player.id)} - {guardianId} - {date} - true') 
                        self.writeToFile('activeChallenges', self.activeChallenges)

                        self.cooldowns.append(f'{str(player.id)} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}') 
                        self.writeToFile('cooldowns', self.cooldowns)

                        response = Embed(title="Guardian Challenge Scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(guardianId)).mention} \n\nis scheduled to be completed by: {date}', color=blue)

                        await self.update_ladder(interaction.guild)
                        break

                else:
                    response = Embed(title="Error", description=f'{player.mention} there is no guardian above you!', color=red)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        await interaction.followup.send(embed=response)

    @app_commands.command(name="results", description="Submit the results of a challenge")
    async def results(self, interaction, result: typing.Literal["W", "L"]):
        await interaction.response.defer()

        player = interaction.user
        noActiveChallenge = True

        for challenge in self.activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False

                challenger = challenge.split(' - ')[0]
                challenged = challenge.split(' - ')[1]

                # Fetching user objects of challenger and challenged players
                challenger_user = await self.bot.fetch_user(int(challenger))
                challenged_user = await self.bot.fetch_user(int(challenged))

                isGuardianchallenge = False
                if challenge.split(' - ')[3] == "true":
                    isGuardianchallenge = True

                leaderboard_change = "The leaderboard didnt change."

                if str(player.id) == challenger:
                    if result == "W": # Player is challenger and won
                        response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=blue)
                        self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenged))
                        self.update_stats(challenger, True)
                        self.update_stats(challenged, False)
                        leaderboard_change = f"{challenger_user.mention} was moved above {challenged_user.mention} for winning the challenge."
                    else:  # Player is challenger and lost
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=red)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                else:
                    if result == "W": # Player is the one being challenged and won
                        response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=blue)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                    else:  # Player is the one being challenged and lost
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=red)
                        self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenged))
                        self.update_stats(challenger, True)
                        self.update_stats(challenged, False)
                        leaderboard_change = f"{challenger_user.mention} was moved above {challenged_user.mention} for winning the challenge."

                self.activeChallenges.remove(challenge)

                self.writeToFile('activeChallenges', self.activeChallenges)
                self.writeToFile('leaderboard', self.leaderboard)
                
                await self.update_ladder(interaction.guild)
                response.add_field(name="Leaderboard Change", value=leaderboard_change, inline=False)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=red)

        await interaction.followup.send(embed=response)

    def movePlayerinLeaderboard(self, player: str, position: int):
        # This is being called everytime there is a change in the leaderboard
        self.leaderboard.remove(player)
        self.leaderboard.insert(position, player) 

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
        await interaction.response.defer()
        alreadyIsInLadder = False
        player = interaction.user

        # Check if player is already in the leaderboard
        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant join the ladder", description=f'{player.mention}, you are already in the ladder', color=red)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            # Add player to the leaderboard
            self.leaderboard.append(str(player.id)) 
            self.writeToFile('leaderboard', self.leaderboard)
            
            response = Embed(title='Player added', description=f'Try not to get wrecked', color=blue)
            await self.update_ladder(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="add", description="Add a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction, player: discord.User, position: int):
        await interaction.response.defer()
        alreadyIsInLadder = False

        # Check if player is already in the leaderboard
        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant add player", description=f'{player.mention} is already in the ladder', color=red)
                alreadyIsInLadder = True
                break

        # Add the player at the desired position
        if not alreadyIsInLadder:
            if position > 0:
                self.leaderboard.insert(position-1,str(player.id)) 
                response=Embed(title="Player added", description=f'{player.mention} added in the {position} position', color=blue)
            elif position == 0:
                self.leaderboard.append(str(player.id)) 
                response=Embed(title="Player added", description=f'{player.mention} added in the last position', color=blue)

            self.writeToFile('leaderboard', self.leaderboard)
            await self.update_ladder(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove", description="Remove a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction, player: discord.User):
        await interaction.response.defer()
        response = Embed(title="Error", description=f'Player {player.mention} not recognized.', color=red)

        # Find the player and remove them from the leaderboard
        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIndex = self.leaderboard.index(str(player.id))
                self.leaderboard.pop(playerIndex)

                self.writeToFile('leaderboard', self.leaderboard)

                # Remove the active challenge if one with the player is found
                for challenge in self.activeChallenges:
                    if str(player.id) in challenge:
                        self.activeChallenges.remove(challenge)
                        break
                self.writeToFile('activeChallenges', self.activeChallenges)
                
                response = Embed(title="Player removed", description=f'Player {player.mention} removed from the ladder', color=blue)
                await self.update_ladder(interaction.guild)
                break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="cointoss", description="Toss a coin!")
    async def cointoss(self, interaction):
        await interaction.response.defer()
        r = random.randint(1,2)
        if r == 1:
            result = "Heads!"
        else:
            result = "Tails!"
        response = Embed(title='Result:', description=result, color=blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="view-locked", description="View currently locked players") #todo: default_member_permissions=3
    #@app_commands.checks.has_permissions(administrator=True)
    #@app_commands.default_permissions(manage_messages=True)
    #@app_commands.checks.has_any_role("GC")
    async def view_locked(self, interaction):
        await interaction.response.defer()
        lines = ""

        # Go through all the locked players and output them
        if self.locked_players:
            for locked_player in self.locked_players:
                rank, playerId, date = locked_player.split(' - ') 
                username = await self.get_username(interaction.guild, playerId)
                lines += "{:<7} | {:>}. {:<15}\n".format(date, rank, username)
        else:
            await interaction.followup.send(f">>> ## Locked Players: \n### **Date Locked | Rank. Player  **\n ```No players currently locked```")
        await interaction.followup.send(f">>> ## Locked Players: \n### **Date Locked | Rank. Player **\n ```{lines}```")

    @app_commands.command(name="lock", description="Lock a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def lock(self, interaction, player: discord.User):
        await interaction.response.defer()
        foundPlayerInLeaderboard = False
        alreadyLocked = False

        # Search for the player in the leaderboard
        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                foundPlayerInLeaderboard = True

                # Search for the player in the list of already locked players
                for locked_player in self.locked_players:
                    if str(player.id) in locked_player:
                        alreadyLocked = True

                # Lock player
                if not alreadyLocked:
                    for challenge in self.activeChallenges:
                        if str(player.id) in challenge:
                            self.activeChallenges.remove(challenge)

                    # Remove player from the leaderboard and add them to the locked player list
                    for leaderboardline in self.leaderboard:
                        if str(player.id) in leaderboardline:
                            leaderboardIndex = self.leaderboard.index(str(player.id))
                            self.leaderboard.pop(leaderboardIndex)

                            date = datetime.now().strftime("%x")
                            self.locked_players.append(f'{leaderboardIndex+1} - {player.id} - {date}') 

                    self.writeToFile('lockedPlayers', self.locked_players)
                    self.writeToFile('leaderboard', self.leaderboard)
                    self.writeToFile('activeChallenges', self.activeChallenges)

                    response=Embed(title='Player Locked', description=f'Player locked untilf further notice', color=blue)
                    await self.update_ladder(interaction.guild)
                    break

        if not foundPlayerInLeaderboard:
            response = Embed(title='Player not found', description=f'Player was not found in the leaderboard')
        elif alreadyLocked:
            response = Embed(title='Player already locked', description=f'The player is already in the locked player list')

        await interaction.followup.send(embed=response)

    @app_commands.command(name="unlock", description="Unlock a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def unlock(self, interaction, player: discord.User):
        await interaction.response.defer()
        response = Embed(title="Error", description=f"Didnt find {player.mention} in the locked player list", color=blue)
        
        # Find the player in the locked player list
        for locked_player in self.locked_players:
            if str(player.id) in locked_player:
                self.locked_players.remove(locked_player)

                # Insert them into the leaderboard
                rank, _, _ = locked_player.split(' - ') 
                self.leaderboard.insert(int(rank)-1, str(player.id)) 

                self.writeToFile('lockedPlayers', self.locked_players)
                self.writeToFile('leaderboard', self.leaderboard)

                response = Embed(title="Unlocked", description=f"{player.mention} unlocked", color=blue)
                await self.update_ladder(interaction.guild)
                break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove-challenge", description="Removes the challenge which has the selected player in it")
    #@app_commands.checks.has_permissions(administrator=True)
    async def removeChallenge(self, interaction, player: discord.User):
        await interaction.response.defer()
        noActiveChallenge = True

        # Find the challenge and remove it
        for challenge in self.activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False
                self.activeChallenges.remove(challenge)
                self.writeToFile('activeChallenges', self.activeChallenges)

                response = Embed(title="Challenge removed", description=f'The challenge with the player: {player.mention} has been removed', color=blue)
                await self.update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove-cooldown", description="Removes the players cooldown")
    #@app_commands.checks.has_permissions(administrator=True)
    async def removeCooldown(self, interaction, player: discord.User):
        await interaction.response.defer()
        hasnoCooldown = True

        # Find the cooldown for the person and remove it
        for cooldown in self.cooldowns:
            if str(player.id) in cooldown:
                hasnoCooldown = False
                self.cooldowns.remove(cooldown)

                self.writeToFile('cooldowns', self.cooldowns)

                response = Embed(title="Cooldown removed", description=f'The cooldown for the player: {player.mention} has been removed', color=blue)
                break

        if hasnoCooldown:
            response = Embed(title="Error", description=f'The player: {player.mention} has no cooldown', color=red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="update-txt", description="Takes all the txt files and changes the names to ids")
    async def updatetxt(self, interaction):
        # This goes through all the txt files and tries to change the usernames to user ids
        await interaction.response.defer()
        await log("Updating Leaderboard...")
        self.load_data()
        
        newLeaderboard = []
        newActiveChallenges = []
        newLockedPlayers = []

        await log(interaction.guild)

        for person in self.leaderboard:
            user_id = await self.get_user_id(interaction.guild, person)
            newLeaderboard.append(user_id) 

        self.writeToFile("leaderboard", newLeaderboard)
        self.leaderboard = newLeaderboard

        for challenge in self.activeChallenges:
            firstPlayer, secondPlayer, date, _ = challenge.split(" - ") 

            firstPlayerID = await self.get_user_id(interaction.guild, firstPlayer)
            secondPlayerID = await self.get_user_id(interaction.guild, secondPlayer)
            newActiveChallenges.append(f"{firstPlayerID} - {secondPlayerID} - {date}") 

        self.writeToFile("activeChallenges", newActiveChallenges)
        self.activeChallenges = newActiveChallenges

        for locked_player in self.locked_players:
            rank, username, date = locked_player.split(' - ') 
            user_id = await self.get_user_id(interaction.guild, username)
            newLockedPlayers.append(f"{rank} - {user_id} - {date}") 

        self.writeToFile("lockedPlayers", newLockedPlayers)
        self.locked_players = newLockedPlayers

        await self.update_ladder(interaction.guild)
        response = Embed(title="Text Files Updated", description="The text files have been updated.", color=blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="update-ladder", description="Command for manually updating the ladder")
    async def updateladder(self, interaction):
        # This is a manual ladder update
        await interaction.response.defer()
        self.load_data()
        await self.update_ladder(interaction.guild)
        response = Embed(title="Ladder Updated", description="The ladder has been updated.", color=blue)
        await interaction.followup.send(embed=response)

    async def getoldstats(self, guild):
        # This is only called when the stats file is empty at the start of the bot
        await log("...Fetching old stats because the stats file is empty")
        channel_id = 1098739590820540506
        channel = self.bot.get_channel(channel_id)
        challenges = []
        
        async for message in channel.history(limit=3500, oldest_first=True):
            if message.author.id == 1099026790829273169:
                if message.content.startswith('Challenge between'):

                    # Get the player Ids
                    players = message.content.split(' between ')[1].split(' and ')
                    first_player = players[0].strip('@')
                    second_player = players[1].strip('@')[0:players[1].index(' is')]

                    first_playerID = first_player.replace('<@', '').replace('>', '')
                    second_playerID = second_player.replace('<@', '').replace('>', '')

                    # If there is still a challenge with one of the players, render the challenge as undone, remove it and add the new challenge
                    for challenge in challenges:
                        if first_playerID in challenge or second_playerID in challenge:
                            challenges.remove(challenge)

                    challenges.append(f"{first_playerID},{second_playerID}")

                for embed in message.embeds:
                    if embed.title == "Results accepted" and embed.description.startswith('Congratulations'):
                        # Look in the challenges list and give the win and loss to the people in the challenge
                        try:
                            player = await self.get_user_id(guild, embed.description[16: embed.description.index("!")])
                        except:
                            player = input("Player name for: " + embed.description[16: embed.description.index("!")])

                        # Give the win and loss to the players of the resolved challenge
                        for challenge in challenges:
                            if player in challenge:
                                otherplayer = challenge.replace(player, "").replace(",", "")
                                self.update_stats(str(player), win=True)
                                self.update_stats(str(otherplayer), win=False)

                                challenges.remove(challenge)
                                break

    async def get_user_id(self, guild, person):
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
    
    async def get_username(self, guild, person):
        try:
            username = guild.get_member(int(person)).display_name
        except:
            username = f"no name found for: {person}"
            await log(f'Error while trying to get the username of one of these users: {person}', isError=True)

        return username

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))