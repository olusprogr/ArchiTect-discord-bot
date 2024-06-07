import asyncio

import discord
from discord.ext import commands
from discord.commands import slash_command

from database._databaseManager import *

import json


class AboutUs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file: logDB = json.load(file)["databases"]["savingUserOperations"]
        with open("config/member.json", "r") as file: data = json.load(file)

        self.members = data["members"]
        self.log_DB = Log(Database(logDB))

    @slash_command(description="See the information about the developers of the bot🖥️")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def about_us(self, ctx):
        registerOperation: bool = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command))
        embed = discord.Embed(color=0xC87A80, title="About Us", description="Meet the team behind the ArchiTect bot!")
        if registerOperation: await ctx.respond(embed=embed)

        await asyncio.sleep(3)

        for member in self.members:
            embedS: discord.Embed = discord.Embed(color=0xC87A80)

            name: str = member["name"]
            role: str = member["role"]
            skills: str = member["skills"]
            contact: str = member["contact"]
            link: str = member["link"]

            print(name, role, skills, contact, link)

            embedS.add_field(
                name=name,
                value=f"**Role:** {role}\n**Skills:** {skills}\n**Contact:** {contact}",
                inline=False
            )
            
            file = discord.File(link, filename=f"image.webp")
            embedS.set_thumbnail(url=f'attachment://image.webp')
            
            await ctx.send(embed=embedS, file=file)
        
    @about_us.error
    async def about_us_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error:")

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided. Make sure you mention a valid user."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "An unexpected error occurred. Please try again later."
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(AboutUs(bot))