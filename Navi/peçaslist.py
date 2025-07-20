import discord
import csv
import aiohttp
from discord.ext import commands

class PaginadorView(discord.ui.View):
    def __init__(self, paginas):
        super().__init__(timeout=60)  # 60 segundos sem interação = fecha
        self.paginas = paginas
        self.index = 0

    async def update_message(self, interaction):
        texto = self.formatar_pagina()
        await interaction.response.edit_message(content=texto, view=self)

    def formatar_pagina(self):
        lista_formatada = "\n".join(f"• {nome}" for nome in self.paginas[self.index])
        return f"📜 **Lista de Peças (Página {self.index+1}/{len(self.paginas)}):**\n{lista_formatada}"

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


class PecasList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="peças", help="Lista todas as peças disponíveis")
    async def pecas_list(self, ctx):
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("Erro ao acessar os dados da planilha.")
                        return
                    data = await response.text()
        except Exception as e:
            await ctx.send("Erro ao buscar as peças.")
            print(f"Erro ao buscar CSV: {e}")
            return

        linhas = data.splitlines()
        if "Nome" not in linhas[0]:
            linhas = linhas[1:]

        reader = list(csv.DictReader(linhas))

        for r in reader:
            for k in r:
                if r[k] is None:
                    r[k] = ""

        nomes = [linha.get("Nome", "").strip() for linha in reader if linha.get("Nome")]

        if not nomes:
            await ctx.send("❌ Nenhuma peça encontrada na planilha.")
            return

        nomes.sort(key=lambda x: x.lower())
        tamanho_pagina = 20
        paginas = [nomes[i:i + tamanho_pagina] for i in range(0, len(nomes), tamanho_pagina)]

        view = PaginadorView(paginas)
        await ctx.send(view.formatar_pagina(), view=view)

async def setup(bot):
    await bot.add_cog(PecasList(bot))
