import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

from database._databaseManager import *

import json
import requests
from PIL import Image
from io import BytesIO


class cs_map(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    give = SlashCommandGroup(name="give", description="Give group")

    @give.command(description="Get one of all CS maps callouts")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cs_callout(self, ctx,
                       maps: Option(str, choices=["Dust2", "Train", "Mirage", "Overpass", "Inferno", "Ancient", "Anubis", "Vertigo", "Nuke", "Cobblestone", "Cache", "Italy"],
                                    description="Select a CS map.")):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{maps}")

        map_info = {
            "Dust2": "https://media.discordapp.net/attachments/1133351096371380224/1133351306602487938/Dust_2.png?width=671&height=671",
            "Train": "https://media.discordapp.net/attachments/1133351096371380224/1133351307722362890/Train.png",
            "Mirage": "https://media.discordapp.net/attachments/1133351096371380224/1133351307135172628/Mirage.png?width=671&height=671",
            "Overpass": "https://media.discordapp.net/attachments/1133351096371380224/1133351307411988530/Overpass.png",
            "Inferno": "https://media.discordapp.net/attachments/1133351096371380224/1133351306875113563/Inferno.png?width=671&height=671",
            "Ancient": "https://media.discordapp.net/attachments/1133351096371380224/1135172416184795236/de_ancient_radar.jpg?width=671&height=671",
            "Anubis": "https://media.discordapp.net/attachments/1133351096371380224/1135172415719219271/de_anubis_radar.jpg?width=671&height=671",
            "Vertigo_upper": "https://media.discordapp.net/attachments/1133351096371380224/1142435551346184282/de_vertigoUP_radar.jpg?width=671&height=671",
            "Vertigo_lower": "https://media.discordapp.net/attachments/1133351096371380224/1142438188871319552/de_vertigoDown__radar.jpg?width=671&height=671",
            "Nuke_upper": "https://media.discordapp.net/attachments/1133351096371380224/1142435459474141284/de_nuke_radar.jpg?width=671&height=671",
            "Nuke_lower": "https://media.discordapp.net/attachments/1133351096371380224/1142435459805479023/de_nuke2_radar.jpg?width=671&height=671",
            "Cobblestone": "https://media.discordapp.net/attachments/1133351096371380224/1151846481326780456/cobblestone_85b0d69929.png?width=671&height=671",
            "Cache": "https://media.discordapp.net/attachments/1133351096371380224/1151846481570045994/cache_5a5bb344bb.png?width=671&height=671",
            "Italy": "https://media.discordapp.net/attachments/1133351096371380224/1151846482006245438/2348279122_preview_Italy.jpg?width=491&height=671",
        }

        map_title = f"Map: {maps}"
        embed = discord.Embed(title=map_title, color=discord.Color.orange())

        if maps == "Vertigo":
            embed_upper = discord.Embed(title=map_title, description="(Upper)", color=discord.Color.orange())
            embed_lower = discord.Embed(description="(Lower)", color=discord.Color.orange())
            embed_upper.set_image(url=map_info["Vertigo_upper"])
            embed_lower.set_image(url=map_info["Vertigo_lower"])
            await ctx.respond(embed=embed_upper)
            await ctx.send(embed=embed_lower)
        elif maps == "Nuke":
            embed_upper = discord.Embed(title=map_title, description="(Upper)", color=discord.Color.orange())
            embed_lower = discord.Embed(description="(Lower)", color=discord.Color.orange())
            embed_upper.set_image(url=map_info["Nuke_upper"])
            embed_lower.set_image(url=map_info["Nuke_lower"])
            await ctx.respond(embed=embed_upper)
            await ctx.send(embed=embed_lower)
        else:
            embed.set_image(url=map_info.get(maps, ""))
            if registerOperation: await ctx.respond(embed=embed)

    @cs_callout.error
    async def give_cs_callout_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error:")

        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)

# -----------------------------------------------------------------------------------------

    @give.command(description="Gives you the amount of messages sent in this channel")
    @discord.default_permissions(read_message_history=True)
    @commands.cooldown(1, 900, commands.BucketType.guild)
    async def messages(self, ctx):
        count = 0
        channel = ctx.channel
        embed = discord.Embed(color=0xC87A80, title="Searching for messages...",
                              description="Please be patient for a moment.\nThis may take **3min+!**")
        await ctx.respond(embed=embed, delete_after=15)
        async for i in channel.history(limit=20000):
            count += 1

        embed = discord.Embed(color=0xC87A80, title="📄MESSAGES/GIVE📄",
                              description=f"Found **{count}** messages in this channel.")
        await ctx.send(embed=embed)

        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), count)

    @messages.error
    async def messages_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.MissingPermissions):
            embed.description = "You don't have permission to execute this command."

        elif isinstance(error, commands.CommandOnCooldown):
            if error.retry_after < 60:
                output = str(round(error.retry_after)) + " seconds"
            else:
                min = round(error.retry_after / 60)
                output = str(min) + " mintues"

            embed.description = f"You're on cooldown. Please try again in {output}."

        elif isinstance(error, commands.ChannelNotFound):
            embed.description = "Channel not found. Please try again in a valid channel."

        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, discord.Forbidden):
            embed.description = "I don't have permission to read message history in this channel."

        else:
            embed.description = "An unexpected error occurred. Please try again later."

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


# -----------------------------------------------------------

    @give.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def img(self, ctx, url: str):
        await ctx.defer()
        self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), url)
        try:
            response = requests.get(url)
            response.raise_for_status()
            information = response.headers

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

            embed = discord.Embed(title='Requested image from the internet:',
                                  color=int(hex_color, 16))
            embed.add_field(value=f'Content-Type: {information["Content-Type"]}\n'
                                 f'Expires: {information["Expires"]}', name='Some informations:')
            embed.set_image(url=url)
            embed.set_footer()

            await ctx.respond(embed=embed)

        except requests.exceptions.HTTPError as errh:
            await ctx.send(f'HTTP Error: {errh}')
        except requests.exceptions.ConnectionError as errc:
            await ctx.send(f'Connection Error: {errc}')
        except requests.exceptions.Timeout as errt:
            await ctx.send(f'Timeout Error: {errt}')
        except requests.exceptions.RequestException as err:
            await ctx.send(f'An error occurred: {err}')


def setup(bot):
    bot.add_cog(cs_map(bot))
