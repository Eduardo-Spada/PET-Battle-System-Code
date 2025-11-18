from discord.ext import commands
from discord import ui, Interaction

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
]

ITENS_POR_PAGINA = 6

def gerar_paginas():
    total = len(COMANDOS)
    paginas = []
    for i in range(0, total, ITENS_POR_PAGINA):
        comandos = COMANDOS[i:i+ITENS_POR_PAGINA]
        pagina_txt = (
            "📘 **Comandos do bot**\n\n"
            f"**Página {len(paginas)+1}/{((total-1)//ITENS_POR_PAGINA)+1}:**\n\n"
            + "\n".join(comandos)
        )
        paginas.append(pagina_txt)
    return paginas

class SOSPaginas(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.paginas = gerar_paginas()
        self.index = 0

    async def update_message(self, interaction):
        await interaction.response.edit_message(content=self.paginas[self.index], view=self)

    @ui.button(label="⬅️ Voltar", style=2)
    async def voltar(self, interaction: Interaction, button: ui.Button):
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @ui.button(label="➡️ Avançar", style=2)
    async def avancar(self, interaction: Interaction, button: ui.Button):
        if self.index < len(self.paginas) - 1:
            self.index += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

class SOSCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sos")
    async def sos(self, ctx):
        view = SOSPaginas()
        await ctx.send(content=view.paginas[0], view=view)

async def setup(bot):
    await bot.add_cog(SOSCommand(bot))
