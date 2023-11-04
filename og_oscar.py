from interactions import *
import os
import random
import discord
import datetime
from datetime import timedelta
from io import open
import json
#@slash_default_member_permission(Permissions.1015667077371138208)

with open('secrets.json') as f:
    TOKEN = json.load(f)["TOKEN"]
    
#@slash_default_member_permission(Permissions.1015667077371138208)
bot = Client(intents=Intents.DEFAULT)
# intents are what events we want to receive from discord, `DEFAULT` is usually fine

today= datetime.datetime.now()
logo = discord.File('logo.png')

with open('rrorder.txt','r+') as file:
    data=file.read()
    rrorder=data.split('\n')
rrorder.pop(-1)

with open('LB.txt','r+') as file:
    data=file.read()
    leaderboard=data.split('\n')
leaderboard.pop(-1)

def chaltest(p):
    for x in challenges:
        if p in x:
            return True

with open('chal.txt','r+') as file:
    data=file.read()
    challenges=data.split('\n')
    challenges.pop(-1)
with open('locked.txt','r+') as file:
    data=file.read()
    locked_players=data.split('\n')
    locked_players.pop(-1)

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

@slash_command(name='test',description='roles embed',default_member_permissions=3)
async def nerd(ctx: SlashContext): 
    response=Embed(title='test')
    await ctx.send(embed=response)

@slash_command(name='rolesembed',description='roles embed',default_member_permissions=3)
async def rolesembed(ctx: SlashContext): 
    with open('rolesintro.txt','r') as file:
        rolesintro = file.read()
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)
    channel = bot.get_channel(1015761028631511181)
    rolesintroembed=Embed(title='Assign your roles!',
    description=rolesintro,
    color=0x2ddaed)
    await channel.send(embed=rolesintroembed)
    serv=Embed(title='Ranks',
    description=f'What is the highest rank you have achieved?',
    color=0x2ddaed)
    serv.set_thumbnail(url='attachment://logo.png')
    await channel.send (embed=serv) 
    rankroles=[
        [
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="GC",
                label="Grandchampion",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="C",
                label="Champion",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="D",
                label="Diamond",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="P",
                label="Platinum",
            )
        ]
    ]
    await channel.send(components=rankroles)
    rankroles2=[
        [
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="G",
                label="Gold",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="S",
                label="Silver",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="B",
                label="Bronze",
            )
        ]
    ]
    await channel.send(components=rankroles2)
    
    serv=Embed(title='Region',
    description=f'What region do you mostly play in?',
    color=0x2ddaed)
    serv.set_thumbnail(url='attachment://logo.png')
    await channel.send (embed=serv) 
    regionroles=[
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="NA",
                label="NA",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="EU",
                label="EU",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="MENA",
                label="MENA",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="OCE",
                label="OCE",
            ),
        ]
    await channel.send(components=regionroles)
    
    serv=Embed(title='System/Console',
    description=f'What system or console do you play on?',
    color=0x2ddaed)
    serv.set_thumbnail(url='attachment://logo.png')
    await channel.send (embed=serv) 
    systemroles=[
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="PC",
                label="PC",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="PS",
                label="Playstation",
            ),     
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="XB",
                label="XBOX",
            ),   
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="SW",
                label="Switch",
            ),  
        ]
    await channel.send(components=systemroles)
    
    serv=Embed(title='Looking for friends roles',
    description=f'These roles are for if you want to be notified when others are looking for people to play with.',
    color=0x2ddaed)
    serv.set_thumbnail(url='attachment://logo.png')
    await channel.send (embed=serv) 
    LFTroles=[
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="RANK",
                label="Competetive",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="CAS",
                label="Casual/Private matches",
            ),     
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="EX",
                label="Extra Modes",
            ),   
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="TOUR",
                label="Tournaments",
            ),  
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="ALT",
                label="Alternate games",
            )
        ]
    await channel.send(components=LFTroles)
    serv=Embed(title='Additional Roles',
    description=f'These roles are specific interests that we offer in this discord! Choose any that you want to be a part of.',
    color=0x2ddaed)
    serv.set_thumbnail(url='attachment://logo.png')
    await channel.send (embed=serv) 
    addroles=[
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="CE",
                label="Community Events",
            ),
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="RLCS",
                label="RLCS Chat",
            ),     
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="1v1",
                label="1v1 Ladder",
            ),   
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="T",
                label="RL Trading",
            ),  
        ]
    await channel.send(components=addroles)
    addroles2=[
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="PCT",
                label="PC Help/Chat",
            ),  
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="PRIV",
                label="Private Matches",
            ),  
            Button( 
                style=ButtonStyle.PRIMARY,
                custom_id="M",
                label="Music Chat",
            ),  
        ]
    await channel.send(components=addroles2)
