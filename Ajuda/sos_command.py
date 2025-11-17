from discord.ext import commands
from discord import Embed, ui, Interaction

# Lista de comandos (adicione quantos quiser)
COMANDOS = [
    "🦠 `!virus Nome` – Mostra dados de um vírus.",
    "🦠 `!viruslist` – Lista todos os vírus.",
    "📍 `!local Nome` – Mostra área e seus vírus.",
    "📍 `!locais` – Lista todas as áreas.",
    "💾 `!chip Nome` – Mostra dados do chip.",
    "💾 `!chipslist` – Lista chips.",
    "🧩 `!peça Nome` – Mostra peça.",
    "🧩 `!pecaslist` – Lista peças.",
    "⚔️ `!batalha` – Inicia batalha.",
    "⚔️ `!rodada` – Registra ação.",
    "⚔️ `!passar` – Passa turno.",
    "⚔️ `!encerrar` – Encerra batalha.",
    "📊 `!status` – Mostra status.",
    "📘 `!doc` – Abre documento informativo.",
    "🤖 `!oi` – Teste do bot.",
    # ADICIONE MAIS SEM MEDO — PÁGINAS INFINITAS!
]

ITENS_POR_PAGINA = 6  # quantidade de comandos por página


class SOSPaginas(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.paginas = self.gerar_paginas()
        self.index = 0

    def gerar_paginas(self):
        paginas = []
        total = len(COMANDOS)

        # Criar páginas automaticamente
        for i in range(0, total, ITENS_POR_PAGINA):
            comandos_pagina = COMANDOS[i:i + ITENS_POR_PAGINA]

            embed = Embed(
                title=f"📘 Lista de Comandos — Página {len(paginas)+1}",
                description="\n".join(comandos_pagina),
                color=0x3498db
            )

            paginas.append(embed)

        return paginas

    # Botão voltar
    @ui.button(label="⬅️ Voltar", style=2)
    async def voltar(self, interaction: Interaction, button: ui.Button):
        if self.index > 0:
            self.index -= 1
        await interaction.response.edit_message(embed=self.paginas[self.index], view=self)

    # Botão avançar
    @ui.button(label="➡️ Avançar", style=2)
    async def avancar(self, interaction: Interaction, button: ui.Button):
        if self.index < len(self.paginas) - 1:
            self.index += 1
        await interaction.response.edit_message(embed=self.paginas[self.index], view=self)


class SOSCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sos")
    async def sos(self, ctx):
        view = SOSPaginas()
        await ctx.send(embed=view.paginas[0], view=view)


async def setup(bot):
    await bot.add_cog(SOSCommand(bot))
