red = 0xFF5733
blue = 0x0CCFFF

osrl_Server = 979020400765841462
log_channel = 1199387324904112178
bot_instance = None

def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot

async def log(output: str, isError: bool = False):
    global bot_instance
    
    if bot_instance is None:
        raise ValueError("Bot instance not set. Call set_bot_instance with a valid bot instance.")

    guild = bot_instance.get_guild(osrl_Server)
    channel = guild.get_channel(log_channel)
    
    if isError:
        output = f"```Error``` \n<@381063088842997763>: \n ``` {output}```"
    else:
        output = f"```{output}```"
    
    await channel.send(output)
