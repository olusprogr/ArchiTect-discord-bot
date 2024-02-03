import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ext.pages import Paginator

from database._databaseManager import *
import json


class Userlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Displays you every sinlge member on the server")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def memberlist(self, ctx):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)
        members = ctx.guild.members
        pages = []
        description = ""

        for index, member in enumerate(members):
            description += f"`{index + 1}.` {member}\n"

            if (index + 1) % 10 == 0 or index == len(members) - 1:
                embed = discord.Embed(title="👥MEMBER LIST/INFORMATION👥", description=description, color=0xC87A80)
                if ctx.guild.icon:
                    embed.set_thumbnail(url=ctx.guild.icon.url)
                pages.append(embed)
                description = ""

        paginator = Paginator(pages=pages, author_check=False)
        await paginator.respond(ctx.interaction)

    @memberlist.error
    async def memberlist_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            raise error

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Userlist(bot))