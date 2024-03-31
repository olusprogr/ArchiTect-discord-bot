import discord
from discord.ext import commands


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()

        embed = discord.Embed(color=0xC87A80, title=f"Hi {member.name}, ", description=f"Welcome. Good to see you!")

        embed2 = discord.Embed(color=0xC87A80, title="Welcome to ArchiTect-Development!",
                               description="The official Discord support&FEQ server for ArchiTect",)
        embed2.set_thumbnail(url="https://media.discordapp.net/attachments/1133351096371380224/1172857726246846514/Archtietc3tst_1.png?ex=66112f60&is=65feba60&hm=6cbce91ec0b43b56fb71e4ac7a40eec67fbfd3dc5c92c79ad2b0f93e1ea15cea&=&format=webp&quality=lossless&width=671&height=671")

        view = discord.ui.View()
        button = discord.ui.Button(
            label="Join Discord Server!",
            url="https://discord.gg/uk5jeHngyv",
            style=discord.ButtonStyle.blurple
        )
        view.add_item(button)

        button = discord.ui.Button(
            label="Visit The ArchiTect Website!",
            url="https://olusprogr.github.io/architect-website-deployed/#/about-us",
            style=discord.ButtonStyle.url
        )
        view.add_item(button)

        embed3 = discord.Embed(color=0xC13584,
                               title="Click here!", url="https://instagram.com/arkitekt.gg?igshid=NzZhOTFlYzFmZQ==")
        embed3.set_thumbnail(
            url="https://media.discordapp.net/attachments/1133351096371380224/1157333387393110016/Archtietc3.jpg?ex=65183a35&is=6516e8b5&hm=7642cbae776a357d14245853d542167d0f07743e634bd5d7991b014594ec1015&=")
        embed3.set_author(name="ArchiTect on Instagram!", icon_url="https://media.discordapp.net/attachments/1133351096371380224/1133812786636537906/Instagram_logo_2016.svg.webp?width=905&height=905")

        await member.dm_channel.send(embed=embed)
        await member.dm_channel.send(embed=embed2, view=view)
        await member.dm_channel.send(embed=embed3)


def setup(bot):
    bot.add_cog(Commands(bot))