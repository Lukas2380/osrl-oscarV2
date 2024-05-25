import asyncio
import random
import re
import typing
import discord
from discord.ext import commands
from discord import app_commands, Embed
from datetime import datetime, timedelta
from cogs.ladder_betting_cog import Ladderbetting_cog
from data.helper_functions import *

class LadderAdmin_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin-add", description="Add a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def add(self, interaction, player: discord.User, position: int):
        await interaction.response.defer()

        if player.bot:
            await interaction.followup.send(embed=Embed(title="Cant add this person to the ladder.", description="This person is a bot and cant be on the ladder.", color="red"))
            return

        alreadyIsInLadder = False

        # Check if player is already in the leaderboard
        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                response = Embed(title="Cant add player", description=f'{player.mention} is already in the ladder', color=red)
                alreadyIsInLadder = True
                break

        # Add the player at the desired position
        if not alreadyIsInLadder:
            if position > 0:
                leaderboard.insert(position-1,str(player.id)) 
                response=Embed(title="Player added", description=f'{player.mention} added in the {position} position', color=blue)
            elif position == 0:
                leaderboard.append(str(player.id)) 
                response=Embed(title="Player added", description=f'{player.mention} added in the last position', color=blue)

            writeToFile('leaderboard', leaderboard)
            await update_ladder(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-remove", description="Remove a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def remove(self, interaction, player: discord.User):
        await interaction.response.defer()
        response = Embed(title="Error", description=f'Player {player.mention} not recognized.', color=red)

        # Find the player and remove them from the leaderboard
        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                playerIndex = leaderboard.index(str(player.id))
                leaderboard.pop(playerIndex)

                writeToFile('leaderboard', leaderboard)

                # Remove the active challenge if one with the player is found
                for challenge in activeChallenges:
                    if str(player.id) in challenge:
                        await Ladderbetting_cog.removeAllBetsFromChallenge(self, interaction, challenge)
                        activeChallenges.remove(challenge)
                        break
                writeToFile('activeChallenges', activeChallenges)
                
                response = Embed(title="Player removed", description=f'Player {player.mention} removed from the ladder', color=blue)
                await update_ladder(interaction.guild)
                break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-viewlocked", description="View currently locked players") #todo: default_member_permissions=3
    #@app_commands.checks.has_permissions(administrator=True)
    #@app_commands.default_permissions(manage_messages=True)
    #@app_commands.checks.has_any_role("GC")
    async def view_locked(self, interaction):
        await interaction.response.defer()
        lines = ""

        # Go through all the locked players and output them
        if locked_players:
            for locked_player in locked_players:
                rank, playerId, date = locked_player.split(' - ') 
                username = await get_username(interaction.guild, playerId)
                lines += "{:<7} | {:>}. {:<15}\n".format(date, rank, username)
            await interaction.followup.send(f">>> ## Locked Players: \n### **Date Locked | Rank. Player **\n ```{lines}```")
        else:
            await interaction.followup.send(f">>> ## Locked Players: \n### **Date Locked | Rank. Player  **\n ```No players currently locked```")

    @app_commands.command(name="admin-lock", description="Lock a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def lock(self, interaction, player: discord.User):
        await interaction.response.defer()
        foundPlayerInLeaderboard = False
        alreadyLocked = False

        # Search for the player in the leaderboard
        for leaderboardEntry in leaderboard:
            if str(player.id) in leaderboardEntry:
                foundPlayerInLeaderboard = True

                # Search for the player in the list of already locked players
                for locked_player in locked_players:
                    if str(player.id) in locked_player:
                        alreadyLocked = True

                # Lock player
                if not alreadyLocked:
                    for challenge in activeChallenges:
                        if str(player.id) in challenge:
                            await Ladderbetting_cog.removeAllBetsFromChallenge(self, interaction, challenge)
                            activeChallenges.remove(challenge)

                    # Remove player from the leaderboard and add them to the locked player list
                    for leaderboardline in leaderboard:
                        if str(player.id) in leaderboardline:
                            leaderboardIndex = leaderboard.index(str(player.id))
                            leaderboard.pop(leaderboardIndex)

                            date = datetime.now().strftime("%x")
                            locked_players.append(f'{leaderboardIndex+1} - {player.id} - {date}') 

                    writeToFile('lockedPlayers', locked_players)
                    writeToFile('leaderboard', leaderboard)
                    writeToFile('activeChallenges', activeChallenges)

                    response=Embed(title='Player Locked', description=f'Player locked until further notice', color=blue)
                    await update_ladder(interaction.guild)
                    break

        if not foundPlayerInLeaderboard:
            response = Embed(title='Player not found', description=f'Player was not found in the leaderboard')
        elif alreadyLocked:
            response = Embed(title='Player already locked', description=f'The player is already in the locked player list')

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-unlock", description="Unlock a player")
    #@app_commands.checks.has_permissions(administrator=True)
    async def unlock(self, interaction, player: discord.User):
        await interaction.response.defer()
        response = Embed(title="Error", description=f"Didnt find {player.mention} in the locked player list", color=blue)
        
        # Find the player in the locked player list
        for locked_player in locked_players:
            if str(player.id) in locked_player:
                locked_players.remove(locked_player)

                # Insert them into the leaderboard
                rank, _, _ = locked_player.split(' - ') 
                leaderboard.insert(int(rank)-1, str(player.id)) 

                writeToFile('lockedPlayers', locked_players)
                writeToFile('leaderboard', leaderboard)

                response = Embed(title="Unlocked", description=f"{player.mention} unlocked", color=blue)
                await update_ladder(interaction.guild)
                break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-removechallenge", description="Removes the challenge which has the selected player in it")
    #@app_commands.checks.has_permissions(administrator=True)
    async def removeChallenge(self, interaction, player: discord.User):
        await interaction.response.defer()
        noActiveChallenge = True

        # Find the challenge and remove it
        for challenge in activeChallenges:
            if str(player.id) in challenge:
                noActiveChallenge = False
                await Ladderbetting_cog.removeAllBetsFromChallenge(self, interaction, challenge)
                activeChallenges.remove(challenge)
                writeToFile('activeChallenges', activeChallenges)

                response = Embed(title="Challenge removed", description=f'The challenge with the player: {player.mention} has been removed', color=blue)
                await update_ladder(interaction.guild)
                break

        if noActiveChallenge:
            response = Embed(title="Error", description=f'No active challenge with the player: {player.mention} found', color=red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-removecooldown", description="Removes the players cooldown")
    #@app_commands.checks.has_permissions(administrator=True)
    async def removeCooldown(self, interaction, player: discord.User):
        await interaction.response.defer()
        hasnoCooldown = True

        # Find the cooldown for the person and remove it
        for cooldown in cooldowns:
            if str(player.id) in cooldown:
                hasnoCooldown = False
                cooldowns.remove(cooldown)

                writeToFile('cooldowns', cooldowns)

                response = Embed(title="Cooldown removed", description=f'The cooldown for the player: {player.mention} has been removed', color=blue)
                break

        if hasnoCooldown:
            response = Embed(title="Error", description=f'The player: {player.mention} has no cooldown', color=red)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-updatetxt", description="Takes all the txt files and changes the names to ids")
    async def updatetxt(self, interaction):
        # This goes through all the txt files and tries to change the usernames to user ids
        await interaction.response.defer()
        await log("Updating Leaderboard...")
        leaderboard, activeChallenges, locked_players, stats, streaksLeaderboard, cooldowns, bets, wallets, activityBonusMessages, activityBonusVCTime, claimcoinsCooldown = load_data()
        
        newLeaderboard = []
        newActiveChallenges = []
        newLockedPlayers = []

        await log(interaction.guild)

        for person in leaderboard:
            user_id = await get_user_id(interaction.guild, person)
            newLeaderboard.append(user_id) 

        writeToFile("leaderboard", newLeaderboard)
        leaderboard = newLeaderboard

        for challenge in activeChallenges:
            firstPlayer, secondPlayer, date = challenge.split(" - ") 

            firstPlayerID = await get_user_id(interaction.guild, firstPlayer)
            secondPlayerID = await get_user_id(interaction.guild, secondPlayer)
            newActiveChallenges.append(f"{firstPlayerID} - {secondPlayerID} - {date} - false") 

        writeToFile("activeChallenges", newActiveChallenges)
        activeChallenges = newActiveChallenges

        for locked_player in locked_players:
            rank, username, date = locked_player.split(' - ') 
            user_id = await get_user_id(interaction.guild, username)
            newLockedPlayers.append(f"{rank} - {user_id} - {date}") 

        writeToFile("lockedPlayers", newLockedPlayers)
        locked_players = newLockedPlayers

        await update_ladder(interaction.guild)
        response = Embed(title="Text Files Updated", description="The text files have been updated.", color=blue)
        await interaction.followup.send(embed=response)

    @app_commands.command(name="admin-updateladder", description="Command for manually updating the ladder")
    async def updateladder(self, interaction):
        # This is a manual ladder update
        await interaction.response.defer()
        load_data()
        await update_ladder(interaction.guild)
        response = Embed(title="Ladder Updated", description="The ladder has been updated.", color=blue)
        await interaction.followup.send(embed=response)

#    @app_commands.command(name="admin-createshowmatch", description="Creates a showmatch for users to bet on.")
#    async def create_showmatch(self, interaction, player1: discord.User, player2: discord.User):
#        await interaction.response.defer()
#        members = interaction.guild.members
#        options = [discord.SelectOption(label=member.name, value=str(member.id)) for member in members if not member.bot]
#        
#        await interaction.followup.send("Please select users who can't bet:", view=UserSelectView(options))


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LadderAdmin_cog(bot))

#from discord.ui import View, Select

#class UserSelect(Select):
#    def __init__(self, options):
#        super().__init__(placeholder='Select users who can\'t bet...',
#                        min_values=1, max_values=len(options), options=options)

#    async def callback(self, interaction: discord.Interaction):
#        selected_users = [option.value for option in self.options if option.default]
#        await interaction.response.send_message(f"Selected users: {', '.join(selected_users)}")

#class UserSelectView(View):
#    def __init__(self, options):
#        super().__init__()
#        self.add_item(UserSelect(options))