#Ranks
@component_callback("GC")
async def GC(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015691161530273843)
    if member.has_role(1015691161530273843):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
    
@component_callback("C")
async def C(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015690755857207366)
    if member.has_role(1015690755857207366):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
    
@component_callback("D")
async def D(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015702334170468442)
    if member.has_role(1015702334170468442):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
    
@component_callback("P")
async def P(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015690588034699295)
    if member.has_role(1015690588034699295):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
@component_callback("G")
async def G(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015691100092104744)
    if member.has_role(1015691100092104744):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
@component_callback("S")
async def S(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015690227525886105)
    if member.has_role(1015690227525886105):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
@component_callback("B")
async def B(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1015690200548126771)
    if member.has_role(1015690200548126771):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)  
#Regions
@component_callback("NA")
async def NA(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=980090542643875861)
    if member.has_role(980090542643875861):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
        
@component_callback("EU")
async def EU(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=980089673592471612)
    if member.has_role(980089673592471612):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
            
@component_callback("SAM")
async def SAM(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1102660707994062958)
    if member.has_role(1102660707994062958):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
            
@component_callback("MENA")
async def MENA(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1150952670182506557)
    if member.has_role(1150952670182506557):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
            
@component_callback("OCE")
async def OCE(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1138436300823855144)
    if member.has_role(1138436300823855144):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True) 
            
#Systems
@component_callback("PC")
async def PC(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=979396318235623444)
    if member.has_role(979396318235623444):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("PS")
async def PS(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=979396138119606293)
    if member.has_role(979396138119606293):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("XB")
async def XB(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=979396050508988507)
    if member.has_role(979396050508988507):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("SW")
async def SW(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=979396238866800772)
    if member.has_role(979396238866800772):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
#Additional Roles
@component_callback("CE")
async def CE(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1083388443427610676)
    if member.has_role(1083388443427610676):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("RLCS")
async def RLCS(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1083587652554604634)
    if member.has_role(1083587652554604634):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("1v1")
async def ladderrole(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1065797067710148661)
    if member.has_role(1065797067710148661):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("T")
async def Trading(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1083596167675400294)
    if member.has_role(1083596167675400294):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("PCT")
async def PCT(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1083588297584025600)
    if member.has_role(1083588297584025600):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("PRIV")
async def PRIV(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1083592526847545364)
    if member.has_role(1083592526847545364):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("M")
async def M(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1085402206347477102)
    if member.has_role(1085402206347477102):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)

@component_callback("RANK")
async def RANK(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1121808492265734214)
    if member.has_role(1121808492265734214):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("CAS")
async def CAS(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1121808992201605140)
    if member.has_role(1121808992201605140):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("EX")
async def EX(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1121809183071809636)
    if member.has_role(1121809183071809636):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("TOUR")
async def TOUR(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1121809378656387112)
    if member.has_role(1121809378656387112):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)
        
