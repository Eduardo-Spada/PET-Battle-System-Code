from discord.ext import commands

class SOSCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sos")
    async def sos(self, ctx):
        ajuda_texto = (
            "📘 **Comandos disponíveis:**\n\n"
            "🦠 **Vírus:**\n"
            "  • `!virus NomeDoVirus` – Mostra os dados de um vírus.\n"
            "  • `!viruslist` – Lista todos os vírus.\n"
            "  • `!locais` – Lista todas as áreas.\n"
            "  • `!local NomeDaArea` – Mostra vírus em uma área específica.\n\n"
            "💾 **Chips:**\n"
            "  • `!chip NomeDoChip` – Mostra os dados de um chip.\n"
            "  • `!chipslist` – Lista todos os chips.\n\n"
            "🧩 **Peças:**\n"
            "  • `!peça NomeDaPeça` – Mostra os dados de uma peça.\n"
            "  • `!pecaslist` – Lista todas as peças.\n\n"
            "⚔️ **Batalha:**\n"
            "  • `!batalha Aliado1 10/10 vs Inimigo1 12/12` – Inicia uma batalha.\n"
            "  • `!rodada Nome faz algo com Alvo 3` – Registra uma ação.\n"
            "  • `!passar Nome` – Passa a vez.\n"
            "  • `!status` – Mostra o status da batalha.\n"
            "  • `!encerrar` – Finaliza a batalha.\n\n"
            "📘 **Documento do Servidor:**\n"
            "  • `!doc` – Mostra o documento informativo.\n\n"
            "🤖 **Outros:**\n"
            "  • `!oi` – Teste rápido.\n\n"
            "🛠️ Mais comandos virão!"
        )
        await ctx.send(ajuda_texto)

async def setup(bot):
    await bot.add_cog(SOSCommand(bot))
