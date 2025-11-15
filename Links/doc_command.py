from discord.ext import commands

class DocCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="doc")
    async def doc(self, ctx):
        documento_url = "https://docs.google.com/spreadsheets/d/1sZCc_4vVS7b4pfTVlpKmDxRjFtrfIapqMMLXvBL5FoU/edit?usp=drivesdk"  # ⬅️ coloque o link real aqui

        await ctx.send(
            "📘 **Documento Informativo do Servidor**\n"
            "Aqui está o documento:\n"
            f"{documento_url}"
        )

async def setup(bot):
    await bot.add_cog(DocCommand(bot))
