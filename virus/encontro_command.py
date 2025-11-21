from discord.ext import commands
import aiohttp
import csv
import random
import re


class EncontroCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = (
            "https://docs.google.com/spreadsheets/d/e/"
            "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
            "pub?gid=1726418026&single=true&output=csv"
        )

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

        area_proc = area_nome.lower().strip()
        virus = []

        for row in reader:
            col_area = next((k for k in row if "area" in k.lower()), None)
            col_nome = next((k for k in row if "name" in k.lower()), None)

            if col_area and col_nome:
                area = row[col_area].strip()
                nome = row[col_nome].strip()
                if area and nome:
                    if area_proc == area.lower() or area_proc in area.lower():
                        virus.append(nome)

        return virus if virus else None

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
            sorteados = [random.choice(virus_area) for _ in range(qtd)]

            texto = f"🎲 Quantidade de Vírus: {qtd}\n\n"
            texto += "🦠 Resultado:\n" + "\n".join(f"• {v}" for v in sorteados)

            await self.enviar_paginado(ctx, texto)
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

            rolls = []
            total_virus = []

            for i in range(1, players + 1):
                qtd = random.randint(1, 3)
                rolls.append(f"🎲 Jogador {i} → {qtd} vírus")
                selecionados = [random.choice(virus_area) for _ in range(qtd)]
                total_virus.extend(selecionados)

            texto = "\n".join(rolls)
            texto += "\n\n🦠 Resultado final:\n"
            texto += "\n".join(f"• {v}" for v in total_virus)

            await self.enviar_paginado(ctx, texto)
            return

        # ---------------------------------------------------------
        # Caso 3 — virus:X
        # ---------------------------------------------------------
        if opcional.lower().startswith("virus:"):
            try:
                qtd = int(opcional.split(":")[1])
                if qtd <= 0:
                    raise ValueError
            except:
                await ctx.send("❌ Use: `!encontro Área virus:5`")
                return

            sorteados = [random.choice(virus_area) for _ in range(qtd)]

            texto = f"🎲 Quantidade definida: {qtd}\n\n"
            texto += "🦠 Resultado:\n"
            texto += "\n".join(f"• {v}" for v in sorteados)

            await self.enviar_paginado(ctx, texto)
            return

        await ctx.send(
            "❌ Parâmetro inválido. Use:\n"
            "`!encontro Área`\n"
            "`!encontro Área players:X`\n"
            "`!encontro Área virus:X`"
        )

    # -------------------------------------------------------------
    # Comando !vamo (corrigido, igual ao !local)
    # -------------------------------------------------------------
    @commands.command(name="vamo")
    async def vamo(self, ctx):

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            linhas = csv_text.splitlines()
            if "Area" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            virus_todas = []

            for row in reader:
                col_area = next((k for k in row if "area" in k.lower()), None)
                col_nome = next((k for k in row if "name" in k.lower()), None)

                if col_area and col_nome:
                    area = row[col_area].strip().lower()
                    nome = row[col_nome].strip()

                    # igual ao !local → sem acentos, sem frescura
                    if "todas as areas" in area and nome:
                        virus_todas.append(nome)

            if not virus_todas:
                await ctx.send("❌ Nenhum vírus encontrado para 'Todas As Areas'.")
                return

            virus_todas = sorted(set(virus_todas))

            texto = "🦠 **Vírus de Todas As Areas:**\n"
            texto += "\n".join(f"• {v}" for v in virus_todas)

            await self.enviar_paginado(ctx, texto)

        except Exception as e:
            print(f"❌ Erro no comando !vamo: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar os vírus.")

    # -------------------------------------------------------------
    # Paginação — SEM BLOCO DE CÓDIGO
    # -------------------------------------------------------------
    async def enviar_paginado(self, ctx, texto):
        if len(texto) <= 1990:
            await ctx.send(texto)
            return

        partes = [texto[i:i + 1990] for i in range(0, len(texto), 1990)]
        for parte in partes:
            await ctx.send(parte)


async def setup(bot):
    await bot.add_cog(EncontroCommand(bot))