@component_callback("ALT")
async def ALT(ctx: ComponentContext):
    member = await bot.fetch_member(user_id=ctx.member.id,guild_id=979020400765841462)
    guild = await bot.fetch_guild(guild_id=979020400765841462)
    role = await guild.fetch_role(role_id=1121809580855410778)
    if member.has_role(1121809580855410778):
        await member.remove_role(role)
        await ctx.send("Role removed",ephemeral=True)
    else:
        await member.add_role(role)
        await ctx.send("Role assigned",ephemeral=True)

#
#LADDER BOT
#


@slash_command(name='results',description='Submit results of a match')
@slash_option(
    name="result",
    description="Result of match",
    required=True,
    opt_type=OptionType.STRING,
    choices=[
    SlashCommandChoice(name="W",value="w"),
    SlashCommandChoice(name="L",value="l")
    ]
    )
async def results(ctx: SlashContext,result:str): 
    result=str(result)
#message author wins
    if result=='w' or result=='W':
        w=''
    #assiging temp variable p to author name
        namet=ctx.member.display_name
        p=str(namet)
    #checking there is an active challenge with the author in it
        for x in challenges:
            if p in x:
                chal=x
                break
        else:
            embed=Embed(title='Error',description=f'No active challenge found',color=0xFF5733)
            await ctx.send (embed=embed)   
            return
    #Setting players with the challenge
        t1,t2,d=chal.split(' - ')
        if (p==t1):
            p1=t1
            p2=t2
            w=t1
        elif (p==t2):
            p1=t2
            p2=t1
            w=t2
    #assigning players their index numbers
        p1n = leaderboard.index(p1)
        p2n = leaderboard.index(p2)
        wn = leaderboard.index(w)
    #switching the players if needed, so player 1 is always the higher(lower number) player
        if (p1n > p2n):
            t=p2 
            p2=p1
            p1=t
            w=p2
    #removing challenge
        for y in challenges:
            if p1 in y:
                temp=challenges.index(y)
                challenges.pop(temp)
        with open('chal.txt','r+')as file:
            file.truncate(0)
            for x in challenges:
                file.write(x+'\n')
     
        embed=Embed(title='Results accepted',description=f'Congratulations {w}! You have won the match!',color=0x0ccff)
        await ctx.send (embed=embed)
        p1n = leaderboard.index(p1)
        p2n = leaderboard.index(p2)
        wn = leaderboard.index(w)
    #switching the players if the lower player won
        if (wn>p1n):
            leaderboard[p1n] = p2
            leaderboard[p2n] = p1
        
    #modifying the leaderboard document
        with open('LB.txt','r+')as file:
            for x in leaderboard:
                file.write(x+'\n')
#Message author loss    
    else:
        if result == 'l' or result=='L':
            print(leaderboard)
            w=''
        #assiging temp variable p to author name
            auth=ctx.member.display_name
            p=str(auth)
        #checking there is an active challenge with the author in it
            for x in challenges:
                if p in x:
                    chal=x
                    break
            else:
                embed=Embed(title='Error',description=f'No active challenge found',color=0xFF5733)
                await ctx.send (embed=embed)   
                return
        #Setting player 2
            t1,t2,d=chal.split(' - ')
            if (p==t1):
                p1=t1
                p2=t2
                w=t2
            elif (p==t2):
                p1=t2
                p2=t1
                w=t1
        #assigning players their index numbers
            p1n = leaderboard.index(p1)
            p2n = leaderboard.index(p2)
        #switching the players if needed, so player 1 is always the higher(lower number) player
            if (p1n > p2n):
                t=p2 
                p2=p1
                p1=t
                w=p1
        #removing challenge
            for y in challenges:
                if p1 in y:
                    pos=challenges.index(y)
                    challenges.pop(pos)
            with open('chal.txt','r+')as file:
                file.truncate(0)
                for x in challenges:
                    file.write(x+'\n')
         
            embed=Embed(title='Results accepted',description=f'Congratulations {w}! You have won the match!',color=0x0ccff)
            await ctx.send (embed=embed)
            p1n = leaderboard.index(p1)
            p2n = leaderboard.index(p2)
            wn = leaderboard.index(w)
            if (wn>p1n):
                leaderboard[p1n] = p2
                leaderboard[p2n] = p1
            
        #modifying the leaderboard document
            with open('LB.txt','r+')as file:
                for x in leaderboard:
                    file.write(x+'\n')
        else:
            embed=Embed(title='Error 404',description=f'Must use "w" or "l" for submission, please retry.\n Refer to #1v1-bot-info for more info',color=0x0ccff)
            await ctx.send (embed=embed)   


