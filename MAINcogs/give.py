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
        self.file = None
        self.map_info = {
            "Dust_2": "assets/csMaps/maps/Dust_2.png",
            "Train": "assets/csMaps/maps/Train.png",
            "Mirage": "assets/csMaps/maps/Mirage.png",
            "Overpass": "assets/csMaps/maps/Overpass.png",
            "Inferno": "assets/csMaps/maps/Inferno.png",
            "Ancient": "assets/csMaps/maps/Ancient.png",
            "Anubis": "assets/csMaps/maps/Anubis.png",
            "Vertigo_upper": "assets/csMaps/maps/Vertigo_upper.png",
            "Vertigo_lower": "assets/csMaps/maps/Vertigo_lower.png",
            "Nuke_upper": "assets/csMaps/maps/Nuke_upper.png",
            "Nuke_lower": "assets/csMaps/maps/Nuke_lower.png",
            "Cobblestone": "assets/csMaps/maps/Cobblestone.png",
            "Cache": "assets/csMaps/maps/Cache.png",
            "Italy": "assets/csMaps/maps/Italy.png",
            "District": "assets/csMaps/maps/District.png"
        }

        with open('config/databases.json', 'r') as file:
            data = json.load(file)
            logDB = data["databases"]["savingUserOperations"]

        self.log_DB = Log(Database(logDB))

    give = SlashCommandGroup(name="give", description="Give group")

    @give.command(description="Get one of all CS maps callouts")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cs_callout(self, ctx,
                       maps: Option(str, choices=["Dust_2", "Train", "Mirage", "Overpass", "Inferno", "Ancient", "Anubis", "Vertigo", "Nuke", "Cobblestone", "Cache", "Italy", "District"],
                                    description="Select a CS map.")):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{maps}")
        map_info = self.map_info

        map_title = f"Map: {maps}"
        embed = discord.Embed(title=map_title, color=discord.Color.orange())

        def locateImg(
                selectedMap: str = map_info.get(maps, ''),
                embedS = discord.Embed(color=discord.Color.orange())
        ):
            filter: [str] = [
                'Vertigo_upper',
                'Vertigo_lower',
                'Nuke_upper',
                'Nuke_lower'
            ]

            for keyword in filter:
                if keyword == selectedMap:
                    selectedMap = map_info.get(keyword, '')
                    print(selectedMap)
                    with open(selectedMap, 'rb') as f:
                        file = discord.File(BytesIO(f.read()), filename=f'{keyword}.png')
                        embedS.set_image(url=f'attachment://{keyword}.png')
                        return [embedS, file]


            with open(selectedMap, 'rb') as f:
                file = discord.File(BytesIO(f.read()), filename=f'{maps.lower()}.png')
                embedS.set_image(url=f'attachment://{maps.lower()}.png')
                return [embedS, file]



        if maps == "Vertigo":
            selectedMapUpper: str = 'Vertigo_upper'
            upper_stuff = locateImg(selectedMap=selectedMapUpper)
            embedUpper = upper_stuff[0]
            fileUpper = upper_stuff[1]
            embedUpper.title = "Vertigo"
            embedUpper.description = '(Upper)'

            await ctx.respond(embed=embedUpper, file=fileUpper)

            selectedMapLower: str = 'Vertigo_lower'
            lower_stuff = locateImg(selectedMap=selectedMapLower)
            embedLower = lower_stuff[0]
            fileLower = lower_stuff[1]
            embedLower.description = '(Lower)'

            await ctx.send(embed=embedLower, file=fileLower)


        elif maps == "Nuke":
            if maps == "Nuke":
                selectedMapUpper = 'Nuke_upper'
                upper_stuff = locateImg(selectedMap=selectedMapUpper)
                embedUpper = upper_stuff[0]
                fileUpper = upper_stuff[1]
                embedUpper.title = "Nuke"
                embedUpper.description = '(Upper)'

                await ctx.respond(embed=embedUpper, file=fileUpper)

                selectedMapLower = 'Nuke_lower'
                lower_stuff = locateImg(selectedMap=selectedMapLower)
                embedLower = lower_stuff[0]
                fileLower = lower_stuff[1]
                embedLower.description = '(Lower)'

                await ctx.send(embed=embedLower, file=fileLower)

        else:
            out = locateImg(embedS=embed)
            await ctx.respond(embed=out[0], file=out[1])

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
            print(error)

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

    @give.command(description="Paste a link of an image and the bot will send it in the chat")
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
