import SettingsAPI_Disc
import discord
from discord.ext import commands

import sys
 # Adjust the path as needed
import os

from discordsec2Tasks import sec2_FUNCTION
import ollama
#ollama 
url = "http://localhost:11434/api/generate"

logger = SettingsAPI_Disc.logging.getLogger("bot")
sec2_Reply_Status = True
def run():
    intents = discord.Intents.default()
    intents.message_content = True  # Enable message content intent if needed
    intents.members = True # Enable members intent if needed
    global sec2_Reply_Status     
    
    bot = commands.Bot(command_prefix='~', intents=intents)
    bot.sec2_Reply_Status = True

    @bot.event
    async def on_ready():
        logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print("____________")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="2sec is online!"))
        print(f'Bot is ready!')
        print("____________")

    @bot.event
    async def on_message(message):
    
        if message.author == bot.user:
            return print("Message ignored or not a command.")
        
        if message.content.startswith('!'):
            command_name = message.content[1:].split()[0]
            if bot.get_command(command_name):
                await bot.process_commands(message)
                return
            
        elif sec2_Reply_Status:
            if message.channel.name == "bot-cmds": 
                global contexts
                if message.content.startswith('2S'):
                    print(f"Received message: {message.content}")
                    input = str(message.content)
                    contexts.append({
                        "role": "user",
                        "content": input})
                    
                    output = str(sec2_FUNCTION(input, contexts))
                    contexts.append({
                        "role": "assistant",
                        "content": output})
                    
                    print(contexts)
                    await message.channel.send(output)
    
    @bot.command
    async def repo(ctx):
        await ctx.message.author.send("https://chatgpt.com/c/68bd5033-b380-832b-ab04-6c4fc365354f")
        discord.utils.get()
        
        #voice_client = guild.voice_client
        #guild = message.guild
        #if voice_client and voice_client.is_connected():
            
    """      
    @bot.command()
    async def status(ctx):
        global sec2_Reply_Status 
        if sec2_Reply_Status:
            await ctx.send("Disabling 2sec's reply status.")
            sec2_Reply_Status = False
        else:
            await ctx.send("2sec is now active!")
            sec2_Reply_Status = True

    #async def schedule(ctx): ask for schedule, and attempts to save it in a database
        """


    async def ping(ctx):
        await ctx.message.author.send("pong")
        discord.utils.get()
        


    
    

    bot.run(SettingsAPI_Disc.DISCORDAPI, root_logger=True)  

try:
    if __name__=="__main__":
        contexts = []
        run()
except Exception as e: 
    print(f"Error in Discord Bot: {e}")

