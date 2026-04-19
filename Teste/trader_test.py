from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pingtrader(self, ctx):
        await ctx.send("Trader test funcionando 🔥")

async def setup(bot):
    print("🔥 TEST COG CARREGOU")
    await bot.add_cog(Test(bot))
