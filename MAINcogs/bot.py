import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import os
import json


class Botinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]
            self.log_DB = Log(Database(logDB))

        with open('config/globalSettings.json', 'r') as file:
            data = json.load(file)
            self.globalSettings = data["globalSetting"]

            self.version = self.globalSettings["version"]
            self.owner = self.globalSettings["owner"]
            self.co_owner = self.globalSettings["co-owner"]

    @slash_command(description="Shows you usefull information about the bot")
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def bot(self, ctx):
        asw = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        file_path = 'AchiTect dev'

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f'Die Datei {file_path} ist {file_size} Bytes groß.')

        if asw:
            embed = discord.Embed(color=0xC87A80, title=":information_source: BOT INFORMATION :information_source:")
            embed.add_field(name="Owner&Co-owner: ", value=f'{self.owner}, {self.co_owner}')
            embed.add_field(name="Staff: ", value="s4mity, levi")
            embed.add_field(name="Bot version: ", value=self.version, inline=True)
            embed.add_field(name="Created: ", value="26. June 2023", inline=True)
            embed.add_field(name="Servers: ", value=len(self.bot.guilds))
            embed.add_field(name="Commands: ", value=len(self.bot.commands))
            embed.add_field(name="Lines of code: ", value="2500")
            embed.add_field(name="File size (DB included): ", value="51,6 MB")
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
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Botinfo(bot))
