from discord.ext import commands
import aiohttp
import csv
import random
import re
import unicodedata
from collections import Counter


class EncontroCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = (
            "https://docs.google.com/spreadsheets/d/e/"
            "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
            "pub?gid=1726418026&single=true&output=csv"
        )

    # -------------------------------------------------------------
    # Função para limpar texto (remove acentos e normaliza)
    # -------------------------------------------------------------
    def limpar_texto(self, t: str):
        t = t.lower().strip()
        t = unicodedata.normalize("NFD", t)
        t = "".join(c for c in t if unicodedata.category(c) != "Mn")
        return t

    # -------------------------------------------------------------
    # Buscar vírus da área
    # -------------------------------------------------------------
    async def coletar_virus_da_area(self, area_nome):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                if resp.status != 200:
                    return None
                csv_text = await resp.text()

        linhas = csv_text.splitlines()
        if "Area" not in linhas[0]:
            linhas = linhas[1:]

        reader = csv.DictReader(linhas)
        reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

        area_proc = self.limpar_texto(area_nome)
        virus = []
        virus_todas = []

        for row in reader:
            col_area = next((k for k in row if "area" in k.lower()), None)
            col_nome = next((k for k in row if "name" in k.lower()), None)

            if col_area and col_nome:
                area = self.limpar_texto(row[col_area])
                nome = row[col_nome].strip()
                if area and nome:
                    if area_proc == area or area_proc in area:
                        virus.append(nome)
                    if "todas as areas" in area:
                        virus_todas.append(nome)

        virus_final = virus + virus_todas
        return virus_final if virus_final else None

    # -------------------------------------------------------------
    # Comando !encontro
    # -------------------------------------------------------------
    @commands.command(name="encontro")
    async def encontro(self, ctx, *, entrada: str = None):

        if not entrada:
            await ctx.send("❌ Use: `!encontro NomeDaArea`")
            return

        match = re.search(r"(players:\s*\d+|virus:\s*\d+)$", entrada, re.IGNORECASE)

        if match:
            opcional = match.group(1).replace(" ", "")
            area = entrada[:match.start()].strip()
        else:
            opcional = ""
            area = entrada.strip()

        virus_area = await self.coletar_virus_da_area(area)
        if not virus_area:
            await ctx.send(f"❌ Nenhum vírus encontrado na área **{area}**.")
            return

        # ---------------------------------------------------------
        # Caso 1 — sem parâmetro
        # ---------------------------------------------------------
        if opcional == "":
            qtd = random.randint(1, 3)
            contagem = Counter(random.choices(virus_area, k=qtd))

            texto = f"🎲 Quantidade de Vírus: {qtd}\n\n🦠 Resultado:\n"
            texto += "\n".join(
                f"• {nome} ({q}x)" if q > 1 else f"• {nome}"
                for nome, q in contagem.items()
            )

            await ctx.send(texto)
            return

        # ---------------------------------------------------------
        # Caso 2 — players:X
        # ---------------------------------------------------------
        if opcional.lower().startswith("players:"):
            try:
                players = int(opcional.split(":")[1])
                if players <= 0:
                    raise ValueError
            except:
                await ctx.send("❌ Use: `!encontro Área players:3`")
                return

            total_contagem = Counter()
            rolls = []

            for i in range(1, players + 1):
                qtd = random.randint(1, 3)
                picks = random.choices(virus_area, k=qtd)
                total_contagem.update(picks)
                rolls.append(f"🎲 Jogador {i} → {qtd} vírus")

            texto = "\n".join(rolls)
            texto += "\n\n🦠 Resultado final:\n"
            texto += "\n".join(
                f"• {nome} ({q}x)" if q > 1 else f"• {nome}"
                for nome, q in total_contagem.items()
            )

            await ctx.send(texto)
            return

        # ---------------------------------------------------------
        # Caso 3 — virus:X  (SUPORTA 1 MILHÃO)
        # ---------------------------------------------------------
        if opcional.lower().startswith("virus:"):
            try:
                qtd = int(opcional.split(":")[1])
                if qtd <= 0:
                    raise ValueError
            except:
                await ctx.send("❌ Use: `!encontro Área virus:5`")
                return

            contagem = Counter(random.choices(virus_area, k=qtd))

            texto = f"🎲 Quantidade definida: {qtd}\n\n🦠 Resultado:\n"
            texto += "\n".join(
                f"• {nome} ({q}x)" if q > 1 else f"• {nome}"
                for nome, q in contagem.items()
            )

            await ctx.send(texto)
            return

        await ctx.send(
            "❌ Parâmetro inválido. Use:\n"
            "`!encontro Área`\n"
            "`!encontro Área players:X`\n"
            "`!encontro Área virus:X`"
        )


async def setup(bot):
    await bot.add_cog(EncontroCommand(bot))