@slash_command(name='ladder',description='Show the current ladder')
async def ladder(ctx: SlashContext): 
    lad=''
    chals=''
    for x in leaderboard:
        p=1+leaderboard.index(x)
        p=str(p)
        lad=lad+(p+'. ' + x)
        if chaltest(x):
            lad=lad+':crossed_swords:'    
        lad=lad+'\n'
    embed=Embed(title='Current Ladder!',description=lad,color=0x0ccff)
    await ctx.send(embed=embed)
    
    
@slash_command(name='add',description='add a player',default_member_permissions=3)
@slash_option(
    name="player",
    description="Player being challenged",
    required=True,
    opt_type=OptionType.USER)
@slash_option(
    name="position",
    description="Position where player will be placed",
    required=True,
    opt_type=OptionType.INTEGER,
    min_value=0,
    max_value=len(leaderboard)+1)
async def add(ctx: SlashContext,player,position): 
    name=player.display_name
    pid=player.id
    p=position-1
    if position>0:
        leaderboard.insert(p,name)
        embed=Embed(title='Player added',description=f'<@{pid}> added in the {position} position',color=0x0ccff)
        await ctx.send(embed=embed)
    elif position==0:
        leaderboard.append(name)
    print(leaderboard)
    with open('LB.txt','r+')as file:
        for x in leaderboard:
            file.write(x+'\n')
            
@slash_command(name='r',description='Remove a player',default_member_permissions=3)
@slash_option(
    name="player",
    description="Player being removed",
    required=True,
    opt_type=OptionType.USER)
async def remove(ctx: SlashContext,player): 
    name=player.display_name
    if name in leaderboard:
    #removing player from leaderboard list
        y = leaderboard.index(name)
        leaderboard.pop(y)
    #removing player from leaderboard document
        with open('LB.txt','r+')as file:
            file.truncate(0)
            for x in leaderboard:
                file.write(x+'\n')
    #removing player from challenges list
        for y in challenges:
            if name in y:
                challenges.remove(y)
        #removing player from challenges document
            with open('chal.txt','r+')as file:
                file.truncate(0)
                for x in challenges:
                    file.write(x+'\n')
        embed=Embed(title='Player Removed',description=f'Player {name} removed from the ladder',color=0x0ccff)
        await ctx.send(embed=embed)
    else:
        embed=Embed(title='Error',description=f'Player {name} not recognized.',color=0xFF5733)
        await ctx.send(embed=embed)

@slash_command(name='challenge',description='Challenge the player above you')
@slash_option(
    name="player",
    description="Player being challenged",
    required=True,
    opt_type=OptionType.USER)
