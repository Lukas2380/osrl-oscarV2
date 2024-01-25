import asyncio
import random
import re
import typing
import unicodedata
import discord
from discord.ext import commands
from discord import app_commands, Embed
from datetime import datetime, timedelta

class LadderBot_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_data()

        #*Info: the The current ladder will not be displayed after more than 123 people join because of the limit of 2000 symbols per message? So maybe make it multiple messages
        # things to do before launching
        #? todo: buttons under the automatic ladder for further information like winstreaks and shit like that
        # todo: make /results and /confirm_results command for equilibrium
        #? todo: maybe show diffrent symbols in /active when guardianchallenge

    red = 0xFF5733
    blue = 0x0CCFFF
    osrl_Server = 979020400765841462 # This is the OSRL Server ID
    log_channel = 1199387324904112178 # This is the id of the log channel in the OSRL Server
    ladder_channel = 1193288442260488402 # This is the id of the ladder channel in the OSRL Server

    @commands.Cog.listener()
    async def on_ready(self):
        await self.log("Bot is active in these guilds:")
        for guild in self.bot.guilds:
            await self.log(str(guild))
            if len(self.stats) == 0:
                await self.getoldstats(guild)
            #await self.update_ladder(guild) # todo: reactivate

    async def log(self, output: str):
        guild = self.bot.get_guild(self.osrl_Server)
        channel = guild.get_channel(self.log_channel)
        await channel.send("```" + output + "```")

    def load_data(self):
        # Read files and initialize variables
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
        channel = guild.get_channel(self.ladder_channel)

        if channel:
            # Find and delete the previous message and remove it
            async for message in channel.history(limit=2):
                if message.author == guild.me:
                    if message.content.startswith('>>>'):
                        await message.delete()
            
            await channel.send(await self.get_activeChallenges(guild))
            await channel.send(await self.get_ladder(guild))

        else:
            await self.log("Error: Channel not found.")

    def update_streak(self, player: str, win:bool, currentStreak: int):
        playerInstreaksLeaderboard = False
        for entry in self.streaksLeaderboard:
            if player in entry:
                playerInstreaksLeaderboard = True
                player, highestLossStreak, highestWinStreak = entry.split(",")
                if win:
                    highestWinStreak = str(max(int(highestWinStreak), currentStreak))
                else:
                    highestLossStreak = str(max(int(highestLossStreak), abs(currentStreak)))

                self.streaksLeaderboard[self.streaksLeaderboard.index(entry)] = (f'{player},{highestLossStreak},{highestWinStreak}')
                

        if not playerInstreaksLeaderboard:
            if win:
                self.streaksLeaderboard.append(f'{player},0,1')
            else:
                self.streaksLeaderboard.append(f'{player},1,0')

        self.writeToFile('streaksLeaderboard', self.streaksLeaderboard)

    def update_stats(self, player: str, win: bool):
        playerInStats = False
        for stat in self.stats:
            if player in stat:
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
                self.stats[self.stats.index(stat)] = (f'{player} - {str(wins)} - {str(losses)} - {str(streak)}')
                break

        if not playerInStats:
            if win:
                self.stats.append(f'{player} - 1 - 0 - 1')
                self.streaksLeaderboard.append(f'{player},0,1')
            else:
                self.stats.append(f'{player} - 0 - 1 - -1')
                self.streaksLeaderboard.append(f'{player},1,0')

        self.writeToFile('stats', self.stats)
        self.writeToFile('streaksLeaderboard', self.streaksLeaderboard)

    @app_commands.command(name="ladder", description="Show the current ladder")
    async def ladder(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await self.get_ladder(interaction.guild))
        
    async def get_ladder(self, guild):
        ladder_table = 'No one on the ladder'
        if len(self.leaderboard) > 0:
                ladder_table = ""
                rank = 0
                    
                for person in self.leaderboard:
                    symbol = ''
                    rank += 1
                    
                    # Check if the person is in the activeChallenges list
                    for element in self.activeChallenges:
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

                    try:
                        username = guild.get_member(int(person)).display_name
                        ladder_table += "{:>}. {} {:<}\n".format(rank, symbol, username)
                    except:
                        ladder_table += "{:>3}. {:<}\n".format(rank, f"no id: {person}" + symbol) #todo: update this

        return(f">>> ## Current Ladder: \n ### **Rank - Player - ⚔️ **\n ```{ladder_table}```")

    async def get_activeChallenges(self, guild):
        active_challenges = "No active challenges"
        # Active Challenges
        if len(self.activeChallenges) > 0:
            #active_challenges = "{:>14} ⚔️ {:<14} - {:<7}\n".format("First Player", "Second Player", "Date")
            active_challenges = ""

            for challenge in self.activeChallenges:
                    firstPlayer, secondPlayer, date, symbol  = challenge.split(" - ")
                    firstPlayerPosition = self.leaderboard.index(firstPlayer) + 1
                    secondPlayerPosition = self.leaderboard.index(secondPlayer) + 1

                    try:
                        firstPlayer = guild.get_member(int(firstPlayer)).display_name
                        secondPlayer = guild.get_member(int(secondPlayer)).display_name
                    except:
                        await self.log(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')
                    
                    if len(firstPlayer+secondPlayer) > 40: # 28 is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayer = firstPlayer[:20]
                        secondPlayer = secondPlayer[:20]
                    
                    active_challenges += "{:^}. {} ⚔️ {}. {}\n".format(firstPlayerPosition, firstPlayer, secondPlayerPosition, secondPlayer)
        
        return(f">>> ## Active Challenges: \n### **First Player vs Second Player **\n ```{active_challenges}```")

    @app_commands.command(name="active", description="Show active challenges")
    async def active(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await self.get_activeChallenges(interaction.guild))

    @app_commands.command(name="show-stats", description="Show the stats for the 1s ladder")
    async def show_stats(self, interaction):
        await interaction.response.defer()
        
        stats = 'No stats found'
        playerindex = None
        sortedStatlist = {}

        if len(self.stats) > 0:
            stats = ""
            for stat in self.stats:
                player, wins, losses, streak = stat.split(" - ")

                try:
                    playerindex = self.leaderboard.index(player) + 1 #plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    try:
                        player = interaction.guild.get_member(int(player)).display_name
                    except:
                        await self.log(f'Error while trying to get the username of one of the user: {player}')
                        break
                    
                    line = "W: {:<3} | L: {:<3} | S: {:<3} | {}\n".format(str(wins), str(losses), str(streak), player[:21])
                    sortedStatlist[playerindex] = line
                
                playerindex = None

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
                player, lossStreak, winStreak = entry.split(',')

                try:
                    playerindex = self.leaderboard.index(player) + 1 #plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    try:
                        player = interaction.guild.get_member(int(player)).display_name
                    except:
                        await self.log(f'Error while trying to get the username of one of the user: {player}')
                        break

                    line = "W: {:<3} | L: {:<3} | {}\n".format(str(winStreak), str(lossStreak), player[:30])
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

        # Show If locked
        for lockedPlayer in self.locked_players:
            if playerID in lockedPlayer:
                playerIsLocked = True
                lockedStatus = "Player is currently locked"
                playerRank = lockedPlayer.split(" - ")[0]

        if not playerIsLocked:
            # Show Position on the ladders
            for ladderEntry in self.leaderboard:
                if playerID in ladderEntry:
                    playerRank = self.leaderboard.index(ladderEntry)

            # Show If in an active challenge
            active_challenge_info = None
            for active_challenge in self.activeChallenges:
                if playerID in active_challenge:
                    active_challenge_info = active_challenge

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
        embed = discord.Embed(title=f"Stats for {player.display_name}", color=self.blue)
        embed.set_thumbnail(url=player.avatar.url)

        if playerIsLocked:
            embed.add_field(name="Locked Status", value=f"{lockedStatus}", inline=False)

        embed.add_field(name="Ladder Position", value=f"```{playerRank}```", inline=False)

        if active_challenge_info:
            embed.add_field(name="Current Challenge", value=f"{active_challenge_info}", inline=False)

        if player_stats:
            _, wins, losses, current_streak = player_stats.split(' - ')
            embed.add_field(name="Wins: ", value=f"```{wins}```", inline=True)
            embed.add_field(name="Losses: ", value=f"```{losses}```", inline=True)
            embed.add_field(name="Streak: ", value=f"```{current_streak}```", inline=True)

        if player_streaks:
            _, highest_loss_streak, highest_win_streak = player_streaks.split(',')
            embed.add_field(name="Highest Win Streak", value=f"```{highest_win_streak}```", inline=True)
            embed.add_field(name="Highest Loss Streak", value=f"```{highest_loss_streak}```", inline=True)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="challenge", description="Challenge the player above you")  
    async def challenge(self, interaction):
        await interaction.response.defer()
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        playerAboveAlreadyInChallenge = False
        playerIsFirst = False
        player = interaction.user

        response = self.handleCooldowns(player=player)
        if response:
            await interaction.followup.send(embed=response)

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
                        response = Embed(title="Error", description="Don't be scared, you're already in a challenge.", color=self.red)
                        break
                    elif playerAboveId in activeChallenge:
                        playerAboveAlreadyInChallenge = True
                        response = Embed(title="Error", description="The player above is already in a challenge", color=self.red)
                        break
                
                if not playerAlreadyInChallenge and not playerAboveAlreadyInChallenge:
                    
                    date = datetime.now() + timedelta(days=7)
                    date = date.strftime("%x")

                    self.activeChallenges.append(f'{str(player.id)} - {playerAboveId} - {date} - false')
                    self.writeToFile('activeChallenges', self.activeChallenges)

                    self.cooldowns.append(f'{str(player.id)} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                    self.writeToFile('cooldowns', self.cooldowns)

                    response = Embed(title="Challenge scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(playerAboveId)).mention} \n\nis scheduled to be completed by: {date}', color=self.blue)

                    await self.update_ladder(interaction.guild)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        if playerIsFirst:
            response = Embed(title="Error", description=f'{player.mention} there is no one left to challenge for you!')
        await interaction.followup.send(embed=response)

    def handleCooldowns(self, player):
        for cooldown in self.cooldowns:
            if str(player.id) in cooldown:
                time = datetime.strptime(cooldown.split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                remaining_time = time + timedelta(days=0) - datetime.now()

                if remaining_time < timedelta(0):
                    self.cooldowns.remove(cooldown)
                else:
                    
                    _, seconds = divmod(remaining_time.seconds, 86400)
                    days = remaining_time.days
                    seconds = remaining_time.seconds
                    hours, seconds = divmod(seconds, 3600)
                    minutes, seconds = divmod(seconds, 60)

                    response = Embed(
                        title="Cooldown Reminder",
                        description=f"Your challenge cooldown has not run out yet, you still have to wait: \n**{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds** before you can challenge again",
                        color=self.red
                    )
                    return response

    @app_commands.command(name="challenge-guardian", description="Challenge the guardian above you")
    async def challenge_guardian(self, interaction):
        await interaction.response.defer()
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        guardianAlreadyInChallenge = False        
        player = interaction.user

        response = self.handleCooldowns(player=player)
        if response:
            await interaction.followup.send(embed=response)

        # Restricting amount of guardian-challenges:
        maxGuardianChallenges = 1
        guardianChallenges = 0

        for challenge in self.activeChallenges:
            if challenge.split(" - ")[3] == "true":
                guardianChallenges += 1

        if guardianChallenges >= maxGuardianChallenges:
            response = Embed(title="Error", description=f"{player.mention}, you can't guardian-challenge! \nThere is already the maximum amount of **{maxGuardianChallenges}** active guardian-challenges.", color=self.red)
            await interaction.followup.send(embed=response)

        guardian_positions = [3] + [i for i in range(5, len(self.leaderboard), 5)]

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True

                playerRank = self.leaderboard.index(str(player.id))
                nearest_guardian = next((guardian_pos for guardian_pos in sorted(guardian_positions, reverse=True) if guardian_pos <= playerRank), None) 

                if nearest_guardian is not None:
                    guardianId = self.leaderboard[nearest_guardian - 1]

                    # Check if anyone is already in a challenge
                    for activeChallenge in self.activeChallenges:
                        if str(player.id) in activeChallenge:
                            playerAlreadyInChallenge = True
                            response = Embed(title="Error", description="Don't be scared, you're already in a challenge.", color=self.red)
                            break
                        elif guardianId in activeChallenge:
                            guardianAlreadyInChallenge = True
                            response = Embed(title="Error", description="The guardian you are trying to challenge is already in a challenge", color=self.red)
                            break

                    if not playerAlreadyInChallenge and not guardianAlreadyInChallenge:
                        # Schedule the challenge
                        date = datetime.now() + timedelta(days=7)
                        date = date.strftime("%x")

                        self.activeChallenges.append(f'{str(player.id)} - {guardianId} - {date} - true')
                        self.writeToFile('activeChallenges', self.activeChallenges)

                        self.cooldowns.append(f'{str(player.id)} - {datetime.now()}')
                        self.writeToFile('cooldowns', self.cooldowns)

                        response = Embed(title="Guardian Challenge Scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(guardianId)).mention} \n\nis scheduled to be completed by: {date}', color=self.blue)

                        await self.update_ladder(interaction.guild)
                        break

                else:
                    response = Embed(title="Error", description=f'{player.mention} there is no guardian above you!', color=self.red)
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
                    if result == "W":
                        response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=self.blue)
                        self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenged))
                        self.update_stats(challenger, True)
                        self.update_stats(challenged, False)
                        leaderboard_change = f"{challenger_user.mention} was moved above {challenged_user.mention} for winning the challenge."
                    else:  # result == "L"
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=self.red)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                else:  # player is the one being challenged
                    if result == "W":
                        response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=self.blue)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, self.leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                    else:  # result == "L"
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=self.red)
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
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=self.red)

        await interaction.followup.send(embed=response)

    def movePlayerinLeaderboard(self, player: str, position: int):
        self.leaderboard.remove(player)
        self.leaderboard.insert(position, player)

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
        await interaction.response.defer()
        alreadyIsInLadder = False
        player = interaction.user

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant join the ladder", description=f'{player.mention}, you are already in the ladder', color=self.red)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            self.leaderboard.append(str(player.id))
            self.writeToFile('leaderboard', self.leaderboard)
            
            response = Embed(title='Player added', description=f'Try not to get wrecked', color=self.blue)
            await self.update_ladder(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="add", description="Add a player")
    #@app_commands.checks.has_any_role("GC")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction, player: discord.User, position: int):
        await interaction.response.defer()
        alreadyIsInLadder = False

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant add player", description=f'{player.mention} is already in the ladder', color=self.red)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            if position > 0:
                self.leaderboard.insert(position-1,str(player.id))
                response=Embed(title="Player added", description=f'{player.mention} added in the {position} position', color=self.blue)
            elif position == 0:
                self.leaderboard.append(str(player.id))
                response=Embed(title="Player added", description=f'{player.mention} added in the last position', color=self.blue)

            self.writeToFile('leaderboard', self.leaderboard)
            
            await self.update_ladder(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove", description="Remove a player")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction, player: discord.User):
        await interaction.response.defer()
        response = Embed(title="Error", description=f'Player {player.mention} not recognized.', color=self.red)

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIndex = self.leaderboard.index(str(player.id))
                self.leaderboard.pop(playerIndex)

                self.writeToFile('leaderboard', self.leaderboard)

                for challenge in self.activeChallenges:
                    if str(player.id) in challenge:
                        self.activeChallenges.remove(challenge)
                        break
                self.writeToFile('activeChallenges', self.activeChallenges)
                
                response = Embed(title="Player removed", description=f'Player {player.mention} removed from the ladder', color=self.blue)
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
        response = Embed(title='Result:', description=result, color=self.blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="view-locked", description="View currently locked players")
    @app_commands.checks.has_permissions(administrator=True)
    async def view_locked(self, interaction):
        await interaction.response.defer()
        lines = ""

        if self.locked_players:
            for locked_player in self.locked_players:
                rank, name, date = locked_player.split(' - ')

                try:
                    username = interaction.guild.get_member(int(name)).display_name
                except:
                    await self.log(f'Error while trying to get the username of the user: {name}')
                    break

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

                    response=Embed(title='Player Locked', description=f'Player locked untilf further notice', color=self.blue)
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
        response = Embed(title="Error", description=f"Didnt find {player.mention} in the locked players", color=self.blue)
        
        for locked_player in self.locked_players:
            if str(player.id) in locked_player:
                self.locked_players.remove(locked_player)

                rank, playerName, date = locked_player.split(' - ')
                self.leaderboard.insert(int(rank)-1, str(player.id))

                self.writeToFile('lockedPlayers', self.locked_players)
                self.writeToFile('leaderboard', self.leaderboard)

                response = Embed(title="Unlocked", description=f"{player.mention} unlocked", color=self.blue)
                await self.update_ladder(interaction.guild)
                break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove-challenge", description="Removes the challenge which has the selected player in it")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeChallenge(self, interaction, player: discord.User):
        await interaction.response.defer()
        noActiveChallenge = True

        for challenge in self.activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False
                self.activeChallenges.remove(challenge)

                self.writeToFile('activeChallenges', self.activeChallenges)

                response = Embed(title="Challenge removed", description=f'The challenge with the player: {player.mention} has been removed', color=self.blue)
                await self.update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=self.red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="remove-cooldown", description="Removes the players cooldown")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeCooldown(self, interaction, player: discord.User):
        await interaction.response.defer()
        hasnoCooldown = True

        for cooldown in self.cooldowns:
            if str(player.id) in cooldown:
                hasnoCooldown = False
                self.cooldowns.remove(cooldown)

                self.writeToFile('cooldowns', self.cooldowns)

                response = Embed(title="Cooldown removed", description=f'The cooldown for the player: {player.mention} has been removed', color=self.blue)
                break

        if hasnoCooldown:
            response = Embed(title="Error", description=f'The player: {player.mention} has no cooldown', color=self.red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="update-txt", description="Takes all the txt files and changes the names to ids")
    async def updatetxt(self, interaction):
        await interaction.response.defer()
        await self.log("Updating Leaderboard...")
        self.load_data()
        
        newLeaderboard = []
        newActiveChallenges = []
        newLockedPlayers = []

        await self.log(interaction.guild)

        for person in self.leaderboard:
            user_id = await self.get_user_id(interaction.guild, person)
            newLeaderboard.append(user_id)

        self.writeToFile("leaderboard", newLeaderboard)
        self.leaderboard = newLeaderboard

        for challenge in self.activeChallenges:
            firstPlayer, secondPlayer, date, symbol = challenge.split(" - ")

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
        response = Embed(title="Text Files Updated", description="The text files have been updated.", color=self.blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="update-ladder", description="Command for manually updating the ladder")
    async def updateladder(self, interaction):
        self.load_data()
        await self.update_ladder(interaction.guild)
        response = Embed(title="Ladder Updated", description="The ladder has been updated.", color=self.blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="test", description="Command")
    async def test(self, ctx):
        guild = None
        channel_id = 1182411076307009607  # Todo: change channel id
        channel = guild.get_channel(channel_id)

        return

        if channel:
            ladder_table = []
            active_challenges = []

            # Generating ladder table
            if len(self.leaderboard) > 0:
                rank = 0
                for person in self.leaderboard:
                    wins = 0
                    losses = 0
                    streak = 0
                    swords = ' '
                    rank += 1

                    for element in self.activeChallenges:
                        if person in element:
                            swords = "⚔️"

                    for element in self.stats:
                        if person in element:
                            user, wins, losses, streak = element.split(" - ")

                    try:
                        username = guild.get_member(int(person)).display_name
                        username = unicodedata.normalize('NFKC', username)
                        username = re.sub(r"[^a-zA-Z0-9]","_",username)
                        ladder_table.append([
                            rank,
                            f"{username[:20]}{' ' * (20 - len(username))}",
                            swords,
                            f"W: {wins}",
                            f"L: {losses}",
                            f"S: {streak}"
                        ])
                    except:
                        ladder_table.append([
                            rank,
                            f"no id: {person}",
                            swords,
                            f"W: {wins}",
                            f"L: {losses}",
                            f"S: {streak}"
                        ])

            # Generating active challenges table
            if len(self.activeChallenges) > 0:
                nr = 0
                for challenge in self.activeChallenges:
                    firstPlayer, secondPlayer, date, symbol = challenge.split(" - ")
                    nr += 1

                    try:
                        firstPlayer = guild.get_member(int(firstPlayer)).display_name
                        secondPlayer = guild.get_member(int(secondPlayer)).display_name
                    except:
                        await self.log(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')

                    active_challenges.append([
                        nr,
                        firstPlayer,
                        secondPlayer,
                        date
                    ])

            # Find and delete the previous embed
            async for message in channel.history(limit=5):
                if message.author == guild.me and message.embeds:
                    for embed in message.embeds:
                        if embed.title == 'Current Ladder' or embed.title == 'Active Challenges':
                            await message.delete()
                            break

            # Convert lists to ASCII tables using generate_text_table function
            ladder_table_str = self.generate_text_table(["Rank", "Player", "Challenge", "Wins", "Losses", "Streak"], ladder_table)
            active_challenges_str = self.generate_text_table(["Nr.", "First Player", "Second Player", "Date"], active_challenges)

            message = f">>> ## Active Challenges: \n{active_challenges_str}\n\n ## Current Ladder: \n{ladder_table_str}"
            await self.log(ladder_table_str)
            await channel.send(f"```\n{message}\n```")
        else:
            await self.log("Error: Channel not found.")

    def generate_text_table(self, header, data):

        
        # Calculate column widths
        col_widths = [max(len(str(row[i])) for row in data + [header]) for i in range(len(header))]

        # Generate the separator line
        separator = '+'.join('-' * (width + 2) for width in col_widths)
        separator = f"+{separator}+"

        # Generate header
        header_row = "| " + " | ".join(f"{header[i]:^{col_widths[i]}}" for i in range(len(header))) + " |"

        # Generate rows
        data_rows = [f"| {' | '.join(f'{row[i]:^{col_widths[i]}}' for i in range(len(row)))} |" for row in data]

        # Combine all parts to create the table
        table = "\n".join([separator, header_row, separator] + data_rows + [separator])
        return table

    async def getoldstats(self, guild):
        await self.log("...Fetching old stats because the stats file is empty")
        channel_id = 1098739590820540506
        channel = self.bot.get_channel(channel_id)
        challenges = []
        a = ""
        b = ""
        
        async for message in channel.history(limit=3500, oldest_first=True):
            if message.author.id == 1099026790829273169:
                if message.content.startswith('Challenge between'):

                    players = message.content.split(' between ')[1].split(' and ')
                    first_player = players[0].strip('@')
                    second_player = players[1].strip('@')[0:players[1].index(' is')]

                    first_playerID = first_player.replace('<@', '').replace('>', '')
                    second_playerID = second_player.replace('<@', '').replace('>', '')

                    for challenge in challenges:
                        if first_playerID in challenge or second_playerID in challenge:
                            challenges.remove(challenge)

                    try:
                        a = guild.get_member(int(first_playerID)).display_name
                    except:
                        a = first_playerID
                    try:
                        b = guild.get_member(int(second_playerID)).display_name
                    except:
                        b = second_playerID

                    #await self.log(f"Challenge between {a} and {b}")
                    #challenges.append(f"{first_playerID},{second_playerID}")
                    challenges.append(f"{first_playerID},{second_playerID}")

                for embed in message.embeds:
                    if embed.title == "Results accepted" and embed.description.startswith('Congratulations'):
                        #await self.log(embed.description)
                        # Look in the challenges list and give the win and loss to the people in the challenge
                        try:
                            player = await self.get_user_id(guild, embed.description[16: embed.description.index("!")])
                        except:
                            input(embed.description[16: embed.description.index("!")])

                        for challenge in challenges:
                            if player in challenge:
                                #await self.log(f"{challenge}, won by {player}")
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
                await self.log(f"Exception: {e}")

        return person

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))