import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Invite the bot to your server")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def invite(self, ctx):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        embed = discord.Embed(title="ArchiTect Invitation link:", color=0xC87A80, description="Click on the button down bellow this message...")
        embed.set_author(name="ArchiTect-Development", icon_url="https://media.discordapp.net/attachments/1133351096371380224/1157333387393110016/Archtietc3.jpg?ex=65183a35&is=6516e8b5&hm=7642cbae776a357d14245853d542167d0f07743e634bd5d7991b014594ec1015&=")

        view = discord.ui.View()
        button = discord.ui.Button(label="Click me!", url="https://discord.com/api/oauth2/authorize?client_id=1123005191038447646&permissions=8&scope=applications.commands%20bot", style=discord.ButtonStyle.red)
        view.add_item(button)

        await ctx.respond(embed=embed, view=view)

    @invite.error
    async def invite_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            embed.description = "I don't have permission to send messages or embeds in this channel."

        elif isinstance(error, commands.CheckFailure):
            embed.description = "You don't have the necessary permissions to use this command."

        elif isinstance(error, commands.NoPrivateMessage):
            embed.description = "This command can't be used in private messages."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Invite(bot))