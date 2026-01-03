import discord
from discord.ext import commands

# Lista de comandos que vão aparecer no !sos
COMANDOS = [
    "🦠 !virus Nome – Mostra dados de um vírus.",
    "🦠 !viruslist – Lista todos os vírus.",
    "📍 !local Nome – Mostra área e seus vírus.",
    "📍 !locais – Lista todas as áreas.",
    "💾 !chip Nome – Mostra dados do chip.",
    "💾 !chipslist – Lista chips.",
    "🧩 !peça Nome – Mostra peça.",
    "🧩 !pecaslist – Lista peças.",
    "⚔️ !batalha – Inicia batalha.",
    "⚔️ !rodada – Registra ação.",
    "⚔️ !passar – Passa turno.",
    "⚔️ !encerrar – Encerra batalha.",
    "📊 !status – Mostra status.",
    "📘 !doc – Abre documento informativo.",
    "🤖 !oi – Teste do bot.",
    "🎲 !encontro Área – Sorteia vírus de uma área + 'Todas as Áreas'.",
    "🎲 !encontro Área players:X – Sorteia vírus para X jogadores.",
    "🎲 !encontro Área virus:X – Sorteia quantidade definida de vírus.",
    "🎁 !r - marque a mensagem do !encontro, e então utilize esse comando! você obterá as Recompensas de todos os vírus!",
    "💰 !r zenny - A mesma coisa que !r, muda que aqui tu só ganha os zennys! utilize somente caso você possua o programa millionaire, viu?",
]

# Quantos itens por página
ITENS_POR_PAGINA = 6


# =====================================================================
# VIEW DO PAGINADOR  — igual ao chipslist, mas adaptada
# =====================================================================
class PaginadorSOS(discord.ui.View):
    def __init__(self, paginas, total):
        super().__init__(timeout=300)  
        self.paginas = paginas
        self.total = total
        self.index = 0

    def formatar_pagina(self):
        lista_formatada = "\n".join(f"{cmd}" for cmd in self.paginas[self.index])
        return (
            f"📘 **Comandos do Bot ({self.total} no total)**\n"
            f"**Página {self.index+1}/{len(self.paginas)}:**\n\n"
            f"{lista_formatada}"
        )

    async def update_message(self, interaction):
        await interaction.response.edit_message(
            content=self.formatar_pagina(),
            view=self
        )

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Próximo ➡️", style=discord.ButtonStyle.secondary)
    async def proximo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.paginas) - 1:
            self.index += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()


# =====================================================================
# COG DO SOS — igual ao chipslist
# =====================================================================
class SOS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sos")
    async def sos(self, ctx):
        total = len(COMANDOS)

        # divide em páginas
        paginas = [
            COMANDOS[i:i + ITENS_POR_PAGINA]
            for i in range(0, total, ITENS_POR_PAGINA)
        ]

        view = PaginadorSOS(paginas, total)
        await ctx.send(view.formatar_pagina(), view=view)


async def setup(bot):
    await bot.add_cog(SOS(bot))
