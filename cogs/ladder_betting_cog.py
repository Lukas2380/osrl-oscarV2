import asyncio
from datetime import datetime, timedelta
import math
import random
import time
import discord
from discord.ext import commands
from discord import app_commands, Embed
from data.helper_functions import *
import discord.utils

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
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to track the last claim time for each user
        self.lastBonusTime = {}  # Dictionary to track the last bonus time for each user
        self.cooldown_period = 30  # Cooldown period in seconds (e.g., 60 seconds for 1 minute)
        self.voiceEntryTime = {}
        # Define a lock to prevent race conditions
        self.claim_lock = asyncio.Lock()

        #? todo: maybe showmatches for coins?
        #? todo: buy custom roles /have selection (/createrole, /swaprole)
        #? todo: gambling on showmatches + rlcs betting (extra challenges file to bet on)
        #? todo: casino-style games (that sounds more like an extra cog)
        #? todo: maybe this: Custom Commands or Bot Interactions (insults)

    async def payout(self, interaction, winner, loser):
        # Add 100 coins to the wallet of the winner
        currentCoinsOfWinner = getWallet(winner)
        currentCoinsOfLoser = getWallet(loser)
        channel = interaction.guild.get_channel(commands_channel)

        for wallet in wallets:
            if winner in wallet:
                wallets[wallets.index(wallet)] = f'{winner} - {str(int(currentCoinsOfWinner) + 100)}'
                winnerUser = await self.bot.fetch_user(int(winner))
                await channel.send(f'{winnerUser.mention}, you gained 100 coins! Your new balance is {str(int(currentCoinsOfWinner) + 100)} coins.')
            elif loser in wallet:
                wallets[wallets.index(wallet)] = f'{loser} - {str(int(currentCoinsOfLoser) + 25)}'
                loserUser = await self.bot.fetch_user(int(loser))
                await channel.send(f'{loserUser.mention}, you gained 25 coins! Your new balance is {str(int(currentCoinsOfLoser) + 25)} coins.')

        # Get every person who bet on this player and remove all the bets from this challenge
        betsToRemove = []
        betsToIgnore = []
        winners = []
        losers = {}
        poolOfLoserCoins = 0
        poolOfWinnerCoins = 0

        for bet in bets:
            personWhoGotBetOn = bet.split(' - ')[0]
            personWhoBet = bet.split(' - ')[1]
            bettingAmount = bet.split(' - ')[2]
            time = bet.split(' - ')[3]
            betOnTime = True
            
            if winner in personWhoGotBetOn or loser in personWhoGotBetOn:
                if datetime.strptime(time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=10) > datetime.now():
                    betOnTime = False
                    betsToIgnore.append(bet)

                if winner in personWhoGotBetOn and betOnTime:               #if person bet on winner and bet is on time
                    winners.append(f"{personWhoBet} - {bettingAmount}")     #append "who bet - how much did they bet" to winners list
                    poolOfWinnerCoins += int(bettingAmount)                 #increase pool of winner coins by "how much did they bet"
                    betsToRemove.append(bet)                                #delete bet afterwards

                elif loser in personWhoGotBetOn and betOnTime:              #if person bet on loser and bet is on time
                    losers.setdefault(personWhoBet, 0)
                    losers[personWhoBet] += int(bettingAmount)              #put "who bet - how much did they bet" on losers dictionary

                    poolOfLoserCoins += int(bettingAmount)                  #increase pool of loser coins by "how much did they bet"
                    betsToRemove.append(bet)                                #delete bet afterwards

        # Delete all the bets that we just went through in that for loop + get the multiplier for how much the person receives after
        # Example: 3 bets: 100 coins bet on loser, 80 coins bet on winner, 20 coins bet on winner. 100 coins bet looses all, 80 coins bet gets 80% of looser coin pool ...
        for bet in betsToRemove:
            personWhoBet = bet.split(' - ')[1]
            bettingAmount = bet.split(' - ')[2]

            if winner in bet.split(' - ')[0]:
                multiplier = int(bettingAmount) / int(poolOfWinnerCoins)
                winners[winners.index(f"{personWhoBet} - {bettingAmount}")] = f"{personWhoBet} - {bettingAmount} - {multiplier}"
            bets.remove(bet)

        # return the coins from the bets that were placed to late
        coinsback = {}

        for bet in betsToIgnore:
            personWhoBet = bet.split(' - ')[1]
            amountBet = bet.split(' - ')[2]
            coinsback.setdefault(personWhoBet, 0)
            coinsback[personWhoBet] += int(amountBet)
            bets.remove(bet)

        for person in coinsback:
            for wallet in wallets:
                if person in wallet:
                    currentCoins = getWallet(person)
                    wallets[wallets.index(wallet)] = f'{person} - {str(int(currentCoins) + coinsback[person])}'
                    user = await self.bot.fetch_user(int(person))
                    await channel.send(f'{user.mention} (Bet: {coinsback[person]}), your coins were put back into your wallet because your bet was placed to close to the end of the challenge.')
                    break

        writeToFile("bets", bets)

        if poolOfLoserCoins == 0 or poolOfWinnerCoins == 0:
            # Refund everyone their bets
            for loser in losers:
                loserId = loser
                betOfLoser = int(losers[loser])
                for wallet in wallets:
                    oldWalletAmount = int(wallet.split(' - ')[1])
                    if loserId in wallet:
                        # Refund the loser's bet
                        newWalletAmount = oldWalletAmount + betOfLoser
                        wallets[wallets.index(wallet)] = f"{loserId} - {str(newWalletAmount)}"
                        # Notify the user
                        loserUser = await self.bot.fetch_user(int(loserId))
                        await channel.send(f'{loserUser.mention} (Bet: {betOfLoser}), there were no bets on the other side, so your coins have been refunded. Your balance is {newWalletAmount} coins.')
            
            for winner in winners:
                winnerId = winner.split(' - ')[0]
                betOfWinner = int(winner.split(' - ')[1])
                for wallet in wallets:
                    oldWalletAmount = int(wallet.split(' - ')[1])
                    if winnerId in wallet:
                        # Refund the winner's bet
                        newWalletAmount = oldWalletAmount + betOfWinner
                        wallets[wallets.index(wallet)] = f"{winnerId} - {str(newWalletAmount)}"
                        # Notify the user
                        winnerUser = await self.bot.fetch_user(int(winnerId))
                        await channel.send(f'{winnerUser.mention} (Bet: {betOfWinner}), there were no bets on the other side, so your coins have been refunded. Your balance is {newWalletAmount} coins.')
        else:
            # There are bets on both sides
            for winner in winners:
                winnerId = winner.split(' - ')[0]
                betOfWinner = int(winner.split(' - ')[1])
                multiplier = float(winner.split(' - ')[2])

                for wallet in wallets:
                    if winnerId in wallet:
                        oldWalletAmount = getWallet(winnerId)
                        gain = int(betOfWinner) + int(poolOfLoserCoins * multiplier)
                        # New entry: "player id - (old wallet amount + bet + share of loser pool)"
                        newWalletAmount = int(oldWalletAmount) + int(gain)
                        wallets[wallets.index(wallet)] = f"{winnerId} - {str(newWalletAmount)}"
                        # Notify the user
                        winnerUser = await self.bot.fetch_user(int(winnerId))
                        await channel.send(f'{winnerUser.mention} (Bet: {betOfWinner}), you gained {int(poolOfLoserCoins * multiplier)} coins! Your new balance is {newWalletAmount} coins.')

            for loser in losers:
                loserId = loser
                betOfLoser = int(losers[loser])
                walletAmount = getWallet(loserId)

                loserUser = await self.bot.fetch_user(int(loserId))
                await channel.send(f'{loserUser.mention} (Bet: {betOfLoser}), you lost {betOfLoser} coins! Your balance is {walletAmount} coins.')

                #for wallet in wallets:
                    #WalletAmount = int(wallet.split(' - ')[1])
                    #if loserId in wallet:
                        #newWalletAmount = oldWalletAmount - betOfLoser
                        #if newWalletAmount < 0:
                            #newWalletAmount = 0
                        #wallets[wallets.index(wallet)] = f"{loserId} - {str(newWalletAmount)}"
                        # Notify the user

            writeToFile("wallets", wallets)

        await assign_mr_moneybags_role(interaction.guild)

    async def placeBet(self, interaction, user, player, amount):        
        bets.append(f"{player} - {user} - {str(amount)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for wallet in wallets:
            if user in wallet:
                coinsInWallet = wallet.split(' - ')[1]
                wallets[wallets.index(wallet)] = f'{user} - {str(int(coinsInWallet) - int(amount))}'
        
        writeToFile("bets", bets)
        writeToFile("wallets", wallets)

        await assign_mr_moneybags_role(interaction.guild)

        return self.getBetsFromUserOnPlayer(user, player)

    async def removeAllBetsFromChallenge(self, interaction, challenge):
        channel = interaction.guild.get_channel(commands_channel)
        player1, player2, _, _ = challenge.split(' - ')
        coinsback = {}
        betstoRemove = []

        for bet in bets:
            if player1 in bet.split(' - ')[0] or player2 in bet.split(' - ')[0]:
                coinsback.setdefault(bet.split(' - ')[1], 0)
                coinsback[bet.split(' - ')[1]] += int(bet.split(' - ')[2])
                betstoRemove.append(bet)

        if len(betstoRemove) > 0:
            for bet in betstoRemove:
                bets.remove(bet)

            for person in coinsback:    
                for wallet in wallets:
                    if person in wallet:
                        currentCoins = getWallet(person)
                        wallets[wallets.index(wallet)] = f'{person} - {str(int(currentCoins) + coinsback[person])}'
                        user = await self.bot.fetch_user(int(person))
                        await channel.send(f'{user.mention} (Bet: {coinsback[person]}), your coins were put back into your wallet because the challenge wasnt completed.')
                        break

            writeToFile("bets", bets)
            writeToFile("wallets", wallets)

    def getBetsFromUserOnPlayer(self, userId, playerId):
        totalBet = 0

        for bet in bets:
            if f'{playerId} - {userId}' in bet:
                totalBet += int(bet.split(' - ')[2])

        return totalBet

    @app_commands.command(name="bet", description="Bet a certain amount of coins on a player that is currently in a ladder challenge")
    async def bet(self, interaction, player: discord.User, amount: int):
        await interaction.response.defer()
        alreadyBetOnOtherSide = False
        coinsInWallet = getWallet(str(interaction.user.id))

        if player.id == interaction.user.id:
            response = Embed(title="You cant place this bet!", description=f'{player.mention}, it isnt allowed to bet on yourself!', color=red)
            await interaction.followup.send(embed=response)
            return

        otherPlayer = ""

        for challenge in activeChallenges:
            if str(player.id) in challenge:
                player1, player2, _, _ = challenge.split(' - ')
                if str(player.id) == player1:
                    otherPlayer = player2
                else:
                    otherPlayer = player1
                break

        if otherPlayer == "":
            response = Embed(title="You cant place this bet!", description=f'{interaction.user.mention}, the player you are trying to bet on is not in a challenge.', color=red)
            await interaction.followup.send(embed=response)
            return

        for bet in bets:
            if f'{otherPlayer} - {interaction.user.id}' in bet:
                alreadyBetOnOtherSide = True
                response = Embed(title="You cant place this bet!", description=f'{interaction.user.mention}, you cant bet on both sides of a challenge.', color=red)

        if not alreadyBetOnOtherSide:
            response = Embed(title="Player not found", description=f'Maybe {player.mention} is not on the ladder or currently not in a challenge', color=red)
            for challenge in activeChallenges:
                if str(interaction.user.id) in challenge and str(player.id) in challenge:
                    response = Embed(title="You cant place this bet!", description=f'{interaction.user.mention}, it isnt allowed to bet on a challenge which you are part of!', color=red)
                elif str(player.id) in challenge:
                    if int(coinsInWallet) == 0:
                        response = Embed(title="You cant place this bet!", description=f'{interaction.user.mention}, you dont have any coins left in your wallet!', color=red)
                    else:
                        if amount > int(coinsInWallet):
                            amount = int(coinsInWallet)
                        coinsBet = await self.placeBet(interaction, str(interaction.user.id), str(player.id), amount)
                        response = Embed(title="Bet placed", description=f'{interaction.user.mention} now bets {str(coinsBet)} coins on {player.mention}')
                    break

        await assign_mr_moneybags_role(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="show-wallets", description="Displays the top 20 wallets with the most amount of coins")
    async def show_wallets(self, interaction):
        await interaction.response.defer()
        await interaction.followup.send(await get_wallets(interaction.guild))

    @app_commands.command(name="show-wallet", description="Only shows you your own wallet")
    async def show_wallet(self, interaction, player: discord.Member,):
        await interaction.response.defer()

        if player.bot:
            await interaction.followup.send(embed=Embed(title="Cant get this wallet", description="This person is a bot and doesnt have a wallet.", color=red))
            return

        user = str(player.id)
        walletAmount = getWallet(user)
        userName = await get_username(interaction.guild, user)
        currentBets = "No current bets."

        for bet in bets:
            playerId, betUser, coinsBet, timeBet = bet.split(' - ')
            if user == betUser:
                if currentBets == "No current bets.":
                    if datetime.strptime(timeBet, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=10) > datetime.now():
                        currentBets = f"🔴" + coloriseString(f"{coinsBet} coins on {await get_username(interaction.guild, playerId)}", "red") + "\t\n"
                    else:
                        currentBets = f"🟢" + coloriseString(f"{coinsBet} coins on {await get_username(interaction.guild, playerId)}", "green") + "\t\n"
                else:
                    if datetime.strptime(timeBet, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=10) > datetime.now():
                        currentBets += f"🔴" + coloriseString(f"{coinsBet} coins on {await get_username(interaction.guild, playerId)}", "red") + "\t\n"
                    else:
                        currentBets += f"🟢" + coloriseString(f"{coinsBet} coins on {await get_username(interaction.guild, playerId)}", "green") + "\t\n"

        response = Embed(title=f"{userName}`s wallet: ")

        response.add_field(name="**Currently available coins:**", value=f"```{walletAmount}```", inline=True)
        response.add_field(name="", value="", inline=True)
        response.add_field(name="", value="", inline=True)
        response.add_field(name="", value="", inline=True)
        response.add_field(name="", value="", inline=False)
        response.add_field(name="**Current bets:**", value=f"```ansi\n{currentBets}```")

        await assign_mr_moneybags_role(interaction.guild)

        await interaction.followup.send(embed=response)

    @app_commands.command(name="show-bets", description="Displays all the bets for the challenge with the selected player")
    async def show_bets(self, interaction, player: discord.User):
        await interaction.response.defer()
        selecedChallenge = ""
        otherplayer = ""
        betsOnPlayer = ""
        totalCoinsBetOnPlayer = 0
        betsOnOtherPlayer = ""
        totalCoinsBetOnOtherPlayer = 0

        noChallengeFound = True
        noBetsFound = True

        for challenge in activeChallenges:
            if str(player.id) in challenge:
                noChallengeFound = False
                if str(player.id) in challenge.split(" - ")[0]:
                    otherplayer = challenge.split(" - ")[1]
                else:
                    otherplayer = challenge.split(" - ")[0]
                break

        if noChallengeFound:
            response = Embed(title="No challenge found!", description=f'{interaction.user.mention}, there does not seem to be a challenge with that player!', color=red)
            await interaction.followup.send(embed=response)
            return

        for bet in bets:
            playerId, userId, betAmount, timeBet = bet.split(' - ')
            if str(player.id) in playerId or otherplayer in playerId:
                noBetsFound = False
                userName = await get_username(interaction.guild, userId)

                if str(player.id) in playerId:
                    if datetime.strptime(timeBet, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=10) > datetime.now():
                        betsOnPlayer += "🔴" + coloriseString(f"{userName} - {betAmount}", "red") + "\t\n"
                    else:
                        betsOnPlayer += "🟢" + coloriseString(f"{userName} - {betAmount}", "green") + "\t\n"
                        totalCoinsBetOnPlayer += int(betAmount)
                elif otherplayer in playerId:
                    if datetime.strptime(timeBet, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=10) > datetime.now():
                        betsOnOtherPlayer += "🔴" + coloriseString(f"{userName} - {betAmount}", "red") + "\t\n"
                    else:
                        betsOnOtherPlayer += "🟢" + coloriseString(f"{userName} - {betAmount}", "green") + "\t\n"
                        totalCoinsBetOnOtherPlayer += int(betAmount)

        if noBetsFound:
            response = Embed(title="No bets found!", description=f'{interaction.user.mention}, there arent any bets on this challenge!', color=red)
            await interaction.followup.send(embed=response)
            return

        playerUsername = await get_username(interaction.guild, str(player.id))
        otherPlayerUsername = await get_username(interaction.guild, otherplayer)
        otherplayerUser = interaction.guild.get_member(int(otherplayer))
        totalCoinsBet = totalCoinsBetOnPlayer + totalCoinsBetOnOtherPlayer

        selecedChallenge = playerUsername + " ⚔️ " + otherPlayerUsername
        response = Embed(title=selecedChallenge, description=f"Some bets might not be counted if they were submitted too late.\n```ansi\n🟢{coloriseString('Green', 'green')} = Will currently be counted\n🔴{coloriseString('Red', 'red')} = Will currently not be counted```")

        try:
            # Calculate and format the odds ratio for the first player
            odds_ratio_player = self.calculate_odds_ratio(totalCoinsBet, totalCoinsBetOnPlayer)

            # Calculate and format the odds ratio for the other player
            odds_ratio_other_player = self.calculate_odds_ratio(totalCoinsBet, totalCoinsBetOnOtherPlayer)
        except ZeroDivisionError:
            odds_ratio_player = "N/A"
            odds_ratio_other_player = "N/A"

        # Add the fields to the response
        response.add_field(
            name="",
            value="{}:\n{} {}\n{} {}".format(player.mention, '**Total bets:**', totalCoinsBetOnPlayer, '**Odds ratio: **', odds_ratio_player),
            inline=True
        )

        response.add_field(
            name="",
            value="{}:\n{} {}\n{} {}".format(otherplayerUser.mention, '**Total bets:**', totalCoinsBetOnOtherPlayer, '**Odds ratio: **', odds_ratio_other_player),
            inline=True
        )

        if betsOnPlayer == "":
            betsOnPlayer = "N/A"
        if betsOnOtherPlayer == "":
            betsOnOtherPlayer = "N/A"

        response.add_field(name=" ", value=" ", inline=False)
        response.add_field(name=f"Bets on {playerUsername}", value=f"```ansi\n{betsOnPlayer}```", inline=True)
        response.add_field(name=f"Bets on {otherPlayerUsername}", value=f"```ansi\n{betsOnOtherPlayer}```", inline=True)

        await interaction.followup.send(embed=response)

    def calculate_odds_ratio(self, total_bets, player_bets):
        ratio = total_bets / player_bets
        
        # Format the ratio based on the decimal part
        if ratio.is_integer():
            # If the ratio is an integer, format as a whole number
            formatted_ratio = f"{int(ratio)}"
        else:
            # Format with one or two decimal places as needed
            formatted_ratio = f"{ratio:.2f}"
            
            # Remove trailing zeros and decimal point if necessary
            if formatted_ratio.endswith('0'):
                formatted_ratio = formatted_ratio.rstrip('0')
            if formatted_ratio.endswith('.'):
                formatted_ratio = formatted_ratio.rstrip('.')
        
        return f"1 : {formatted_ratio}"

    @app_commands.command(name="claim-coins", description="With this command you can claim your daily coins for betting on the 1s ladder.")
    async def claim_coins(self, interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        current_time = datetime.now()

        # Lock the critical section to   prevent multiple claims
        async with self.claim_lock:
            # Check the last claim time for the user
            if user_id in claimcoinsCooldown:
                # Convert last_claim_date from string to datetime
                last_claim_date = datetime.fromisoformat(claimcoinsCooldown[user_id])

                # Calculate the time difference since the last claim
                time_since_last_claim = current_time - last_claim_date

                # Calculate the remaining time until the user can claim again
                remaining_time = timedelta(days=1) - time_since_last_claim
                
                if remaining_time > timedelta(0):
                    # Calculate the remaining days, hours, minutes, and seconds
                    days, seconds = divmod(remaining_time.total_seconds(), 86400)
                    hours, seconds = divmod(seconds, 3600)
                    minutes, seconds = divmod(seconds, 60)
                    
                    # Create an embed with red color and the remaining time
                    embed = Embed(
                        title="Your daily coin cooldown has not run out yet!",
                        description=f"You still have to wait: **{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds** \nbefore you can claim again.",
                        color=red
                    )

                    # Send the embed as a response
                    await interaction.followup.send(embed=embed)
                    return

            # Allow the user to claim coins
            coins_in_wallet = int(getWallet(user_id))
            coins_to_add = random.randint(1, 25)
            # Retrieve activity bonus coins from both sources
            activityCoinsVC = activityBonusVCTime.get(str(user_id), 0)
            activityCoinsMessages = activityBonusMessages.get(str(user_id), 0)

            for wallet in wallets:
                if user_id in wallet:
                    wallets[wallets.index(wallet)] = f"{user_id} - {coins_in_wallet + coins_to_add + activityCoinsVC + activityCoinsMessages}"
                    await log(f"{await get_username(interaction.guild, user_id)} (Had: {coins_in_wallet}, Random: {coins_to_add}, VC: {activityBonusVCTime.get(str(user_id), 0)}, Messages: {activityBonusMessages.get(str(user_id), 0)})")

            activityBonusVCTime[str(user_id)] = 0
            activityBonusMessages[str(user_id)] = 0

            # Update the last claim time for the user
            claimcoinsCooldown[user_id] = str(current_time)

            writeDictToFile("wallets_activityBonusMessages", activityBonusMessages)
            writeDictToFile("wallets_activityBonusVCTime", activityBonusVCTime)
            writeDictToFile("claimcoins_cooldown", claimcoinsCooldown)

            await assign_mr_moneybags_role(interaction.guild)

            await interaction.followup.send(
                embed=Embed(
                    title="Coins added",
                    description=f"{coins_to_add + activityCoinsVC + activityCoinsMessages} coins were added to your wallet!\nYou now have **{coins_in_wallet + coins_to_add + activityCoinsVC + activityCoinsMessages}** coins.",
                    color=green
                )
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if channelisValid(message.channel.id):
            # Add to activity bonus
            if message.author.id != self.bot.user.id:
                user_id = str(message.author.id)
                current_time = time.time()

                # Check if the user has a last bonus time
                if user_id in self.lastBonusTime:
                    last_bonus_time = self.lastBonusTime[user_id]
                    # Calculate the time difference since the last bonus
                    time_difference = current_time - last_bonus_time

                    # If the time difference is less than the cooldown period, skip awarding bonus
                    if time_difference < self.cooldown_period:
                        return

                activityBonusMessages.setdefault(str(message.author.id), 0)
                if activityBonusMessages[str(message.author.id)] < 25:
                    activityBonusMessages[str(message.author.id)] += 2
                    if activityBonusMessages[str(message.author.id)] > 25:
                        activityBonusMessages[str(message.author.id)] = 25
                    await log(f"Added 2 coins to {message.author.name}'s wallet, they now have: {activityBonusMessages[str(message.author.id)]}")
                    writeDictToFile("wallets_activityBonusMessages", activityBonusMessages)

                self.lastBonusTime[user_id] = current_time

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # If a user joins a voice channel
        if before.channel is None and after.channel is not None:
            if not channelisValid(after.channel):
                return
            self.voiceEntryTime[member.id] = time.time()

        # If a user leaves a voice channel
        if before.channel is not None and after.channel is None:
            if not channelisValid(after.channel):
                return
            entry_time = self.voiceEntryTime.get(member.id)
            if entry_time:
                # Calculate the time spent in the voice channel
                time_spent = time.time() - entry_time
                
                # Define the reward rate: 2 coins for every 10 minutes
                reward_rate = 2 / 600  # 2 coins per 600 seconds (10 minutes)
                
                # Calculate the reward based on the time spent
                reward = int(time_spent * reward_rate)
                
                # Add the reward to the user's activity bonus wallet
                activityBonusVCTime.setdefault(str(member.id), 0)
                if activityBonusVCTime[str(member.id)] + reward < 25:
                    activityBonusVCTime[str(member.id)] += reward
                    await log(f"Added {reward} coins to {member.display_name}'s wallet for spending {time_spent / 60:.2f} minutes in voice channels. Total activity coins: {activityBonusVCTime[str(member.id)]}")
                else:
                    activityBonusVCTime[str(member.id)] = 25
                    await log(f"Set {member.display_name}'s wallet to {activityBonusVCTime[str(member.id)]} for being in vc. ")
                writeDictToFile("wallets_activityBonusVCTime", activityBonusVCTime)
                
                # Reset the entry time
                del self.voiceEntryTime[member.id]

def channelisValid(channelid):
    # list of channels which shouldnt be counted towards the coin reward since they are mod only for example
    adminCommands = 1099011452389568673
    adminChat = 1083545029064273940
    adminCommandChannel = 1093592217353998336
    problemChildren = 1272687110851264614
    coachesChat = 1071486425041747968
    communityAnnouncements = 1083388944265252904
    crossPlatformGameList = 1108592729384038440

    afkvc = 1149912179244531772
    modvc = 1071523960082141234

    if channelid in [adminCommands, adminChat, adminCommandChannel, problemChildren, coachesChat, communityAnnouncements, crossPlatformGameList, afkvc, modvc]:
        return False

    return True

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