import discord
import csv
import aiohttp
import random
from discord.ext import commands

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv"

class Mercado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mercado")
    async def mercado(self, ctx, *, opcao: str = None):
        if not opcao:
            await ctx.send(
                "**🛒 Mercado**\n"
                "Opções disponíveis:\n"
                "• `NaviCust Pack | Rare` — 500 Zenny"
            )
            return

        if opcao.lower() != "navicust pack | rare":
            await ctx.send("❌ Opção inválida.")
            return

        # ── Buscar CSV ─────────────────────────────
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(CSV_URL) as response:
                    if response.status != 200:
                        await ctx.send("❌ Erro ao acessar a planilha.")
                        return
                    data = await response.text()
        except Exception as e:
            print(e)
            await ctx.send("❌ Erro ao buscar dados.")
            return

        linhas = data.splitlines()
if "Nome" not in linhas[0]:
    linhas = linhas[1:]

reader = list(csv.DictReader(linhas))

# Normaliza valores None
for r in reader:
    for k in r:
        if r[k] is None:
            r[k] = ""


        # ── Separar por raridade ───────────────────
        comuns, incomuns, raros, super_raros, ssr = [], [], [], [], []

        for linha in reader:
            nome = linha.get("Nome", "").strip()
            raridade = linha.get("Rarity", "").strip()

            if not nome:
                continue

            if raridade == "C":
                comuns.append(nome)
            elif raridade == "U":
                incomuns.append(nome)
            elif raridade == "R":
                raros.append(nome)
            elif raridade == "SR":
                super_raros.append(nome)
            elif raridade == "SSR":
                ssr.append(nome)

        if not (comuns and incomuns and raros):
            await ctx.send("❌ Erro: dados insuficientes na planilha.")
            return

        # ── ROLLS ──────────────────────────────────
        slot1 = random.choice(comuns + incomuns)
        slot2 = random.choice(comuns + incomuns)

        dado = random.randint(1, 20)

        if 1 <= dado <= 14:
            slot3 = random.choice(raros)
            raridade3 = "R"
        elif 15 <= dado <= 19:
            slot3 = random.choice(super_raros)
            raridade3 = "SR"
        else:
            slot3 = random.choice(ssr)
            raridade3 = "SSR"

        # ── Resultado ──────────────────────────────
        resposta = (
            "**📦 NaviCust Pack | Rare aberto!**\n\n"
            f"🧩 **Slot 1:** {slot1} *(C/U)*\n"
            f"🧩 **Slot 2:** {slot2} *(C/U)*\n"
            f"✨ **Slot 3:** {slot3} *(🎲 {dado} → {raridade3})*"
        )

        await ctx.send(resposta)

async def setup(bot):
    await bot.add_cog(Mercado(bot))
