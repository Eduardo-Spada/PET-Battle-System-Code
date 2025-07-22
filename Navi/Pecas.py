import discord
import csv
import aiohttp
from discord.ext import commands
import difflib

class Pecas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="peça", help="Mostra os dados de uma peça")
    async def peca(self, ctx, *, nome_peca: str = None):
        if not nome_peca:
            await ctx.send("Você precisa digitar o nome da peça. Ex: `!peça AirShoes`")
            return

        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("Erro ao acessar os dados da planilha.")
                        return
                    data = await response.text()
        except Exception as e:
            await ctx.send("Erro ao buscar os dados da peça.")
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

        nome_peca_proc = nome_peca.strip().lower()
        peca_encontrada = None

        # Lista com todos os nomes de peças
        lista_pecas = [linha.get("Nome", "").strip() for linha in reader if linha.get("Nome")]

        # 1ª tentativa: busca exata
        for linha in reader:
            nome = linha.get("Nome", "").strip()
            if nome.lower() == nome_peca_proc:
                peca_encontrada = linha
                break

        # 2ª tentativa: busca aproximada (nome contém parte do texto)
        if not peca_encontrada:
            for linha in reader:
                nome = linha.get("Nome", "").strip()
                if nome_peca_proc in nome.lower():
                    peca_encontrada = linha
                    break

        # Se não achou, tenta sugerir nomes parecidos
        if not peca_encontrada:
            sugestoes = difflib.get_close_matches(nome_peca_proc, [n.lower() for n in lista_pecas], n=1, cutoff=0.6)
            if sugestoes:
                sugestao_real = next((n for n in lista_pecas if n.lower() == sugestoes[0]), sugestoes[0])
                await ctx.send(f"❌ Nenhuma peça encontrada com o nome **{nome_peca}**.\nVocê quis dizer **{sugestao_real}**?")
            else:
                await ctx.send(f"❌ Nenhuma peça encontrada com o nome **{nome_peca}**.")
            return

        # Exibe os dados da peça encontrada
        efeito = peca_encontrada.get("Efeito", "Nenhum").strip()
        raridade = peca_encontrada.get("Rarity", "Desconhecida").strip()

        resposta = (
            f"**🧩 Peça:** {peca_encontrada['Nome']}\n"
            f"**🎯 Efeito:** {efeito or 'Nenhum'}\n"
            f"**⭐ Raridade:** {raridade or 'Desconhecida'}"
        )

        await ctx.send(resposta)

async def setup(bot):
    await bot.add_cog(Pecas(bot))
