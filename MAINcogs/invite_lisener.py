from discord.ext import commands


class GuildJoinListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        owner = guild.owner

        print(f"Bot joined a new server: {guild.name} (ID: {guild.id})")
        print(f"Server owner: {owner.name}#{owner.discriminator} (ID: {owner.id})")
        print(f"Member count: {guild.member_count}")


def setup(bot):
    bot.add_cog(GuildJoinListener(bot))
