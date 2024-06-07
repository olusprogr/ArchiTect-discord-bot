import asyncio

import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class Botinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.minOnRuntime: int = 1
        self.file_path: str = 'AchiTect dev'
        self.value: str = 'minutes'
        self.bot.loop.create_task(self.min_counter())

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

        with open('config/globalSettings.json', 'r') as file:
            data = json.load(file)
            globalSettings = data["globalSetting"]

        self.lineOfCode = globalSettings['linesOfCode']
        self.version = globalSettings["version"]
        self.owner = globalSettings["owner"]
        self.co_owner = globalSettings["co-owner"]


    async def min_counter(self):
        while True:
            self.minOnRuntime += 1
            await asyncio.sleep(60)

    @slash_command(description="Shows you usefull information about the bot")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def bot(self, ctx):
        await ctx.defer()
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        def botsOnRunTime() -> tuple[str, int]:
            if self.minOnRuntime >= 60:
                convertedTime = self.minOnRuntime / 60  # to hours
                self.value = 'hours'
                if convertedTime >= 24:
                    convertedTime /= 24  # to days
                    self.value = 'days'
            else:
                convertedTime = round(self.minOnRuntime, 2)

            return self.value, convertedTime

        if registerOperation:
            embed = discord.Embed(color=0xC87A80, title=":information_source: BOT INFORMATION :information_source:")
            embed.add_field(name="Owner&Co-owner: ", value=f'{self.owner}, {self.co_owner}')
            embed.add_field(name="Staff: ", value="s4mity, levi")
            embed.add_field(name="Bot version: ", value=self.version, inline=True)
            embed.add_field(name="Created: ", value="26. June 2023", inline=True)
            embed.add_field(name="Servers: ", value=len(self.bot.guilds).__str__())
            embed.add_field(name="Commands: ", value=len(self.bot.commands).__str__())
            embed.add_field(name="Lines of code: ", value=self.lineOfCode)
            embed.add_field(name="File size (DB included): ", value="145 MB")
            embed.add_field(name="Bot Runtime: ", value=f"{round(botsOnRunTime()[1], 2)} {botsOnRunTime()[0]}")

            await ctx.respond(embed=embed)

    @bot.error
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
            embed.description = "An unknown error occurred.", error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Botinfo(bot))
