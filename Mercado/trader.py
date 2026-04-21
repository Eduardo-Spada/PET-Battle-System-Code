import discord
import csv
import aiohttp
import random
import re
import difflib
from collections import Counter
from discord.ext import commands

PACKS = {
    "navicust pack | rare": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv",
        "tipo": "program"
    },
    "battlechip pack": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=1394317870&single=true&output=csv",
        "tipo": "chip"
    }
}

BANNED_PARTS = {
    "navicust pack | rare": {"TrueLove", "SlghBell"},
    "battlechip pack": {"FolderBack"}
}

RARITY_ORDER = ["C", "U", "R", "SR", "SSR"]

class Trader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def carregar_dados(self):
        dados = []

        try:
            async with aiohttp.ClientSession() as session:
                for nome_pack, info in PACKS.items():
                    try:
                        async with session.get(info["url"]) as resp:
                            if resp.status != 200:
                                print(f"⚠️ Erro ao buscar {nome_pack}: Status {resp.status}")
                                continue

                            text = await resp.text()

                            # 🔥 CORREÇÃO DO CSV (igual ao comando chip)
                            linhas = text.splitlines()

                            if "Nome" not in linhas[0]:
                                linhas = linhas[1:]

                            reader = csv.DictReader(linhas)
                            reader.fieldnames = [
                                h.strip().replace("\ufeff", "")
                                for h in reader.fieldnames
                            ]

                            for row in reader:
                                nome = row.get("Nome", "").strip()
                                raridade = row.get("Rarity", "").strip()

                                if not nome or not raridade:
                                    continue

                                if nome in BANNED_PARTS.get(nome_pack, set()):
                                    continue

                                dados.append({
                                    "nome": nome,
                                    "raridade": raridade,
                                    "tipo": info["tipo"]
                                })

                    except Exception as e:
                        print(f"❌ Erro ao processar {nome_pack}: {e}")
                        continue

        except Exception as e:
            print(f"❌ ERRO CRÍTICO em carregar_dados(): {e}")
            return []

        print(f"📦 Total de itens carregados: {len(dados)}")

        return dados

    # =========================
    # !TRADER
    # =========================
    @commands.command(name="trader")
    async def trader(self, ctx):

        texto = (
            "🔄 **Battler Trader**\n\n"
            "Bem-vindo ao Battler Trader!\n\n"
            "Você sacrifica itens e recebe um novo aleatório.\n\n"
            "**📜 Regras:**\n"
            "• 5 itens → 1 resultado\n"
            "• Tipo depende da maioria\n"
            "• Raridade depende da maioria\n"
            "• Empate → raridade mais alta\n"
            "• Itens NÃO voltam\n\n"
            "**⚙️ Uso:**\n"
            "`!inserir`\n"
            "Cannon (2x)\n"
            "Sword"
        )

        await ctx.send(texto)

        await ctx.send(
            "https://cdn.discordapp.com/attachments/1432893983046242346/1495525077691924561/TEPPEN_3ME_081_art.webp"
        )

    # =========================
    # !INSERIR
    # =========================
    @commands.command(name="inserir")
    async def inserir(self, ctx):

        linhas = ctx.message.content.split("\n")[1:]

        if not linhas:
            await ctx.send("❌ Insira itens abaixo do comando.")
            return

        itens = []

        for linha in linhas:
            match = re.match(r"(.+?)\s*\((\d+)x\)", linha)

            if match:
                itens += [match.group(1).strip()] * int(match.group(2))
            else:
                itens.append(linha.strip())

        if len(itens) < 5:
            await ctx.send("❌ Mínimo de 5 itens.")
            return

        dados = await self.carregar_dados()

        if not dados:
            await ctx.send("❌ Erro ao carregar dados do servidor.")
            return

        mapa = {d["nome"].lower(): d for d in dados}
        nomes = list(mapa.keys())

        encontrados = []

        for nome in itens:
            n = nome.lower()

            if n in mapa:
                encontrados.append(mapa[n])
            else:
                sugestao = difflib.get_close_matches(n, nomes, 1)

                await ctx.send(
                    f"❌ Item não encontrado: **{nome}**"
                    + (f"\n👉 Você quis dizer: **{sugestao[0]}**?" if sugestao else "")
                )
                return

        grupos = [encontrados[i:i+5] for i in range(0, len(encontrados), 5)]

        resultados = []
        for g in grupos:
            if len(g) < 5:
                continue
            resultados.append(self.processar(g, dados))

        if not resultados:
            await ctx.send("❌ Nenhum resultado válido gerado.")
            return

        await ctx.send("**🎰 Resultado do Trader:**\n" + "\n".join(resultados))

    def processar(self, grupo, dados):

        usados = {d["nome"].lower() for d in grupo}

        tipo_counter = Counter(d["tipo"] for d in grupo)
        rar_counter = Counter(d["raridade"] for d in grupo)

        if not tipo_counter or not rar_counter:
            return "❌ Erro ao processar tipos/raridades"

        tipo = tipo_counter.most_common(1)[0][0]
        rar = rar_counter.most_common(1)[0][0]

        pool = [
            d["nome"] for d in dados
            if d["tipo"] == tipo
            and d["raridade"] == rar
            and d["nome"].lower() not in usados
        ]

        return random.choice(pool) if pool else "❌ Nada encontrado"


async def setup(bot):
    try:
        await bot.add_cog(Trader(bot))
        print("✅ Trader Cog carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao registrar Trader Cog: {e}")
