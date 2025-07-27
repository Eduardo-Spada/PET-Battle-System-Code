from discord.ext import commands
import aiohttp
import csv
import discord

# 🔹 Dicionário para imagens
from Chip.chips_imagens import chips_imagens


class ChipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chip")
    async def chip(self, ctx, *, nome: str = None):
        """Busca as informações de um Chip pelo nome."""
        if not nome:
            await ctx.send("❌ Use: `!chip NomeDoChip` para buscar os dados.")
            return

        try:
            # URL da aba BattleChips (CSV)
            url = (
                "https://docs.google.com/spreadsheets/d/e/"
                "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
                "pub?gid=1394317870&single=true&output=csv"
            )

            # 🔹 Fazendo requisição para obter os dados da planilha
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            # 🔹 Processando CSV
            linhas = csv_text.splitlines()
            if "Nome" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            chip_encontrado = None
            nome_proc = nome.lower().strip()

            # 🔹 Busca exata
            for row in reader:
                col_nome = next((k for k in row if "nome" in k.lower()), None)
                if not col_nome:
                    continue
                if nome_proc == row[col_nome].strip().lower():
                    chip_encontrado = row
                    break

            # 🔹 Busca aproximada
            if not chip_encontrado:
                for row in reader:
                    col_nome = next((k for k in row if "nome" in k.lower()), None)
                    if not col_nome:
                        continue
                    if nome_proc in row[col_nome].strip().lower():
                        chip_encontrado = row
                        break

            # 🔹 Se não encontrou nada
            if not chip_encontrado:
                await ctx.send(f"❌ Nenhum chip com nome parecido a **{nome}** foi encontrado.")
                return

            def safe(chave):
                return chip_encontrado.get(chave, "Desconhecido")

            nome_chip = safe("Nome")
            imagem_url = chips_imagens.get(nome_chip.lower().strip())

            # 🔹 Montando mensagem de texto puro (sem embed)
            msg = (
                f"💾 **Chip:** {nome_chip}\n"
                f"**Elemento:** {safe('Elemento')}\n"
                f"**Dano:** {safe('Dano')}\n"
                f"**Efeito:** {safe('Efeito')}\n"
                f"**Rarity:** {safe('Rarity')}"
            )

            # Se houver imagem, adiciona o link na mesma mensagem
            if imagem_url:
                msg += f"\n{imagem_url}"

            await ctx.send(msg)

        except Exception as e:
            print(f"❌ Erro no comando !chip: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar o chip.")


# Setup para discord.py 2.x
async def setup(bot):
    await bot.add_cog(ChipCommand(bot))
