import discord
import csv
import aiohttp
import random
import re
import difflib
from collections import Counter
from discord.ext import commands

MAX_PACKS = 20

PACKS = {
    "navicust pack | rare": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv",
        "tipo": "program",
        "emoji": "🧩"
    },
    "battlechip pack": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=1394317870&single=true&output=csv",
        "tipo": "chip",
        "emoji": "💾"
    }
}

BANNED_PARTS = {
    "navicust pack | rare": {"TrueLove"},
    "battlechip pack": {"FolderBack"}
}

RARITY_ORDER = ["C", "U", "R", "SR", "SSR"]

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # MERCADO (VOLTOU 😈)
    # =========================
    @commands.command(name="mercado")
    async def mercado(self, ctx, *, opcao: str = None):

        if not opcao:
            await ctx.send(
                "**🛒 Mercado**\n"
                "Opções disponíveis:\n\n"
                "• `NaviCust Pack | Rare`\n"
                "• `BattleChip Pack`\n"
            )
            return

        partes = opcao.rsplit(" ", 1)
        nome_pack = partes[0].lower().strip()
        quantidade = 1

        if len(partes) == 2 and partes[1].isdigit():
            quantidade = int(partes[1])

        if nome_pack not in PACKS:
            await ctx.send("❌ Pack inválido.")
            return

        if quantidade < 1 or quantidade > MAX_PACKS:
            await ctx.send(f"❌ Entre 1 e {MAX_PACKS}.")
            return

        pack = PACKS[nome_pack]

        async with aiohttp.ClientSession() as session:
            async with session.get(pack["url"]) as resp:
                data = await resp.text()

        linhas = data.splitlines()
        reader = list(csv.DictReader(linhas))

        comuns, incomuns, raros, sr, ssr = [], [], [], [], []

        for linha in reader:
            nome = linha.get("Nome", "").strip()
            raridade = linha.get("Rarity", "").strip()

            if not nome or not raridade:
                continue

            if nome in BANNED_PARTS.get(nome_pack, set()):
                continue

            if raridade == "C":
                comuns.append(nome)
            elif raridade == "U":
                incomuns.append(nome)
            elif raridade == "R":
                raros.append(nome)
            elif raridade == "SR":
                sr.append(nome)
            elif raridade == "SSR":
                ssr.append(nome)

        msg = f"**📦 {quantidade}x {nome_pack.title()}**\n\n"

        for i in range(quantidade):
            # Slot 1
            if random.random() < 0.5:
                s1 = random.choice(comuns)
                r1 = "C"
            else:
                s1 = random.choice(incomuns)
                r1 = "U"

            # Slot 2
            if random.random() < 0.5:
                s2 = random.choice(comuns)
                r2 = "C"
            else:
                s2 = random.choice(incomuns)
                r2 = "U"

            # Slot 3
            dado = random.randint(1, 20)
            if dado <= 14:
                s3 = random.choice(raros)
                r3 = "R"
            elif dado <= 19:
                s3 = random.choice(sr)
                r3 = "SR"
            else:
                s3 = random.choice(ssr)
                r3 = "SSR"

            msg += (
                f"**Pack {i+1}:**\n"
                f"{pack['emoji']} {s1} ({r1})\n"
                f"{pack['emoji']} {s2} ({r2})\n"
                f"✨ {s3} (🎲 {dado} → {r3})\n\n"
            )

        await ctx.send(msg)

    # =========================
    # TRADER (COM IMAGEM)
    # =========================
    @commands.command(name="trader")
    async def trader(self, ctx):

        embed = discord.Embed(
            title="🔄 Battler Trader",
            description="Use `!inserir` para trocar itens!",
            color=discord.Color.blue()
        )

        embed.set_image(url="https://cdn.discordapp.com/attachments/1432893983046242346/1495525077691924561/TEPPEN_3ME_081_art.webp")

        await ctx.send(embed=embed)

    # =========================
    # INSERIR (igual antes)
    # =========================
    @commands.command(name="inserir")
    async def inserir(self, ctx):

        linhas = ctx.message.content.split("\n")[1:]

        itens = []
        for linha in linhas:
            match = re.match(r"(.+?)\s*\((\d+)x\)", linha)
            if match:
                itens += [match.group(1)] * int(match.group(2))
            else:
                itens.append(linha.strip())

        if len(itens) < 5:
            await ctx.send("❌ Mínimo 5 itens.")
            return

        dados = await self.carregar_dados()
        mapa = {d["nome"].lower(): d for d in dados}

        encontrados = []
        for nome in itens:
            if nome.lower() in mapa:
                encontrados.append(mapa[nome.lower()])
            else:
                sugestao = difflib.get_close_matches(nome.lower(), mapa.keys(), 1)
                await ctx.send(f"❌ {nome} não encontrado. Talvez: {sugestao}")
                return

        grupos = [encontrados[i:i+5] for i in range(0, len(encontrados), 5)]

        resultados = []
        for g in grupos:
            resultados.append(self.processar_grupo(g, dados))

        await ctx.send("\n".join(resultados))

    async def carregar_dados(self):
        dados = []
        async with aiohttp.ClientSession() as session:
            for nome_pack, info in PACKS.items():
                async with session.get(info["url"]) as resp:
                    text = await resp.text()

                for row in csv.DictReader(text.splitlines()):
                    nome = row.get("Nome", "").strip()
                    rar = row.get("Rarity", "").strip()

                    if nome and rar:
                        dados.append({
                            "nome": nome,
                            "raridade": rar,
                            "tipo": info["tipo"]
                        })
        return dados

    def processar_grupo(self, grupo, dados):
        tipo = Counter(d["tipo"] for d in grupo).most_common(1)[0][0]
        rar = Counter(d["raridade"] for d in grupo).most_common(1)[0][0]

        usados = {d["nome"].lower() for d in grupo}

        pool = [
            d["nome"] for d in dados
            if d["tipo"] == tipo and d["raridade"] == rar and d["nome"].lower() not in usados
        ]

        return random.choice(pool) if pool else "❌ Nada encontrado"

async def setup(bot):
    await bot.add_cog(Sistema(bot)
