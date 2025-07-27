from discord.ext import commands
from discord import Embed
import aiohttp
import csv

# 👇 importa o dicionário com as imagens
from Chip.chips_imagens import chips_imagens


class ChipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chip")
    async def chip(self, ctx, *, nome: str = None):
        if not nome:
            await ctx.send("❌ Use: `!chip NomeDoChip` para buscar os dados.")
            return

        try:
            url = (
                "https://docs.google.com/spreadsheets/d/e/"
                "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
                "pub?gid=1394317870&single=true&output=csv"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            linhas = csv_text.splitlines()

            # Remove header extra se precisar
            if "Nome" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            chip_encontrado = None
            nome_proc = nome.lower().strip()

            # Busca exata
            for row in reader:
                col_nome = next((k for k in row if "nome" in k.lower()), None)
                if not col_nome:
                    continue
                if nome_proc == row[col_nome].strip().lower():
                    chip_encontrado = row
                    break

            # Busca parcial (se não achou na exata)
            if not chip_encontrado:
                # CSV reader já foi esgotado, então precisa resetar
                linhas = csv_text.splitlines()
                if "Nome" not in linhas[0]:
                    linhas = linhas[1:]
                reader = csv.DictReader(linhas)
                reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

                for row in reader:
                    col_nome = next((k for k in row if "nome" in k.lower()), None)
                    if not col_nome:
                        continue
                    if nome_proc in row[col_nome].strip().lower():
                        chip_encontrado = row
                        break

            if not chip_encontrado:
                await ctx.send(f"❌ Nenhum chip com nome parecido a **{nome}** foi encontrado.")
                return

            def safe(chave):
                return chip_encontrado.get(chave, "Desconhecido")

            # Monta Embed com os dados
            embed = Embed(
                title=f"💾 Chip: {safe('Nome')}",
                color=0x00ffcc
            )
            embed.add_field(name="Elemento", value=safe('Elemento'), inline=False)
            embed.add_field(name="Dano", value=safe('Dano'), inline=False)
            embed.add_field(name="Efeito", value=safe('Efeito'), inline=False)
            embed.add_field(name="Rarity", value=safe('Rarity'), inline=False)

            # Pega imagem e adiciona no embed se existir
            nome_padrao = safe("Nome").lower().strip()
            imagem_url = chips_imagens.get(nome_padrao)
            if imagem_url:
                embed.set_image(url=imagem_url)

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"❌ Erro no comando !chip: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar o chip.")


async def setup(bot):
    await bot.add_cog(ChipCommand(bot))