async def challenge(ctx: SlashContext,player): 
    name=player.display_name
    pid=player.id
    name=str(name)
    p1=name
    date = datetime.datetime.now()+timedelta(days=7)
    auth=ctx.member.display_name
    aid=ctx.member.id
    p2=str(auth)
    print(p1)
    print(p2)
    if p1 in leaderboard:
        p1n = leaderboard.index(p1)
        p2n = leaderboard.index(p2)
    #checking if the player is in a challenge
        for x in challenges:
            if p1 in x:
                embed=Embed(title='Error',description=f'That player is already in a challenge.',color=0xFF5733)
                await ctx.send (embed=embed)   
                return
            elif p2 in x:
                embed=Embed(title='Error',description=f"Don't be scared, you're already in a challenge.",color=0xFF5733)
                await ctx.send (embed=embed) 
                return
    #checking player challenged is the player above challenger
        if ((p2n - p1n)>1 or (p2n - p1n)<-1 ):
            embed=Embed(title='Error',description=f'Players listed are not eligible to play eachother',color=0xFF5733)
            await ctx.send (embed=embed)
            return
        c=p2+' - '+p1+' - '+(date.strftime("%x"))
        challenges.append(c)
    #modifying challenge document
        with open('chal.txt','w+')as file:
            for x in challenges:
                file.write(x+'\n')
        await ctx.send(f'Challenge between <@{pid}> and <@{aid}> is scheduled to be completed by {date.strftime("%x")}')
    else:
        embed=Embed(title='Error',description=f'Please enter players names accurately, I do not recognize those names.',color=0xFF5733)
        await ctx.send (embed=embed)
        
@slash_command(name='active',description='Show active challenges')
async def active(ctx: SlashContext): 
    act=''
#checks if there are challenges, if not sends error
    if len(challenges) > 0:
        for x in challenges:
            a=1+challenges.index(x)
            a=str(a)
            act=act+(a+'. '+x+'\n')

        embed=Embed(title=f'Active Challenges',description=act,color=0x0ccff)
        await ctx.send(embed=embed)
    else:
        embed=Embed(title=f'Active Challenges',description=f'No active challenges',color=0xFF5733)
        await ctx.send(embed=embed)


@slash_command(name='join',description='Join the ladder!')
async def join(ctx: SlashContext): 
    namet=ctx.member.display_name
    user=str(namet)
    leaderboard.append(user)
    with open('LB.txt','r+')as file:
        for x in leaderboard:
            file.write(x+'\n')
    embed=Embed(title='Player added',description=f'Try not to get wrecked',color=0x0ccff)
    await ctx.send(embed=embed)

@slash_command(name='l',description='Lock a player',default_member_permissions=3)
@slash_option(
    name="player",
    description="Player being locked",
    required=True,
    opt_type=OptionType.USER)
async def lock(ctx: SlashContext,player): 
    name=player.display_name     
    if name in leaderboard:
        for x in challenges:
            if name in x:
                challenges.remove(x)
        for x in leaderboard:
            if name in x:
                y = leaderboard.index(name)
                leaderboard.pop(y)
                y=y+1                
                y=str(y)
                date=today.strftime('%x')
                lo=y+' - '+name+' - '+(date)
                locked_players.append(lo)
    #adding player to locked document
        with open('locked.txt','w+') as file:
            for x in locked_players:
                file.write(x+'\n')
    #removing player from the leaderboard document
        with open('LB.txt','r+')as file:
            for x in leaderboard:
                file.write(x+'\n')
        embed=Embed(title='Player Locked',description=f'Player locked until further notice',color=0x0ccff)
        await ctx.send(embed=embed)
                
    else:
        embed=Embed(title=f'Error',description=f'Player not found',color=0xFF5733)
        await ctx.send(embed=embed)
        
@slash_command(name='view-locked',description='View currently locked players',default_member_permissions=3)
async def viewlocked(ctx: SlashContext):  
    lock=''
    if len(locked_players)>0:
        for x in locked_players:
            rank,name,date=x.split(' - ')
            lock=lock+(rank+'. ' + name + '........Date locked: '+ date + '\n')
        embed=Embed(title='Locked players',description=lock ,color=0x0ccff)
        await ctx.send(embed=embed)
        print(locked_players)
    else:        
        embed=Embed(title=f'Empty',description=f'No players currently locked',color=0xFF5733)
        await ctx.send(embed=embed)

@slash_command(name='unlock',description='Unlock a player',default_member_permissions=3)
@slash_option(
    name="player",
    description="Player being unlocked",
    required=True,
    opt_type=OptionType.USER)
async def unlock(ctx: SlashContext,player): 
    name=player.display_name       
