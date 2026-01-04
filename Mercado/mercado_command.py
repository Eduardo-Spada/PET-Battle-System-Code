import discord
import csv
import aiohttp
import random
from discord.ext import commands

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv"

BANNED_PARTS = {"TrueLove"}
MAX_PACKS = 20

class Mercado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mercado")
    async def mercado(self, ctx, *, opcao: str = None):
        # ── Menu ──────────────────────────────────
        if not opcao:
            await ctx.send(
                "**🛒 Mercado**\n"
                "Opções disponíveis:\n"
                "• `NaviCust Pack | Rare` — 500 Zenny\n"
                "_Um pacote brilhante que contém três partes NaviCustomizer — "
                "uma delas garantida como **Rare ou superior**!_"
            )
            return

        # ── Parse opção + quantidade ──────────────
        partes = opcao.rsplit(" ", 1)
        nome_pack = partes[0].lower()
        quantidade = 1

        if len(partes) == 2 and partes[1].isdigit():
            quantidade = int(partes[1])

        if nome_pack != "navicust pack | rare":
            await ctx.send("❌ Opção inválida.")
            return

        if quantidade < 1 or quantidade > MAX_PACKS:
            await ctx.send(f"❌ Você pode comprar entre 1 e {MAX_PACKS} pacotes por vez.")
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
            print(f"Erro ao buscar CSV: {e}")
            await ctx.send("❌ Erro ao buscar dados.")
            return

        # ── Correção do cabeçalho ──────────────────
        linhas = data.splitlines()
        if "Nome" not in linhas[0]:
            linhas = linhas[1:]

        reader = list(csv.DictReader(linhas))

        # Normaliza valores None
        for r in reader:
            for k in r:
                if r[k] is None:
                    r[k] = ""

        # ── Separar por raridade (ignorando banidos) ─
        comuns = []
        incomuns = []
        raros = []
        super_raros = []
        ssr = []

        for linha in reader:
            nome = linha.get("Nome", "").strip()
            raridade = linha.get("Rarity", "").strip()

            if not nome or not raridade:
                continue

            if nome in BANNED_PARTS:
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

        # ── Abrir pacotes ──────────────────────────
        mensagem = f"**📦 Abertura de {quantidade}x NaviCust Pack | Rare**\n\n"

        for i in range(1, quantidade + 1):
            # Slot 1
            if random.choice(["C", "U"]) == "C":
                slot1 = random.choice(comuns)
                rar1 = "C"
            else:
                slot1 = random.choice(incomuns)
                rar1 = "U"

            # Slot 2
            if random.choice(["C", "U"]) == "C":
                slot2 = random.choice(comuns)
                rar2 = "C"
            else:
                slot2 = random.choice(incomuns)
                rar2 = "U"

            # Slot 3
            dado = random.randint(1, 20)
            if 1 <= dado <= 14:
                slot3 = random.choice(raros)
                rar3 = "R"
            elif 15 <= dado <= 19:
                slot3 = random.choice(super_raros)
                rar3 = "SR"
            else:
                slot3 = random.choice(ssr)
                rar3 = "SSR"

            mensagem += (
                f"**Pack {i}:**\n"
                f"🧩 Slot 1: {slot1} ({rar1})\n"
                f"🧩 Slot 2: {slot2} ({rar2})\n"
                f"✨ Slot 3: {slot3} (🎲 {dado} → {rar3})\n\n"
            )

        await ctx.send(mensagem)

async def setup(bot):
    await bot.add_cog(Mercado(bot))
