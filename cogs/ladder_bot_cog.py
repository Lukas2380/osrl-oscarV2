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
        # todo: timer for things like rechallenge or smthing like that
        # todo: make challenged person have shield instead of sword, have challenged guardian have golden shield
        # todo: make commands work for admin only
        # todo: make log channel for logging instead of echo
        # todo: challenge scheduled embed make blue

    red = 0xFF5733
    blue = 0x0CCFFF

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            print(self.bot.guilds)
            if len(self.stats) == 0:
                await self.getoldstats(guild)
            await self.update_ladder(guild)

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

    def writeToFile(self, file: str, mylist: list):
        with open(f'./data/ladder/{file}.txt', "w") as file:
            for entry in mylist:
                file.write(entry+'\n')

    async def update_ladder(self, guild):
        # ! Warning: at about 4000 symbols maybe about 69 players in the ladder, the embed will be maxed out and cant be displayed
        # ! Since I am using the line numbers as the player position, if you want to send the ladder as two embeds, the "position" will start at 1 again
        channel_id = 1182411076307009607  # Todo: change channel id
        channel = guild.get_channel(channel_id)

        if channel:
            ladder_table = 'No active challenges'
            active_challenges = 'No active challenges'
            if len(self.leaderboard) > 0:
                ladder_table = ""
                #ladder_table = "{:^5} - {:<14} {:^2} |{:<2}|{:<2}|{:<2}\n".format("Rank", "Player", "⚔️", "Wins", "Losses", "Streak")
                #ladder_table += "\n"
                rank = 0

                # Check if there are any entries in the leaderboard
                if self.leaderboard:
                    
                    for person in self.leaderboard:
                        wins = 0
                        losses = 0
                        streak = 0
                        swords = ''
                        rank += 1
                        
                        # Check if the person is in the activeChallenges list
                        for element in self.activeChallenges:
                            if person in element:
                                swords = "⚔️"

                        for element in self.stats:
                            if person in element:
                                user, wins, losses, streak = element.split(" - ")

                        try:
                            username = guild.get_member(int(person)).display_name
                            #username = unicodedata.normalize('NFKC', username)
                            #username = re.sub(r"[^a-zA-Z0-9]","_",username)
                            #ladder_table += "{:^3} - {:<14}| W: {:<3} | L: {:<3} | S: {:<3}\n".format(rank, username[:14] + swords, wins, losses, streak)
                            ladder_table += "{:^3} | W: {:<2} | L: {:<2} | S: {:<2} - {:<14}\n".format(rank, wins, losses, streak, username[:14] + swords)
                        except:
                            ladder_table += "{:^3} - {:<17}| W: {:<3} | L: {:<3} | S: {:<3}\n".format(rank, f"no id: {person[:14]}" + swords, wins, losses, streak)

                ladder_table += "\n"

            # Active Challenges
            if len(self.activeChallenges) > 0:
                #active_challenges = "{:>14} ⚔️ {:<14} - {:<7}\n".format("First Player", "Second Player", "Date")
                active_challenges = ""
                nr = 0

                for challenge in self.activeChallenges:
                    firstPlayer, secondPlayer, date = challenge.split(" - ")
                    nr += 1

                    try:
                        firstPlayer = guild.get_member(int(firstPlayer)).display_name
                        secondPlayer = guild.get_member(int(secondPlayer)).display_name
                    except:
                        print(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')
                    
                    if len(firstPlayer+secondPlayer) > 28: # 28 is the max length of the message (+nr+swords+date+spaces) that can be displayed on the phone
                        firstPlayer = firstPlayer[:14]
                        secondPlayer = secondPlayer[:14]
                    active_challenges += "{:^} - {} ⚔️ {} - {:<7}\n".format(nr, firstPlayer, secondPlayer, date)

                active_challenges += "\n"

            # Find and delete the previous embed
            async for message in channel.history(limit=5):
                if message.author == guild.me and message.embeds:
                    for embed in message.embeds:
                        if embed.title == 'Current Ladder' or embed.title == 'Active Challenges':
                            await message.delete()
                            break

            message = f">>> ## Active Challenges: \n### **Nr., First Player, Second Player, Date**\n```{active_challenges}``` \n## **Current Ladder:** \n### **Rank - Player - ⚔️ - Wins - Losses - Streak**\n```{ladder_table}```"
            
            #message = f">>> ## Active Challenges: \n```{active_challenges}``` \n ## Current Ladder: \n```{ladder_table}```"
            #message = f"```Active Challenges:\n{active_challenges}\n\nCurrent Ladder:\n{ladder_table}```"
            await channel.send(message)

        else:
            print("Error: Channel not found.")

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
        ladder = ''

        for person in self.leaderboard:
            swords = ''
            rank = 1 + self.leaderboard.index(person)

            # Check if the person is in the activeChallenges list
            for element in self.activeChallenges:
                if person in element:
                    swords = ':crossed_swords:'

            try:
                username = interaction.guild.get_member(int(person)).display_name
                ladder += f'{rank}. {username}{swords}\n'
            except:
                await interaction.response.send_message(f'Error while trying to get the username of the user: {person}')

        response = Embed(title='Current Ladder: ', description=ladder, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="active", description="Show active challenges")
    async def active(self, interaction):
        activeChallenges = 'No active challenges'
        
        if len(self.activeChallenges) > 0:
            activeChallenges = ''

            for challenge in self.activeChallenges:
                firstPlayer, secondPlayer, date = challenge.split(" - ")

                try:
                    firstPlayer = interaction.guild.get_member(int(firstPlayer)).display_name
                    secondPlayer = interaction.guild.get_member(int(secondPlayer)).display_name
                    activeChallenges += f"{firstPlayer} - {secondPlayer} - {date}\n"
                except:
                    await interaction.response.send_message(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')
                

        response = Embed(title='Active Challenges ', description=activeChallenges, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="show_stats", description="Show the stats for the 1s ladder")
    async def show_stats(self, interaction):
        #todo: finishing ui touch here
        stats = 'No stats found'

        if len(self.stats) > 0:
            stats = 'Player | Highest Lossstreak | Highest Winstreak'

            for stat in self.stats:
                player, wins, losses, streak = stat.split(" - ")

                try:
                    player = interaction.guild.get_member(int(player)).display_name
                    stats += f'{str(player)} | W: {str(wins)} | L: {str(losses)} | S: {str(streak)}\n'
                except:
                    await interaction.response.send_message(f'Error while trying to get the username of one of the user: {player}')

        response = Embed(title='Ladder Stats: ', description=stats, color=self.blue)
        await interaction.response.send_message(embed=response)
        
    @app_commands.command(name="streaks", description="Shows the highest win and lossstreaks of the ladder")
    async def streaks(self, interaction):
        streaksLB = "No streaks found"
        
        if len(self.streaksLeaderboard) > 0:
            streaksLB = ''
            
            for entry in self.streaksLeaderboard:
                player, lossStreak, winStreak = entry.split(',')

                try:
                    player = interaction.guild.get_member(int(player)).display_name
                    streaksLB += f'{str(player)} | L: {str(lossStreak)} | W: {str(winStreak)}\n'
                except:
                    await interaction.response.send_message(f'Error while trying to get the username of one of the user: {player}')
        
        response = Embed(title='Ladder Streaks: ', description=streaksLB, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="challenge", description="Challenge the player above you")
    async def challenge(self, interaction):
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        playerAboveAlreadyInChallenge = False
        playerIsFirst = False
        player = interaction.user

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

                    self.activeChallenges.append(f'{str(player.id)} - {playerAboveId} - {date}')

                    self.writeToFile('activeChallenges', self.activeChallenges)

                    response = Embed(title="Challenge scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(playerAboveId)).mention} \n\nis scheduled to be completed by: {date}')

                    await self.update_ladder(interaction.guild)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        if playerIsFirst:
            response = Embed(title="Error", description=f'{player.mention} there is no one left to challenge for you!')
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="guardian", description="Challenge the guardian above you")
    async def guardian(self, interaction):
        #todo: maybe make it a shield instead of the swords
        playerIsInLeaderboard = False
        playerAlreadyInChallenge = False
        guardianAlreadyInChallenge = False
        player = interaction.user

        guardian_positions = [3] + [i for i in range(5, len(self.leaderboard), 5)]

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True

                playerRank = self.leaderboard.index(str(player.id))
                nearest_guardian = next((guardian_pos for guardian_pos in sorted(guardian_positions, reverse=True) if guardian_pos < playerRank), None)

                if nearest_guardian is not None:
                    guardianId = self.leaderboard[nearest_guardian - 1]
                    print(guardianId)

                    # Check if anyone is already in a challenge
                    for activeChallenge in self.activeChallenges:
                        if str(player.id) in activeChallenge:
                            playerAlreadyInChallenge = True
                            # Handle player already in a challenge
                            break
                        elif guardianId in activeChallenge:
                            guardianAlreadyInChallenge = True
                            # Handle guardian already in a challenge
                            break

                    if not playerAlreadyInChallenge and not guardianAlreadyInChallenge:
                        # Schedule the challenge
                        date = datetime.now() + timedelta(days=7)
                        date = date.strftime("%x")

                        self.activeChallenges.append(f'{str(player.id)} - {guardianId} - {date}')
                        self.writeToFile('activeChallenges', self.activeChallenges)

                        response = Embed(title="Guardian Challenge Scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(guardianId)).mention} \n\nis scheduled to be completed by: {date}')

                        await self.update_ladder(interaction.guild)
                        break

                else:
                    response = Embed(title="Error", description=f'{player.mention} there is no guardian above you!', color=self.red)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="results", description="Submit the results of a challenge")
    async def results(self, interaction, result: typing.Literal["W", "L"]):
        player = interaction.user
        noActiveChallenge = True

        for challenge in self.activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False
                otherPlayer = challenge.split(' - ')[1]

                playerIndex = self.leaderboard.index(str(player.id))
                otherPlayerIndex = self.leaderboard.index(otherPlayer)

                if playerIndex < otherPlayerIndex:
                    winnerIndex = playerIndex
                else:
                    winnerIndex= otherPlayerIndex

                if result == "W":
                    response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=self.blue)
                    
                    if playerIndex > otherPlayerIndex:
                        self.leaderboard.remove(str(player.id))
                        self.leaderboard[winnerIndex] = str(player.id)
                        self.leaderboard.insert(winnerIndex+1, otherPlayer)
                    
                    self.update_stats(str(player.id), True)
                    self.update_stats(otherPlayer, False)

                else:
                    response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=self.red)

                    if playerIndex < otherPlayerIndex:
                        self.leaderboard[winnerIndex] = otherPlayer
                        self.leaderboard[winnerIndex+1] = str(player.id)

                    self.update_stats(otherPlayer, True)
                    self.update_stats(str(player.id), False)

                self.activeChallenges.remove(challenge)

                self.writeToFile('activeChallenges', self.activeChallenges)
                self.writeToFile('leaderboard', self.leaderboard)
                
                await self.update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=self.red)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
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

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="add", description="Add a player")
    async def add(self, interaction, player: discord.User, position: int):
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

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="remove", description="Remove a player")
    async def remove(self, interaction, player: discord.User):
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

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="cointoss", description="Toss a coin!")
    async def cointoss(self, interaction):
        r = random.randint(1,2)
        if r == 1:
            result = "Heads!"
        else:
            result = "Tails!"
        response = Embed(title='Result:', description=result, color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="view-locked", description="View currently locked players")
    async def viewlocked(self, interaction):

        if self.locked_players:
            embed_description = "```\n"
            embed_description += "{:<20} {:<15} {:<10}\n".format("Name", "Date Locked", "Rank")

            for locked_player in self.locked_players:
                rank, name, date = locked_player.split(' - ')

                try:
                    username = interaction.guild.get_member(int(name)).display_name
                except:
                    await interaction.response.send_message(f'Error while trying to get the username of the user: {name}')

                embed_description += "{:<20} {:<15} {:<10}\n".format(username, date, rank)
            embed_description += "```\n"
            response = Embed(
                title='Locked players',
                description=embed_description,
                color=self.blue
            )
        else:
            response = Embed(
                title='Empty',
                description='No players currently locked',
                color=self.red
            )
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="lock", description="Lock a player")
    async def lock(self, interaction, player: discord.User):
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

                    response=Embed(title='Player Locked', description=f'Player locked untilf further notice', color=self.blue)
                    await self.update_ladder(interaction.guild)
                    break

        if not foundPlayerInLeaderboard:
            response = Embed(title='Player not found', description=f'Player was not found in the leaderboard')
        else:
            response = Embed(title='Player already locked', description=f'The player is already in the locked player list')

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="unlock", description="Unlock a player")
    async def unlock(self, interaction, player: discord.User):

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

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="remove-challenge", description="Removes the challenge which has the selected player in it")
    async def removechallenge(self, interaction, player: discord.User):
        noActiveChallenge = True

        for challenge in self.activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False
                self.activeChallenges.remove(challenge)

                self.writeToFile('activeChallenges', self.activeChallenges)

                response = Embed(title="Challenge removed", description=f'The challenge with the player: {player.mention} was removed', color=self.blue)
                await self.update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=self.red)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="update-txt", description="Takes all the txt files and changes the names to ids")
    async def updatetxt(self, interaction):
        print("Updating Leaderboard...")
        self.load_data()
        
        newLeaderboard = []
        newActiveChallenges = []
        newLockedPlayers = []

        print(interaction.guild)

        for person in self.leaderboard:
            user_id = await self.get_user_id(interaction.guild, person)
            newLeaderboard.append(user_id)

        self.writeToFile("leaderboard", newLeaderboard)
        self.leaderboard = newLeaderboard

        for challenge in self.activeChallenges:
            firstPlayer, secondPlayer, date = challenge.split(" - ")

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
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="update-ladder", description="Command for manually updating the ladder")
    async def updateladder(self, interaction):
        self.load_data()
        await self.update_ladder(interaction.guild)
        response = Embed(title="Ladder Updated", description="The ladder has been updated.", color=self.blue)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="test", description="Command")
    async def test(self, ctx):
        guild = ctx.guild
        channel_id = 1182411076307009607  # Todo: change channel id
        channel = guild.get_channel(channel_id)

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
                    firstPlayer, secondPlayer, date = challenge.split(" - ")
                    nr += 1

                    try:
                        firstPlayer = guild.get_member(int(firstPlayer)).display_name
                        secondPlayer = guild.get_member(int(secondPlayer)).display_name
                    except:
                        print(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')

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
            print(ladder_table_str)
            await channel.send(f"```\n{message}\n```")
        else:
            print("Error: Channel not found.")

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
        print("...Fetching old stats because the stats file is empty")
        channel_id = 1150003078796415054
        channel = self.bot.get_channel(channel_id)
        challenges = []
        
        async for message in channel.history(limit=1050, oldest_first=True):
            if message.author.id == 381063088842997763:
                if message.content.startswith('Challenge between'):
                    players = message.content.split(' between ')[1].split(' and ')
                    first_player = players[0].strip('@')
                    second_player = players[1].strip('@')[0:players[1].index(' is')]

                    first_playerID = first_player.replace('<@', '').replace('>', '')
                    second_playerID = second_player.replace('<@', '').replace('>', '')

                    challenges.append(f"{first_playerID},{second_playerID}")
                
            for embed in message.embeds:
                if embed.title == "Results accepted" and embed.description.startswith('Congratulations'):
                    # Look in the challenges list and give the win and loss to the people in the challenge
                    player = await self.get_user_id(guild, embed.description[16: embed.description.index("!")])

                    for challenge in challenges:
                        if player in challenge:
                            otherplayer = challenge.replace(player, "").replace(",", "")
                            self.update_stats(str(player), win=True)
                            self.update_stats(str(otherplayer), win=False)

                            challenges.remove(challenge)
                            break

    async def get_user_id(self, guild, person):
        #person = str.lower(person)
        
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
                print(f"Exception: {e}")

        return person

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))