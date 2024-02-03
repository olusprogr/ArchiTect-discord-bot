import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

        logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))


    @slash_command(description="Get all the information you need about the server")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def serverinfo(self, ctx):
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), None)

        embed = discord.Embed(color=0xC87A80)
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        embed.add_field(name="👑 Owned by", value=ctx.guild.owner.mention, inline=True)
        embed.add_field(name="👥 Members", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="🔐 Roles", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="📆 Created at" ,value=ctx.guild.created_at.__format__("%A, %d. %B %Y"),inline=True)
        embed.add_field(name="💬 Channels", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="💎 Booster", value=ctx.guild.premium_subscription_count, inline=True)
        embed.set_footer(text="🆔 ID: " + str(ctx.guild.id))
        await ctx.respond(embed=embed)

    @serverinfo.error
    async def serverinfo_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(serverinfo(bot))