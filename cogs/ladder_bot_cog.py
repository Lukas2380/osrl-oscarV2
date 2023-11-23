import random
import typing
import discord
from discord.ext import commands
from discord import app_commands, Embed
from datetime import datetime, timedelta
from table2ascii import table2ascii

class LadderBot_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_data()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
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

    def writeToFile(self, file: str, mylist: list):
        with open(f'./data/ladder/{file}.txt', "w") as file:
            for entry in mylist:
                file.write(entry+'\n')

    async def update_ladder(self, guild):
        channel_id = 1176131566741762078  # Replace this with your channel ID
        channel = guild.get_channel(channel_id)

        if channel:
            ladder_table = "Rank - Player - Challenge - Wins - Losses - Streak"
            ladder_table += "```\n"
            active_challenges = 'No active challenges'

            # Check if there are any entries in the leaderboard
            if self.leaderboard:
                
                for person in self.leaderboard:
                    wins = 0
                    losses = 0
                    streak = 0
                    swords = ''
                    
                    # Check if the person is in the activeChallenges list
                    for element in self.activeChallenges:
                        if person in element:
                            swords = "⚔️"  # Unicode character for crossed swords emoji

                    for element in self.stats:
                        if person in element:
                            user, wins, losses, streak = element.split(" - ")

                    try:
                        username = guild.get_member(int(person)).display_name
                        ladder_table += "- {:<20} |{:<2}| W: {:<3} | L: {:<3} | S: {:<3}\n".format(username, swords, wins, losses, streak)
                    except:
                        await channel.send(f'Error while trying to get the username of the user: {person}')

            ladder_table += "```\n"

            # Active Challenges
            if len(self.activeChallenges) > 0:
                active_challenges = "First Player - Second Player - Date\n"
                active_challenges += "```\n"
                
                for challenge in self.activeChallenges:
                    firstPlayer, secondPlayer, date = challenge.split(" - ")

                    try:
                        firstPlayer = guild.get_member(int(firstPlayer)).display_name
                        secondPlayer = guild.get_member(int(secondPlayer)).display_name
                        active_challenges += "- {:<15} - {:<15} - {:<10}\n".format(firstPlayer, secondPlayer, date)
                    except:
                        await channel.send(f'Error while trying to get the username of one of these users: {firstPlayer}/{secondPlayer}')

                active_challenges += "```\n"

            # Construct the embed
            response = Embed(title='Current Ladder and Active Challenges', color=0x0ccff)
            response.add_field(name='Current Ladder:', value=ladder_table, inline=False)
            response.add_field(name='Active Challenges:', value=active_challenges, inline=False)

            # Find and delete the previous embed
            async for message in channel.history(limit=5):  # Adjust limit as needed
                if message.author == guild.me and message.embeds:
                    for embed in message.embeds:
                        if embed.title == 'Current Ladder and Active Challenges':
                            await message.delete()
                            break

            # Send the updated embed
            await channel.send(embed=response)
        else:
            print("Error: Channel not found.")

    def update_stats(self, player: str, win: bool):
        playerInStats = False
        for stat in self.stats:
            if player in stat:
                playerInStats = True
                player, wins, losses, streak = stat.split(' - ')
                if win:
                    wins = int(wins) + 1
                    streak = int(streak) + 1
                else:
                    losses = int(losses) + 1
                    if int(streak) > 0:
                        streak = 0
                    else:
                        streak = int(streak) - 1

                self.stats[self.stats.index(stat)] = (f'{player} - {str(wins)} - {str(losses)} - {str(streak)}')
                break

        if not playerInStats:
            if win:
                self.stats.append(f'{player} - 1 - 0 - 1')
            else:
                self.stats.append(f'{player} - 0 - 1 - 0')

        self.writeToFile('stats', self.stats)

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

        response = Embed(title='Current Ladder: ', description=ladder, color=0x0ccff)
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
                

        response = Embed(title='Active Challenges ', description=activeChallenges, color=0x0ccff)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="stats", description="Show the stats for the 1s ladder")
    async def stats(self, interaction):
        stats = 'No stats found'

        if len(self.stats) > 0:
            stats = ''

            for stat in self.stats:
                player, wins, losses, streak = stat.split(" - ")

                try:
                    player = interaction.guild.get_member(int(player)).display_name
                    stats += f'{str(player)} | W: {str(wins)} | L: {str(losses)} | S: {str(streak)}\n'
                except:
                    await interaction.response.send_message(f'Error while trying to get the username of one of the user: {player}')

        response = Embed(title='Ladder Stats: ', description=stats, color=0x0ccff)
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

                playerAboveId = self.leaderboard[playerRank - 1 ]
                
                # Check if anyone is already in a challenge
                for activeChallenge in self.activeChallenges:
                    if str(player.id) in activeChallenge:
                        playerAlreadyInChallenge = True
                        response = Embed(title="Error", description="Don't be scared, you're already in a challenge.", color=0xFF5733)
                        break
                    elif playerAboveId in activeChallenge:
                        playerAboveAlreadyInChallenge = True
                        response = Embed(title="Error", description="The player above is already in a challenge", color=0xFF5733)
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

    @app_commands.command(name="guardian", description="Challenge a selected guardian of the ladder")
    async def guardian(self, interaction, guardian: discord.User):
        response = Embed(title="Error", description=f'This function is not implemented yet', color=0xFF5733)
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
                    response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=0x0ccff)
                    
                    if playerIndex > otherPlayerIndex:
                        self.leaderboard[winnerIndex] = str(player.id)
                        self.leaderboard[winnerIndex+1] = otherPlayer
                    
                    self.update_stats(str(player.id), True)
                    self.update_stats(otherPlayer, False)

                else:
                    response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=0xFF5733)

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
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=0xFF5733)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
        alreadyIsInLadder = False
        player = interaction.user

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant join the ladder", description=f'{player.mention}, you are already in the ladder', color=0xff5733)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            self.leaderboard.append(str(player.id))
            self.writeToFile('leaderboard', self.leaderboard)
            
            response = Embed(title='Player added', description=f'Try not to get wrecked', color=0x0ccff)
            await self.update_ladder(interaction.guild)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="add", description="Add a player")
    async def add(self, interaction, player: discord.User, position: int):
        alreadyIsInLadder = False

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant add player", description=f'{player.mention} is already in the ladder', color=0xff5733)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            if position > 0:
                self.leaderboard.insert(position-1,str(player.id))
                response=Embed(title="Player added", description=f'{player.mention} added in the {position} position', color=0x0ccff)
            elif position == 0:
                self.leaderboard.append(str(player.id))
                response=Embed(title="Player added", description=f'{player.mention} added in the last position', color=0x0ccff)

            self.writeToFile('leaderboard', self.leaderboard)
            
            await self.update_ladder(interaction.guild)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="remove", description="Remove a player")
    async def remove(self, interaction, player: discord.User):
        response = Embed(title="Error", description=f'Player {player.mention} not recognized.', color=0xFF5733)

        for leaderboardEntry in self.leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIndex = self.leaderboard.index(str(player.id))
                self.leaderboard.pop(playerIndex)

                self.writeToFile('leaderboard', self.leaderboard)

                for challenge in self.activeChallenges:
                    if str(player.id) in challenge:
                        self.activeChallenges.remove(challenge)
                        break
                
                response = Embed(title="Player removed", description=f'Player {player.mention} removed from the ladder', color=0x0ccff)
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
        response = Embed(title='Result:', description=result, color=0x0ccff)
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
                color=0x0ccff
            )
        else:
            response = Embed(
                title='Empty',
                description='No players currently locked',
                color=0xFF5733
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

                    response=Embed(title='Player Locked', description=f'Player locked untilf further notice', color=0x0ccff)
                    await self.update_ladder(interaction.guild)
                    break

        if not foundPlayerInLeaderboard:
            response = Embed(title='Player not found', description=f'Player was not found in the leaderboard')
        elif alreadyLocked:
            response = Embed(title='Player already locked', description=f'The player is already in the locked player list')

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="unlock", description="Unlock a player")
    async def unlock(self, interaction, player: discord.User):

        response = Embed(title="Error", description=f"Didnt find {player.mention} in the locked players", color=0x0ccff)
        
        for locked_player in self.locked_players:
            if str(player.id) in locked_player:
                self.locked_players.remove(locked_player)

                rank, playerName, date = locked_player.split(' - ')
                self.leaderboard.insert(int(rank)-1, str(player.id))

                self.writeToFile('lockedPlayers', self.locked_players)
                self.writeToFile('leaderboard', self.leaderboard)

                response = Embed(title="Unlocked", description=f"{player.mention} unlocked", color=0x0ccff)
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

                response = Embed(title="Challenge removed", description=f'The challenge with the player: {player.mention} was removed', color=0x0ccff)
                await self.update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=0xFF5733)

        await interaction.response.send_message(embed=response)

    @app_commands.command(name="update-txt", description="Takes all the txt files and changes the names to ids")
    async def updatetxt(self, interaction):
        response = Embed(title="Error", description=f'This function is not implemented yet', color=0xFF5733)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="get-oldstats", description="Goes through all the /challenge and /results commands to get all the stats")
    async def getoldstats(self, interaction):
        response = Embed(title="Error", description=f'This function is not implemented yet', color=0xFF5733)
        await interaction.response.send_message(embed=response)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))