import math
import discord
from discord.ext import commands
from discord import app_commands, Embed
from data.helper_functions import *

#import pymongo
#from pymongo import MongoClient
#try:
#            cluster = MongoClient("mongodb+srv://dbUser:P3xrDm342xJ1vgbn@oscar.k8ijd1u.mongodb.net/?retryWrites=true&w=majority&appName=oscar")
#            db = cluster["osrl_oscarV2"]
#            collection = db["Betting"]
#            collection.insert_one({"better_id": "0123123", "amount_of_coins": 5})
#        except Exception as e:
#            print(e)

class Ladderbetting_cog(commands.Cog):
    #todo: dont bet on both sides
    #todo: need to somehow stop people from betting on games basically after the outcome is decided
    def __init__(self, bot):
        self.bot = bot

    def payout(winner, loser):
        # Add 100 coins to the wallet of the winner
        currentCoins = getWallet(winner)
        for wallet in wallets:
            if winner in wallet:
                wallets[wallets.index(wallet)] = f'{winner} - {str(int(currentCoins) + 100)}'
            elif loser in wallet:
                wallets[wallets.index(wallet)] = f'{winner} - {str(int(currentCoins) + 25)}'

        # Get every person who bet on this player and remove all the bets from this challenge
        betsToRemove = []
        winners = []
        poolOfLoserCoins = 0
        poolOfWinnerCoins = 0
        returnPerPlayerFromPool = 0

        for bet in bets:
            personWhoGotBetOn = bet.split(' - ')[0]
            personWhoBet = bet.split(' - ')[1]
            bettingAmount = bet.split(' - ')[2]

            if winner in personWhoGotBetOn:
                winners.append(f"{personWhoBet} - {bettingAmount}")
                poolOfWinnerCoins += int(bettingAmount)
            elif loser in personWhoGotBetOn:
                poolOfLoserCoins += int(bettingAmount)

            betsToRemove.append(bet)

        for bet in betsToRemove:
            personWhoBet = bet.split(' - ')[1]
            bettingAmount = bet.split(' - ')[2]

            if winner in bet.split(' - ')[0]:
                multiplier = int(bettingAmount) / int(poolOfWinnerCoins)
                winners[winners.index(f"{personWhoBet} - {bettingAmount}")] = f"{personWhoBet} - {bettingAmount} - {multiplier}"
            bets.remove(bet)

        writeToFile("bets", bets)

        if poolOfLoserCoins > 0:
            returnPerPlayerFromPool = int(math.ceil(poolOfLoserCoins / len(winners)))

        for winner in winners:
            winnerId = winner.split(' - ')[0]
            betOfWinner = winner.split(' - ')[1]
            multiplier = winner.split(' - ')[2]

            for wallet in wallets:
                oldWalletAmount = wallet.split(' - ')[1]
                if winnerId in wallet:
                    # New entry: "player id - (old wallet amount + bet + share of loser pool)"
                    wallets[wallets.index(wallet)] = f"{winnerId} - {str(int(oldWalletAmount) + int(betOfWinner) + int(int(returnPerPlayerFromPool) * float(multiplier)))}"
            writeToFile("wallets", wallets)

    def placeBet(self, user, player, amount):
        hasalreadyBet = False
        newBet = 0
        for bet in bets:
            if f'{player} - {user}' in bet:
                hasalreadyBet = True
                newBet = int(bet.split(' - ')[2]) + int(amount)
                bets[bets.index(bet)] = f"{player} - {user} - {newBet}"
        
        if not hasalreadyBet:
            bets.append(f'{player} - {user} - {amount}')
            newBet = int(amount)
        
        for wallet in wallets:
            if user in wallet:
                coinsInWallet = wallet.split(' - ')[1]
                wallets[wallets.index(wallet)] = f'{user} - {str(int(coinsInWallet) - int(amount))}'
        
        writeToFile("bets", bets)
        writeToFile("wallets", wallets)

        return newBet

    @app_commands.command(name="bet", description="Bet a certain amount of coins on a player that is currently in a ladder challenge")
    async def bet(self, interaction, player: discord.User, amount: int):
        await interaction.response.defer()
        coinsInWallet = getWallet(str(interaction.user.id))

        if player.id == interaction.user.id:
            response = Embed(title="You cant bet on yourself!", description=f'{player.mention}, it isnt allowed to bet on yourself!', color=red)
            await interaction.followup.send(embed=response)
            return

        response = Embed(title="Player not found", description=f'Maybe {player.mention} is not on the ladder or currently not in a challenge', color=red)
        for challenge in activeChallenges:
            if str(interaction.user.id) in challenge:
                response = Embed(title="You cant bet on this challenge!", description=f'{interaction.user.mention}, it isnt allowed to bet on a challenge which you are part of!', color=red)
            else:
                if str(player.id) in challenge:
                    if amount > int(coinsInWallet):
                        response = Embed(title="You cant bet that much!", description=f'{interaction.user.mention}, you dont have that many coins in your wallet!', color=red)
                    else:
                        coinsBet = self.placeBet(str(interaction.user.id), str(player.id), amount)
                        response = Embed(title="Bet placed", description=f'{interaction.user.mention} now bets {str(coinsBet)} coins on {player.mention}')
            break

        await interaction.followup.send(embed=response)

    @app_commands.command(name="show-wallets")
    async def show_wallets(self, interaction):
        await interaction.response.defer()
        walletOutput = "No wallets found"

        if len(wallets) > 0:
            walletOutput = ""
            for entry in wallets:
                userId, coins = entry.split(' - ')

                username = await get_username(interaction.guild, userId)
                walletOutput += f"{username} - {coins}\n"

        await interaction.followup.send(f">>> ## Wallets Leaderboard: \n### **Highest Winstreak | Highest Lossstreak | Player **\n ```{walletOutput}```")

    @app_commands.command(name="show-bets")
    async def show_bets(self, interaction):
        await interaction.response.defer()
        betOutput = "No bets found"

        if len(bets) > 0:
            betOutput = ""
            for entry in bets:
                playerId, userId, bet = entry.split(' - ')

                username = await get_username(interaction.guild, userId)
                playerName = await get_username(interaction.guild, playerId)
                betOutput += f"{username} bet {bet} coins on {playerName}\n"

        await interaction.followup.send("```" + betOutput + "```")


def getWallet(user):
    userInWallets = False

    for wallet in wallets:
        if user in wallet:
            userInWallets = True
            coins = wallet.split(' - ')[1]

    if not userInWallets:
        coins = 100
        wallets.append(f'{user} - {str(coins)}')
        writeToFile("wallets", wallets)

    return coins


async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(Ladderbetting_cog(bot))