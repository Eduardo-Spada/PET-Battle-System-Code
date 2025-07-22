import discord
import csv
import aiohttp
from discord.ext import commands

URL_CHIPS = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
    "pub?gid=1394317870&single=true&output=csv"
)


class PaginadorChips(discord.ui.View):
    def __init__(self, paginas, total_chips):
        super().__init__(timeout=60)  # Fecha após 60 segundos sem interação
        self.paginas = paginas
        self.total_chips = total_chips
        self.index = 0

    def formatar_pagina(self):
        lista_formatada = "\n".join(f"• {nome}" for nome in self.paginas[self.index])
        return (
            f"💾 **Lista de Chips ({self.total_chips} no total)**\n"
            f"**Página {self.index+1}/{len(self.paginas)}:**\n{lista_formatada}"
        )

    async def update_message(self, interaction):
        await interaction.response.edit_message(content=self.formatar_pagina(), view=self)

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


class ChipsList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chipslist", help="Lista todos os chips disponíveis.")
    async def chipslist(self, ctx):
        """Comando para exibir a lista de chips paginada."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL_CHIPS) as response:
                    if response.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha de chips.")
                        return
                    data = await response.text()
        except Exception as e:
            await ctx.send("⚠️ Ocorreu um erro ao buscar os chips.")
            print(f"Erro ao buscar CSV de chips: {e}")
            return

        linhas = data.splitlines()
        if "Nome" not in linhas[0]:
            linhas = linhas[1:]

        reader = list(csv.DictReader(linhas))
        nomes = []

        for row in reader:
            for k in row:
                if row[k] is None:
                    row[k] = ""
            col_nome = next((k for k in row if "nome" in k.lower()), None)
            if col_nome:
                nome_chip = row[col_nome].strip()
                if nome_chip:
                    nomes.append(nome_chip)

        if not nomes:
            await ctx.send("❌ Nenhum chip encontrado na planilha.")
            return

        nomes.sort(key=lambda x: x.lower())
        total_chips = len(nomes)

        # Divide em páginas (20 nomes por página)
        tamanho_pagina = 20
        paginas = [nomes[i:i + tamanho_pagina] for i in range(0, len(nomes), tamanho_pagina)]

        view = PaginadorChips(paginas, total_chips)
        await ctx.send(view.formatar_pagina(), view=view)


async def setup(bot):
    await bot.add_cog(ChipsList(bot))
