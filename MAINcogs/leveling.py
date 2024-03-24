import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from database._databaseManager import *

from easy_pil import *
import json


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/databases.json', 'r') as file:
            data = json.load(file)

            logDB = data["databases"]["savingUserOperations"]
            levelDB = data["databases"]["userLevelingSystem"]

        self.raw_level_DB = "users"
        self.level_DB = Economy(Database(levelDB))
        self.log_DB = Log(Database(logDB))

    @staticmethod
    def get_level(xp):
        level_ranges = [25, 50, 75, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000,
                        50000, 80000, 100000]

        for i, threshold in enumerate(level_ranges, start=1):
            if xp <= threshold:
                return i, threshold

        return len(level_ranges) + 1, 0

    @commands.Cog.listener()
    async def on_message(self, ctx):
        self.level_DB.insertValue(int(ctx.author.id))

    @slash_command(description="Get your current registered xp and level out from our new set up database.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rank(self, ctx, user: Option(discord.Member, "Select a user", default=None)):
        registerOperation = self.log_DB.log(str(ctx.guild), str(ctx.author), str(ctx.command), f"{user}")
        if user is None: user = ctx.author

        await ctx.defer()
        result = self.level_DB.getUserXP(user.id)

        lvl = self.get_level(result[0])

        background = Editor(Canvas((900, 300), color="#6B3A73"))
        profile_picture = await load_image_async(str(user.avatar.url))
        profile = Editor(profile_picture).resize((150, 150)).circle_image()

        poppins = Font.poppins(size=40)
        poppins_small = Font.poppins(size=30)

        card_right_shape = [(600, 0), (750, 300), (900, 300), (900, 0)]
        background.polygon(card_right_shape, color="#F18F01")
        background.paste(profile, (30, 30))

        small_profile_picture = await load_image_async(
            "https://media.discordapp.net/attachments/1133351096371380224/1200840827405094952/Archtietc.webp?ex=6611792b&is=65ff042b&hm=efd4e3e164892e21150533b33b6be0865b6c7bc53ded52fe9d1ad42b00543085&=&format=webp&width=671&height=671")
        small_profile = Editor(small_profile_picture).resize((180, 180)).circle_image()
        background.paste(small_profile, (750, 160))

        level = int(100 / lvl[1] * result[0])
        background.rectangle((30, 220), width=650, height=40, color="#8E44AD", radius=20)
        background.bar((30, 220), height=40, max_width=650, percentage=level, color="#E67E22",
                       radius=20)
        background.text((200, 40), user.name, font=poppins, color="#FFFFFF")

        background.rectangle((200, 100), width=650, height=2, fill="#FFFFFF")
        background.text(
            (200, 130),
            f"Level - {lvl[0]}    XP - {result[0]} / {lvl[1]}",
            font=poppins_small,
            color="#FFFFFF"
        )

        file = discord.File(fp=background.image_bytes, filename="levelcard.png")
        if registerOperation: await ctx.respond(file=file)


    @rank.error
    async def rank_error(self, ctx, error):
        embed = discord.Embed(color=0xC87A80, title="Error: ")

        if isinstance(error, commands.MemberNotFound):
            embed.description = "User not found."

        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Please provide all required arguments."

        elif isinstance(error, commands.BadArgument):
            embed.description = "Invalid argument provided."

        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"You're on cooldown. Please try again in {round(error.retry_after)} seconds."

        else:
            embed.description = f"An unexpected error occurred. Please try again later. {error}"
            print(error)

        await ctx.respond(embed=embed, ephemeral=True, delete_after=15)


def setup(bot):
    bot.add_cog(Rank(bot))
