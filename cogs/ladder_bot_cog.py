import asyncio
import random
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

    async def custom_on_ready(self):
        #await asyncio.sleep(10)
        #await log("Bot is active in these guilds:")
        for guild in self.bot.guilds:
            #await log(str(guild))
            stats = statsTable.select("*").execute()
            if len(stats.data) == 0:
                await initialiseDatabasefromTextfiles(guild)
            #await update_ladder(guild)

    @app_commands.command(name="show-cooldowns", description="Show all the cooldowns of the people in the ladder")
    async def show_cooldowns(self, interaction):
        pass

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
        pass

    @app_commands.command(name="show-streaks", description="Shows the highest win and lossstreaks of the ladder")
    async def streaks(self, interaction):
        pass

    @app_commands.command(name="show-playerinfo", description="Get all the ladder information for one player")
    async def player_info(self, interaction, player: discord.User):
        pass

    @app_commands.command(name="challenge", description="Challenge the player above you")  
    async def challenge(self, interaction):
        pass

    @app_commands.command(name="challenge-guardian", description="Challenge the guardian above you")
    async def challenge_guardian(self, interaction):
        pass

    @app_commands.command(name="results", description="Submit the results of a challenge")
    async def results(self, interaction, result: typing.Literal["W", "L"]):
        pass

    @app_commands.command(name="join", description="Join the ladder!")
    async def join(self, interaction):
        await interaction.response.defer()
        playerID = await get_user_id(interaction.guild, interaction.user)

        try:
            # Add player to the leaderboard
            highestPosition = leaderboardTable.select("position").order("position", desc=True).limit(1).execute()
            leaderboardTable.insert({"user_id": playerID, "position":highestPosition.data[0]['position'] + 1}).execute()
            
            response = Embed(title='Player added', description=f'Try not to get wrecked', color=blue)
            await update_ladder(interaction.guild)
        except APIError as e:
            response = Embed(title="Cant join the ladder", description=f'{interaction.user.mention}, you are already in the ladder', color=red)
            print(e)

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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LadderBot_cog(bot))