#checks if player is in locked players
    for x in locked_players:
        if name in x:
            locked_players.remove(x)
            y,n,date=x.split(' - ')
            y=int(y)
            y=y-1
            leaderboard.insert(y,n)
        #removing player from the locked document
            with open('locked.txt','w+') as file:
                file.truncate(0)
                for x in locked_players:
                    file.write(x+'\n')
        #adding player to the leaderboard document
            with open('LB.txt','r+')as file:
                for x in leaderboard:
                    file.write(x+'\n')
            embed=Embed(title='Unlocked',description=f'Player unlocked' ,color=0x0ccff)
            await ctx.send(embed=embed)

@slash_command(name='cointoss',description='Toss a coin!')
async def cointoss(ctx: SlashContext):              
    r=random.randint(1,2)
    if r==1:
        embed=Embed(title='Result',description=f'Heads!' ,color=0x0ccff)
        await ctx.send(embed=embed)
    elif r==2:
        embed=Embed(title='Result',description=f'Tails!' ,color=0x0ccff)
        await ctx.send(embed=embed)
        
        
#
#INFO AND RULES
#

@slash_command(name='servrules',description='Resend the rules embed',default_member_permissions=3)
async def servrules(ctx: SlashContext): 
    channel = bot.get_channel(979020401621467178)
    with open('servrules.txt','r') as file:
        serv = file.read()
    serv=Embed(title='Old School Server Rules',
    description=serv,
    color=0x2ddaed)
    serv.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=serv)  
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)
    
@slash_command(name='servfaq',description='Resend the faq embed',default_member_permissions=3)
async def servfaq(ctx: SlashContext): 
    channel = bot.get_channel(1089183143711494254)
    with open('faq.txt','r') as file:
        faq = file.read()
    faq=Embed(title='Frequently Asked Questions',
    description=faq,
    color=0x2ddaed)
    faq.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=faq) 
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)    

@slash_command(name='anonrep',description='Resend the anonrep embed',default_member_permissions=3)
async def servanonrep(ctx: SlashContext): 
    channel = bot.get_channel(1099810839508303922)
    with open('anonrep.txt','r') as file:
        anonrep = file.read()
    report=Embed(title='Anonymous Reporting Form',
    description=anonrep,
    color=0x2ddaed)
    report.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=report)
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)
    
@slash_command(name='servdir',description='Resend the servdir embed',default_member_permissions=3)
async def servdir(ctx: SlashContext): 
    channel = bot.get_channel(1072889959226277978)
    with open('welcome.txt','r') as file:
        welcome = file.read()
    with open('rlconnect.txt','r') as file:
        rlconnect = file.read()
    with open('tmsearch.txt','r') as file:
        tmsearch = file.read()
    with open('coaching.txt','r') as file:
        coaching = file.read()
    servdirec=Embed(title='Old School Server Directory',color=0x2ddaed)
    servdirec.add_field(name='Welcome',value=welcome,inline=False)
    servdirec.add_field(name='RL Connect',value=rlconnect,inline=False)
    servdirec.add_field(name='Teammate Search',value=tmsearch,inline=False)
    servdirec.add_field(name='Coaches Corner',value=coaching,inline=False)
    servdirec.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=servdirec)  
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)
    
@slash_command(name='servstaff',description='Resend the server staff embed',default_member_permissions=3)
async def servstaff(ctx: SlashContext): 
    channel = bot.get_channel(1071431628666191962)
    with open('servstaff.txt','r') as file:
        servstaff = file.read()
    servstaffembed=Embed(title='Server Staff List',
    description=servstaff,
    color=0x2ddaed)
    servstaffembed.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=servstaffembed)
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)
    
