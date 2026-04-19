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
    "navicust pack | rare": {"TrueLove"},
    "battlechip pack": {"FolderBack"}
}

RARITY_ORDER = ["C", "U", "R", "SR", "SSR"]

class Sistema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # CARREGAR DADOS
    # =========================
    async def carregar_dados(self):
        dados = []

        async with aiohttp.ClientSession() as session:
            for nome_pack, info in PACKS.items():
                async with session.get(info["url"]) as resp:
                    if resp.status != 200:
                        continue
                    text = await resp.text()

                linhas = text.splitlines()
                reader = csv.DictReader(linhas)

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

        return dados

    # =========================
    # COMANDO TRADER (COM IMAGEM)
    # =========================
    @commands.command(name="trader")
    async def trader(self, ctx):

        embed = discord.Embed(
            title="🔄 Battler Trader",
            description=(
                "Hm? Tem algo novo na loja...\n"
                "Um **Battler Trader**!\n\n"
                "Você entrega itens e recebe um novo!\n\n"
                "**📜 Regras:**\n"
                "• 5 itens → 1 resultado\n"
                "• Tipo depende da maioria (Chip ou Programa)\n"
                "• Raridade depende da maioria\n"
                "• Empate → raridade mais alta\n"
                "• Itens usados NÃO voltam\n\n"
                "**⚙️ Uso:**\n"
                "`!inserir`\n"
                "Cannon (2x)\n"
                "Sword\n"
            ),
            color=discord.Color.blue()
        )

        # 🔥 COLOCA SUA IMAGEM AQUI
        embed.set_image(url="https://cdn.discordapp.com/attachments/1432893983046242346/1495525077691924561/TEPPEN_3ME_081_art.webp?ex=69e68fc4&is=69e53e44&hm=8c09d8766c398b177a5e8d72041f9f860ba310eaeb8bbc0995cd8f8a4859a8f3&")

        await ctx.send(embed=embed)

    # =========================
    # INSERIR ITENS
    # =========================
    @commands.command(name="inserir")
    async def inserir(self, ctx):

        linhas = ctx.message.content.split("\n")[1:]

        if not linhas:
            await ctx.send("❌ Insira itens abaixo do comando.")
            return

        itens_input = []

        for linha in linhas:
            linha = linha.strip()

            match = re.match(r"(.+?)\s*\((\d+)x\)", linha, re.IGNORECASE)

            if match:
                nome = match.group(1).strip()
                qtd = int(match.group(2))
            else:
                nome = linha
                qtd = 1

            itens_input.extend([nome] * qtd)

        if len(itens_input) < 5:
            await ctx.send("❌ Mínimo de 5 itens.")
            return

        dados = await self.carregar_dados()

        mapa = {d["nome"].lower(): d for d in dados}
        nomes_validos = list(mapa.keys())

        encontrados = []

        for nome in itens_input:
            nome_lower = nome.lower().strip()

            if nome_lower in mapa:
                encontrados.append(mapa[nome_lower])
            else:
                sugestao = difflib.get_close_matches(nome_lower, nomes_validos, n=1)

                if sugestao:
                    await ctx.send(
                        f"❌ Item não encontrado: **{nome}**\n"
                        f"👉 Você quis dizer: **{sugestao[0]}**?"
                    )
                else:
                    await ctx.send(f"❌ Item não encontrado: **{nome}**")

                return

        resultados = []

        grupos = [encontrados[i:i+5] for i in range(0, len(encontrados), 5)]

        for grupo in grupos:
            if len(grupo) < 5:
                continue

            resultado = self.processar_grupo(grupo, dados)
            resultados.append(resultado)

        texto = "**🎰 Resultados do Trader:**\n\n"
        for i, r in enumerate(resultados, 1):
            texto += f"Resultado {i}: {r}\n"

        await ctx.send(texto)

    # =========================
    # PROCESSAR
    # =========================
    def processar_grupo(self, grupo, dados):

        usados = set(d["nome"].lower() for d in grupo)

        tipo_count = Counter(d["tipo"] for d in grupo)

        if tipo_count["chip"] > tipo_count["program"]:
            tipo_final = "chip"
        elif tipo_count["program"] > tipo_count["chip"]:
            tipo_final = "program"
        else:
            tipo_final = random.choice(["chip", "program"])

        rar_count = Counter(d["raridade"] for d in grupo)

        max_qtd = max(rar_count.values())
        empatados = [r for r, q in rar_count.items() if q == max_qtd]

        rar_final = max(empatados, key=lambda r: RARITY_ORDER.index(r))

        pool = [
            d["nome"] for d in dados
            if d["tipo"] == tipo_final
            and d["raridade"] == rar_final
            and d["nome"].lower() not in usados
        ]

        if not pool:
            return "❌ Sem opções disponíveis."

        return random.choice(pool)


async def setup(bot):
    await bot.add_cog(Sistema(bot))
