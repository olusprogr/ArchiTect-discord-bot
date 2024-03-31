import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from database._databaseManager import *

import json
import requests
from PIL import Image
from io import BytesIO


class Userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    @slash_command(description="Show every info of the choiced user")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def userinfo(self, ctx, user: Option(discord.Member, "Select a user", default=None)):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), user)
        if user == None: user = ctx.author

        await ctx.defer()

        response = requests.get(user.avatar.url)
        image_bytes = BytesIO(response.content)

        image = Image.open(image_bytes)

        max_size = (100, 100)
        image.thumbnail(max_size, Image.ANTIALIAS)

        width, height = image.size
        total_red, total_green, total_blue = 0, 0, 0

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                total_red += pixel[0]
                total_green += pixel[1]
                total_blue += pixel[2]

        average_red = total_red // (width * height)
        average_green = total_green // (width * height)
        average_blue = total_blue // (width * height)

        hex_color = "0x{:02x}{:02x}{:02x}".format(average_red, average_green, average_blue)

        embed = discord.Embed(color=int(hex_color, 16))
        embed.set_author(name=f"User Information - {user}", icon_url=user.avatar.url if user.avatar else discord.Embed.Empty)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else discord.Embed.Empty)

        embed.add_field(name="ID:", value=user.id, inline=False)
        embed.add_field(name="Name:", value=user.display_name, inline=False)
        embed.add_field(name="Bot:", value=user.bot, inline=False)
        embed.add_field(name="Status:", value=str(user.status).title(), inline=False)
        embed.add_field(name="Activity:", value=user.activity.name if user.activity else "None", inline=False)

        embed.set_footer(
            text=f"Joined on {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')} | Account created on {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if registerOperation: await ctx.respond(embed=embed)

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        elif isinstance(error, commands.errors.MemberNotFound):
            embed.description = "User not found. Please make sure to mention a valid user."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Missing required argument. Please provide a valid user."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Bad argument provided. Please provide a valid user."

        elif isinstance(error, commands.MissingPermissions):
            embed.description = "You don't have the required permissions to execute this command."

        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = "The bot doesn't have the required permissions to execute this command."

        else:
            embed.description = "An unexpected error occurred. Please try again later."
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Userinfo(bot))
