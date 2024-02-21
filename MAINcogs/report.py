import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class A(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Report to us")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def report(self, ctx):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        modal = TutorialModal(title="Press Enter")
        if registerOperation: await ctx.send_modal(modal)

    @report.error
    async def reporterror(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            if error.retry_after < 60:
                output = str(round(error.retry_after)) + " seconds"
            else:
                output = str(min) + " mintues"

            embed.description = f"You need to wait {output} before you can use this command again."

        elif isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred while executing the command: {error.original}"

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

def setup(bot):
    bot.add_cog(A(bot))


class TutorialModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Title",
                placeholder="Title here:",
            ),
            discord.ui.InputText(
                label="Problem description",
                placeholder="Explicit description here:",
                style=discord.InputTextStyle.long
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title=self.children[0].value,
            description=self.children[1].value,
            color=0xC87A80
        )

        await interaction.response.send_message(embed=embed)
