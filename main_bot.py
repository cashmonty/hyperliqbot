import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from commands import positions, recentorders, allprices, userfills, fundingrates

import commands as my_commands  # Import your commands

# Load environment variables
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.messages = True  # Enable any other intents as needed
intents.message_content = True 
bot = commands.Bot(command_prefix="/", intents=intents)



bot.add_command(positions)
bot.add_command(recentorders)
bot.add_command(allprices)
bot.add_command(userfills)
bot.add_command(fundingrates)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Run the bot
bot.run(bot_token)



