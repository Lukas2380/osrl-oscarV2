import asyncio
import random
import re
import typing
import discord
from discord.ext import commands
from discord import app_commands, Embed
from datetime import datetime, timedelta
from data.helper_functions import *

class LadderBot_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.custom_on_ready())

        #*Info: the The current ladder will not be displayed after more than 123 people join because of the limit of 2000 symbols per message? So maybe make it multiple messages
        # things to do before launching
        #? todo: make the txt files more readable with having the names displayed aswell and just ignore them in the code
        # todo: update the info txt files
        #? todo: make command for setting the amount of guardian challenges
        # todo: make command for editing txt files
        #? todo: betting?

    async def custom_on_ready(self):
        #await asyncio.sleep(10)
        #await log("Bot is active in these guilds:")
        for guild in self.bot.guilds:
            #await log(str(guild))
            if len(stats) == 0:
                print("here")
                #await self.getoldstats(guild)
            await update_ladder(guild)

    def update_streak(self, player: str, win:bool, currentStreak: int):
        # This is called everytime the stats are updated
        playerInstreaksLeaderboard = False
        for entry in streaksLeaderboard:
            if player in entry:
                # Update the streak for the player entry
                playerInstreaksLeaderboard = True
                player, highestLossStreak, highestWinStreak = entry.split(" - ") 
                if win:
                    highestWinStreak = str(max(int(highestWinStreak), currentStreak))
                else:
                    highestLossStreak = str(max(int(highestLossStreak), abs(currentStreak)))

                # Update the streaks leaderboard
                streaksLeaderboard[streaksLeaderboard.index(entry)] = (f'{player} - {highestLossStreak} - {highestWinStreak}') 
                

        if not playerInstreaksLeaderboard:
            # Create a new entry for the player
            if win:
                streaksLeaderboard.append(f'{player} - 0 - 1') 
            else:
                streaksLeaderboard.append(f'{player} - 1 - 0') 

        writeToFile('streaksLeaderboard', streaksLeaderboard)

    def update_stats(self, player: str, win: bool):
        # This is called for each player everytime a challenge was finished
        playerInStats = False
        for stat in stats:
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
                stats[stats.index(stat)] = (f'{player} - {str(wins)} - {str(losses)} - {str(streak)}') 
                break

        if not playerInStats:
            # Create a new entry for the player
            if win:
                stats.append(f'{player} - 1 - 0 - 1') 
                streaksLeaderboard.append(f'{player} - 0 - 1') 
            else:
                stats.append(f'{player} - 0 - 1 - -1') 
                streaksLeaderboard.append(f'{player} - 1 - 0') 

        writeToFile('stats', stats)
        writeToFile('streaksLeaderboard', streaksLeaderboard)

    @app_commands.command(name="show-cooldowns", description="Show all the cooldowns of the people in the ladder")
    async def show_cooldowns(self, interaction):
        await interaction.response.defer()

        if len(cooldowns) > 0:
            output = ""

            for cooldown in cooldowns:
                time = datetime.strptime(cooldown.split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                remaining_time = time + timedelta(days=2) - datetime.now()
                
                if remaining_time < timedelta(0):
                    cooldowns.remove(cooldown)
                else:
                    player = await get_username(interaction.guild, cooldown.split(" - ")[0])

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
        await interaction.followup.send(await get_ladder(interaction.guild))

    @app_commands.command(name="show-active", description="Show active challenges")
    async def active(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await get_activeChallenges(interaction.guild))

    @app_commands.command(name="show-stats", description="Show the stats for the 1s ladder")
    async def show_stats(self, interaction):
        await interaction.response.defer()
        
        # Standard output if no stat is found
        stats = 'No stats found'
        playerindex = None
        sortedStatlist = {}

        if len(stats) > 0:
            stats = ""
            for stat in stats:
                player, wins, losses, streak = stat.split(" - ") 

                # Only get the stats if the player is on the leaderboard
                try:
                    playerindex = leaderboard.index(player) + 1 # Plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    playername = await get_username(interaction.guild, player)

                    # Write and format the stats
                    line = "W: {:<3} | L: {:<3} | S: {:<3} | {}\n".format(str(wins), str(losses), str(streak), playername[:21])
                    sortedStatlist[playerindex] = line
                
                playerindex = None

        # Sort the list
        for person in dict(sorted(sortedStatlist.items())):
            stats += sortedStatlist[person]
        
        await interaction.followup.send(f">>> ## Ladder Stats: \n### **Wins | Losses | Current Streak | Player **\n ```{stats}```")

    @app_commands.command(name="show-streaks", description="Shows the highest win and lossstreaks of the ladder")
    async def streaks(self, interaction):
        await interaction.response.defer()
        streaksLB = "No streaks found"
        playerindex = None
        sortedStatlist = {}
        
        if len(streaksLeaderboard) > 0:
            streaksLB = ''
            for entry in streaksLeaderboard:
                player, lossStreak, winStreak = entry.split(' - ') 

                try:
                    playerindex = leaderboard.index(player) + 1 #plus one because python says if 0 equals false
                except:
                    pass

                if playerindex:
                    playername = await get_username(interaction.guild, player)

                    # Write and format the streak stats
                    line = "W: {:<3} | L: {:<3} | {}\n".format(str(winStreak), str(lossStreak), playername[:30])
                    sortedStatlist[playerindex] = line
                
                playerindex = None

        for person in dict(sorted(sortedStatlist.items())):
            streaksLB += sortedStatlist[person]
        
        await interaction.followup.send(f">>> ## Ladder Streaks: \n### **Highest Winstreak | Highest Lossstreak | Player **\n ```{streaksLB}```")

    @app_commands.command(name="show-playerinfo", description="Get all the ladder information for one player")
    async def player_info(self, interaction, player: discord.User):
        await interaction.response.defer()
        playerID = str(player.id)
        playerIsLocked = False
        lockedStatus = ""
        playerRank = "/"

        # Show if person is locked
        for lockedPlayer in locked_players:
            if playerID in lockedPlayer:
                playerIsLocked = True
                lockedStatus = "Player is currently locked"
                playerRank = lockedPlayer.split(" - ")[0]

        if not playerIsLocked:
            # Show Position on the ladder
            for ladderEntry in leaderboard:
                if playerID in ladderEntry:
                    playerRank = leaderboard.index(ladderEntry)

            # Show if person is in an active challenge
            active_challenge_info = None
            for active_challenge in activeChallenges:
                if playerID in active_challenge:
                    firstPlayer, secondPlayer, date, isGuardian  = active_challenge.split(" - ") 
                    firstPlayerPosition = leaderboard.index(firstPlayer) + 1
                    secondPlayerPosition = leaderboard.index(secondPlayer) + 1

                    firstPlayerName = await get_username(interaction.guild, firstPlayer)
                    secondPlayerName = await get_username(interaction.guild, secondPlayer)
                    
                    if len(firstPlayerName+secondPlayerName) > 40: # 28 is the max length of the message (+nr+swords+date+spaces) that can be displayed on phone
                        firstPlayerName = firstPlayerName[:20]
                        secondPlayerName = secondPlayerName[:20]
                    
                    # Write and format the output
                    active_challenge_info = "{:^}. {} ⚔️ {}. {}\n".format(firstPlayerPosition, firstPlayerName, secondPlayerPosition, secondPlayerName)

        # Show Wins/Losses/Current Streak
        player_stats = None
        for entry in stats:
            if playerID in entry:
                player_stats = entry

        # Show Highest Win Streak/Highest Loss Streak
        player_streaks = None
        for streak in streaksLeaderboard:
            if playerID in streak:
                player_streaks = streak

        # Create the embed
        embed = discord.Embed(title=f"Stats for {player.display_name}", color=blue)
        embed.set_thumbnail(url=player.avatar.url)

        if playerIsLocked:
            embed.add_field(name="Locked Status", value=f"{lockedStatus}", inline=False)

        embed.add_field(name="Ladder Position", value=f"```{playerRank}```", inline=False)

        if not playerIsLocked:
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

        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True
                playerRank = leaderboard.index(str(player.id))

                if playerRank == 0:
                    playerIsFirst = True
                    break

                playerAboveId = leaderboard[playerRank - 1]
                
                # Check if anyone is already in a challenge
                for activeChallenge in activeChallenges:
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
                    
                    activeChallenges.append(f'{str(player.id)} - {playerAboveId} - {date} - false') 
                    writeToFile('activeChallenges', activeChallenges)
                    
                    cooldowns.append(f'{str(player.id)} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}') 
                    writeToFile('cooldowns', cooldowns)

                    response = Embed(title="Challenge scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(playerAboveId)).mention} \n\nis scheduled to be completed by: {date}', color=blue)

                    await update_ladder(interaction.guild)
                break

        if not playerIsInLeaderboard:
            response = Embed(title="Error", description=f'User: {player.mention} was not found in the leaderboard')

        if playerIsFirst:
            response = Embed(title="Error", description=f'{player.mention} there is no one left to challenge for you!')
        await interaction.followup.send(embed=response)

    def handleCooldowns(self, player):
        # This is called for the player who put in /challenge or /challenge-guardian
        for cooldown in cooldowns:
            if str(player.id) in cooldown:
                time = datetime.strptime(cooldown.split(" - ")[1], "%Y-%m-%d %H:%M:%S")
                remaining_time = time + timedelta(days=2) - datetime.now()

                # If cooldown ran out
                if remaining_time < timedelta(0):
                    cooldowns.remove(cooldown)
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
        maxGuardianChallenges = 1000 #todo Not restricted currently 
        guardianChallenges = 0

        for challenge in activeChallenges:
            if challenge.split(" - ")[3] == "true":
                guardianChallenges += 1

        if guardianChallenges >= maxGuardianChallenges:
            response = Embed(title="Error", description=f"{player.mention}, you can't guardian-challenge! \nThere is already the maximum amount of **{maxGuardianChallenges}** active guardian-challenges.", color=red)
            await interaction.followup.send(embed=response)

        # Set the guardianpositions to 3, and then in steps of five so 5,10... and so on
        guardian_positions = [3] + [i for i in range(5, len(leaderboard), 5)]

        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIsInLeaderboard = True

                # Get the next guardian in the ladder
                playerRank = leaderboard.index(str(player.id))
                nearest_guardian = next((guardian_pos for guardian_pos in sorted(guardian_positions, reverse=True) if guardian_pos <= playerRank), None) 

                if nearest_guardian is not None:
                    guardianId = leaderboard[nearest_guardian - 1]

                    # Check if anyone is already in a challenge
                    for activeChallenge in activeChallenges:
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

                        activeChallenges.append(f'{str(player.id)} - {guardianId} - {date} - true') 
                        writeToFile('activeChallenges', activeChallenges)

                        cooldowns.append(f'{str(player.id)} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}') 
                        writeToFile('cooldowns', cooldowns)

                        response = Embed(title="Guardian Challenge Scheduled", description=f'Challenge between: \n\n{player.mention} and {interaction.guild.get_member(int(guardianId)).mention} \n\nis scheduled to be completed by: {date}', color=blue)

                        await update_ladder(interaction.guild)
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

        for challenge in activeChallenges:
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
                        self.movePlayerinLeaderboard(challenger, leaderboard.index(challenged))
                        self.update_stats(challenger, True)
                        self.update_stats(challenged, False)
                        leaderboard_change = f"{challenger_user.mention} was moved above {challenged_user.mention} for winning the challenge."
                    else:  # Player is challenger and lost
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=red)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                else:
                    if result == "W": # Player is the one being challenged and won
                        response = Embed(title="Results accepted", description=f'Congratulations {player.mention}! You have won the challenge!', color=blue)
                        if isGuardianchallenge:
                            self.movePlayerinLeaderboard(challenger, leaderboard.index(challenger) + 1)
                            leaderboard_change = f"{challenger_user.mention} was moved down one spot for losing the guardian challenge."
                        self.update_stats(challenger, False)
                        self.update_stats(challenged, True)
                    else:  # Player is the one being challenged and lost
                        response = Embed(title="Results accepted", description=f'Unlucky {player.mention}, maybe you will win next time', color=red)
                        self.movePlayerinLeaderboard(challenger, leaderboard.index(challenged))
                        self.update_stats(challenger, True)
                        self.update_stats(challenged, False)
                        leaderboard_change = f"{challenger_user.mention} was moved above {challenged_user.mention} for winning the challenge."

                activeChallenges.remove(challenge)

                writeToFile('activeChallenges', activeChallenges)
                writeToFile('leaderboard', leaderboard)
                
                await update_ladder(interaction.guild)
                response.add_field(name="Leaderboard Change", value=leaderboard_change, inline=False)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=red)

        await interaction.followup.send(embed=response)

    def movePlayerinLeaderboard(self, player: str, position: int):
        # This is being called everytime there is a change in the leaderboard
        leaderboard.remove(player)
        leaderboard.insert(position, player) 

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
        await interaction.response.defer()
        alreadyIsInLadder = False
        player = interaction.user

        # Check if player is already in the leaderboard
        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant join the ladder", description=f'{player.mention}, you are already in the ladder', color=red)
                alreadyIsInLadder = True
                break

        if not alreadyIsInLadder:
            # Add player to the leaderboard
            leaderboard.append(str(player.id)) 
            writeToFile('leaderboard', leaderboard)
            
            response = Embed(title='Player added', description=f'Try not to get wrecked', color=blue)
            await update_ladder(interaction.guild)

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
                            player = await get_user_id(guild, embed.description[16: embed.description.index("!")])
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

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))