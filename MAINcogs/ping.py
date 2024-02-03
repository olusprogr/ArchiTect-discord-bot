import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Get the bots ping")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def ping(self, ctx):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        embed = discord.Embed(title="🏓PONG/LATENCY🏓", description=f"Client latency: **{round(self.bot.latency, 3)}**s",
                              color=0xC87A80)
        embed.set_footer(text="Issues on discords or the bots sides could create weird or high latency.")
        await ctx.respond(embed=embed)

    @ping.error
    async def bot_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred while executing the command: {error.original}"

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to send messages in this channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

def setup(bot):
    bot.add_cog(Ping(bot))