@slash_command(name='ladderrules',description='Resend the ladder rules embed',default_member_permissions=3)
async def ladderrules(ctx: SlashContext): 
    channel = bot.get_channel(1063875272950165504)
    with open('1v1rules.txt','r') as file:
        rules = file.read()
    servstaffembed=Embed(title='1v1 Ladder Rules',
    description=rules,
    color=0x2ddaed)
    servstaffembed.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=servstaffembed)
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)   
    
@slash_command(name='ladderadmin',description='Resend the ladder admin info embed',default_member_permissions=3)
async def ladderadmininfo(ctx: SlashContext): 
    channel = bot.get_channel(1099011452389568673)
    with open('admininfo.txt','r') as file:
        admininfo = file.read()
    servstaffembed=Embed(title='1v1 Ladder admin commands',
    description=admininfo,
    color=0x2ddaed)
    servstaffembed.set_footer(text="lol nerds")
    await channel.send (embed=servstaffembed)
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)     
    
@slash_command(name='ladderinfo',description='Resend the ladder info embed',default_member_permissions=3)
async def ladderinfo(ctx: SlashContext): 
    channel = bot.get_channel(1099009440532938903)
    with open('1v1info.txt','r') as file:
        info = file.read()
    servstaffembed=Embed(title='1v1 Ladder Commands and Info',
    description=info,
    color=0x2ddaed)
    servstaffembed.set_footer(text="Thank you for being apart of this community, the staff work hard to ensure this is a safe and fun environment for everyone, and it wouldn't be possible without all of you")
    await channel.send (embed=servstaffembed)
    response=Embed(title='Embed Sent')
    await ctx.send(embed=response)      
    
    ##coaching commands
    
@slash_command(name='request',description='request a replay review!')
async def request(ctx: SlashContext): 
    name=ctx.member.display_name
    rrorder.append(name)
    rr=''
    for x in rrorder:
        p=1+rrorder.index(x)
        p=str(p)
        rr=rr+(p+'. ' + x)
        rr=rr+'\n'
        print (rr)
    channel = bot.get_channel(1132339056097902704)
    replayreview=Embed(title="Players waiting on replay reviews",
    description=rr,
    color=0x2ddaed)
    await channel.send (embed=replayreview)
    with open('rrorder.txt','r+')as file:
        for x in rrorder:
            file.write(x+'\n')
            
@slash_command(name='claim',description='claim a replay review')
@slash_option(
    name="player",
    description="claim a replay review",
    required=True,
    opt_type=OptionType.USER)
async def claim(ctx: SlashContext,player): 
    name=player.display_name
    x=rrorder.index(name)
    rrorder.pop(x)
    new=name+"....."+(ctx.member.display_name)
    rrorder.append(new)
    rr=''
    for x in rrorder:
        p=1+rrorder.index(x)
        p=str(p)
        rr=rr+(p+'. ' + x)
        rr=rr+'\n'
        print (rr)
    channel = bot.get_channel(1132339056097902704)
    replayreview=Embed(title="Players waiting on replay reviews",
    description=rr,
    color=0x2ddaed)
    await channel.send (embed=replayreview)
    with open('rrorder.txt','r+')as file:
        for x in rrorder:
            file.write(x+'\n')


            
@slash_command(name='complete',description='complete a replay review')
@slash_option(
    name="player",
    description="Player whos replay was completed",
    required=True,
    opt_type=OptionType.USER)
async def complete(ctx: SlashContext,player): 
    name=player.display_name
    for x in rrorder:
        if name in x:
            y=rrorder.index(x)
            rrorder.pop(y)
    rr=''
    for x in rrorder:
        p=1+rrorder.index(x)
        p=str(p)
        rr=rr+(p+'. ' + x)
        rr=rr+'\n'
        print (rr)
    channel = bot.get_channel(1132339056097902704)
    replayreview=Embed(title="Players waiting on replay reviews",
    description=rr,
    color=0x2ddaed)
    await channel.send (embed=replayreview)
    with open('rrorder.txt','r+')as file:
        for x in rrorder:
            file.write(x+'\n')
    
    
    
bot.start(TOKEN)