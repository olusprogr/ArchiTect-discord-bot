import discord
from discord.ext import commands


class OnLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_server_id = 1122894633840685137
        self.target_channel_id = 1122894777361367081

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == self.target_server_id:
            channel = member.guild.get_channel(self.target_channel_id)
            if channel:
                await channel.send(f"{member.name} has left the server.")
            else:
                print(f"Target channel not found in server {member.guild.name}")

def setup(bot):
    bot.add_cog(OnLeave(bot))