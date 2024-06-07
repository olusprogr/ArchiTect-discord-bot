import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, Button

from database._databaseManager import *

import json


mainEmbed = discord.Embed(title="HERE ARE ALL THE COMMANDS", color=0xC87A80,
                          description="The bot uses slash command, you can get information on a command by using /help command.",)
mainEmbed.add_field(name="General", value=f"```/greet\n/report\n/rank\n/embed\n/clear\n/daily_credits```")
mainEmbed.add_field(name="Information", value=f"```/help\n/userinfo\n/memberlist\n/serverinfo\n/bot\n/ping```")
mainEmbed.add_field(name="Premium", value=f"```/say\n/spam\n```")


class LinkButtonView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Consider getting premium and get perks.", style=discord.ButtonStyle.link,
                             url="https://architect-discord-bot.onrender.com"))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Get some help commands")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def help(self, ctx):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)
        if registerOperation: await ctx.respond(embed=mainEmbed, view=LinkButtonView())

    @help.error
    async def help_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error:")

        if isinstance(error, commands.MissingPermissions):
            embed.description = "You don't have permission to execute this command."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            embed.description = "I don't have permission to send messages or embeds in this channel."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Help(bot))
