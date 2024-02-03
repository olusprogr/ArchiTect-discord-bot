import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

from datetime import datetime
import json


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Create an embed")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        modal = TutorialModal(title="Press Enter")
        await ctx.send_modal(modal)

    @embed.error
    async def embed_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, discord.Forbidden):
            embed.description = "I don't have the necessary permissions to send messages in this channel."

        elif isinstance(error, discord.HTTPException):
            embed.description = "An error occurred while processing your request. Please try again later."

        else:
            embed.description = "An unknown error occurred."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Embed(bot))


class TutorialModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Embed title",
                placeholder="Placeholder"
            ),
            discord.ui.InputText(
                label="Embed description",
                placeholder="Placeholder",
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

        utc_now = datetime.utcnow()
        time = utc_now.strftime("%A, %d %B %Y %H:%M")

        embed.set_footer(
            text=f"{interaction.user}  •  {time}",
            icon_url=f"{interaction.user.avatar.url}",

        )

        await interaction.response.send_message(embed=embed)
