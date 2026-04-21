import discord
import csv
import aiohttp
import random
from discord.ext import commands

MAX_PACKS = 20

PACKS = {
    "navicust pack | rare": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=0&single=true&output=csv",
        "nome_coluna": "Nome",
        "raridade_coluna": "Rarity",
        "preco": 500,
        "emoji": "🧩"
    },
    "battlechip pack": {
        "url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=1394317870&single=true&output=csv",
        "nome_coluna": "Nome",
        "raridade_coluna": "Rarity",
        "preco": 500,
        "emoji": "💾"
    }
}

BANNED_PARTS = {
    "navicust pack | rare": {"TrueLove", "SlghBell"},
    "battlechip pack": {"FolderBack"}
}

class Mercado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mercado")
    async def mercado(self, ctx, *, opcao: str = None):

        # ── MENU ─────────────────────────────
        if not opcao:
            await ctx.send(
                "**🛒 Mercado**\n"
                "Opções disponíveis:\n\n"
                "• `NaviCust Pack | Rare` — 500 Zenny\n"
                "_3 partes, 1 garantida R ou superior_\n\n"
                "• `BattleChip Pack` — 500 Zenny\n"
                "_3 chips, 1 garantido R ou superior_\n\n"
                "• `ElementPack | Elemento`\n"
                "_Pacote especial (não comprável)_\n"
                "_Use: !mercado ElementPack fire 1_"
            )
            return

        # ── PARSE ────────────────────────────
        partes = opcao.split()
        quantidade = 1

        if partes[-1].isdigit():
            quantidade = int(partes[-1])
            partes = partes[:-1]

        # ── ELEMENT PACK ─────────────────────
        if len(partes) >= 2 and partes[0].lower() == "elementpack":
            elemento = partes[1].lower()

            url = PACKS["battlechip pack"]["url"]

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            await ctx.send("❌ Erro ao acessar planilha.")
                            return
                        text = await resp.text()
            except:
                await ctx.send("❌ Erro ao buscar dados.")
                return

            linhas = text.splitlines()

            if "Nome" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)

            # 🔥 limpeza (IMPORTANTE)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            filtrados = []

            for row in reader:
                nome = row.get("Nome", "").strip()
                rar = row.get("Rarity", "").strip()

                # 🔥 DETECTA COLUNA ELEMENTO AUTOMATICAMENTE
                col_elemento = next((k for k in row if "elemento" in k.lower()), None)
                if not col_elemento:
                    continue

                elem = row[col_elemento].strip().lower()

                if not nome or not rar:
                    continue

                if elem == elemento:
                    filtrados.append((nome, rar))

            if not filtrados:
                await ctx.send("❌ Nenhum chip encontrado pra esse elemento.")
                return

            # 🔥 SEPARAÇÃO POR RARIDADE (SUA LÓGICA)
            comuns, incomuns, raros, sr, ssr = [], [], [], [], []

            for nome, rar in filtrados:
                if rar == "C":
                    comuns.append(nome)
                elif rar == "U":
                    incomuns.append(nome)
                elif rar == "R":
                    raros.append(nome)
                elif rar == "SR":
                    sr.append(nome)
                elif rar == "SSR":
                    ssr.append(nome)

            if not (comuns and incomuns and raros):
                await ctx.send("❌ Dados insuficientes para esse elemento.")
                return

            msg = f"🌟 **ElementPack | {elemento.title()} x{quantidade}**\n\n"

            for i in range(1, quantidade + 1):

                # Slot 1
                if random.random() < 0.5:
                    slot1 = random.choice(comuns)
                    rar1 = "C"
                else:
                    slot1 = random.choice(incomuns)
                    rar1 = "U"

                # Slot 2
                if random.random() < 0.5:
                    slot2 = random.choice(comuns)
                    rar2 = "C"
                else:
                    slot2 = random.choice(incomuns)
                    rar2 = "U"

                # Slot 3
                dado = random.randint(1, 20)

                if dado <= 14:
                    slot3 = random.choice(raros)
                    rar3 = "R"
                elif dado <= 19:
                    slot3 = random.choice(sr)
                    rar3 = "SR"
                else:
                    slot3 = random.choice(ssr)
                    rar3 = "SSR"

                msg += (
                    f"**Pack {i}:**\n"
                    f"💾 Slot 1: {slot1} ({rar1})\n"
                    f"💾 Slot 2: {slot2} ({rar2})\n"
                    f"✨ Slot 3: {slot3} (🎲 {dado} → {rar3})\n\n"
                )

            await ctx.send(msg)
            return

        # ── PACK NORMAL (INALTERADO) ─────────
        nome_pack = " ".join(partes).lower().strip()

        if nome_pack not in PACKS:
            await ctx.send("❌ Pack inválido.")
            return

        if quantidade < 1 or quantidade > MAX_PACKS:
            await ctx.send(f"❌ Você pode comprar entre 1 e {MAX_PACKS} pacotes.")
            return

        pack = PACKS[nome_pack]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pack["url"]) as response:
                    if response.status != 200:
                        await ctx.send("❌ Erro ao acessar a planilha.")
                        return
                    data = await response.text()
        except:
            await ctx.send("❌ Erro ao buscar dados.")
            return

        linhas = data.splitlines()

        if pack["nome_coluna"] not in linhas[0]:
            linhas = linhas[1:]

        reader = csv.DictReader(linhas)
        reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]
        reader = list(reader)

        comuns, incomuns, raros, sr, ssr = [], [], [], [], []

        for linha in reader:
            nome = linha.get(pack["nome_coluna"], "").strip()
            raridade = linha.get(pack["raridade_coluna"], "").strip()

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

        if not (comuns and incomuns and raros):
            await ctx.send("❌ Dados insuficientes.")
            return

        mensagem = f"**📦 Abertura de {quantidade}x {nome_pack.title()}**\n\n"

        for i in range(1, quantidade + 1):

            slot1 = random.choice(comuns if random.random() < 0.5 else incomuns)
            rar1 = "C" if slot1 in comuns else "U"

            slot2 = random.choice(comuns if random.random() < 0.5 else incomuns)
            rar2 = "C" if slot2 in comuns else "U"

            dado = random.randint(1, 20)

            if dado <= 14:
                slot3 = random.choice(raros)
                rar3 = "R"
            elif dado <= 19:
                slot3 = random.choice(sr)
                rar3 = "SR"
            else:
                slot3 = random.choice(ssr)
                rar3 = "SSR"

            mensagem += (
                f"**Pack {i}:**\n"
                f"{pack['emoji']} Slot 1: {slot1} ({rar1})\n"
                f"{pack['emoji']} Slot 2: {slot2} ({rar2})\n"
                f"✨ Slot 3: {slot3} (🎲 {dado} → {rar3})\n\n"
            )

        await ctx.send(mensagem)


async def setup(bot):
    await bot.add_cog(Mercado(bot))
