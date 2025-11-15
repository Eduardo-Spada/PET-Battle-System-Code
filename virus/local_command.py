from discord.ext import commands
import aiohttp
import csv
import unicodedata

class LocalCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # URL da planilha CSV pública
        self.url = (
            "https://docs.google.com/spreadsheets/d/e/"
            "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
            "pub?gid=1726418026&single=true&output=csv"
        )

    def normalize(self, texto):
        """Remove acentos, coloca em minúsculo e tira espaços extras."""
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode().lower().strip()

    @commands.command(name="locais")
    async def locais(self, ctx):
        """Lista todas as áreas disponíveis na planilha."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as resp:
                    if resp.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            linhas = csv_text.splitlines()
            reader = csv.DictReader(linhas)
            # Normaliza os nomes das colunas
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            areas = set()
            for row in reader:
                # Normaliza keys e values
                row = {k.strip().lower(): v for k, v in row.items()}
                area = row.get("area", "").strip()
                if area:
                    areas.add(area)

            if not areas:
                await ctx.send("❌ Nenhuma área encontrada na planilha.")
                return

            areas_list = sorted(areas)
            texto = f"📍 **Áreas Disponíveis ({len(areas_list)}):**\n" + "\n".join(f"• {a}" for a in areas_list)

            # Divide em blocos se muito longo
            if len(texto) > 2000:
                partes = [texto[i:i + 1990] for i in range(0, len(texto), 1990)]
                for parte in partes:
                    await ctx.send(f"```{parte}```")
            else:
                await ctx.send(f"```{texto}```")

        except Exception as e:
            print(f"❌ Erro no comando !locais: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar listar as áreas.")

    @commands.command(name="local")
    async def local(self, ctx, *, area_nome: str = None):
        """Lista todos os vírus em uma área específica."""
        if not area_nome:
            await ctx.send("❌ Use: `!local NomeDaArea` para buscar os vírus dessa área.")
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as resp:
                    if resp.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            linhas = csv_text.splitlines()
            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            area_proc = self.normalize(area_nome)
            virus_encontrados = []

            for row in reader:
                # Normaliza keys e values
                row = {k.strip().lower(): v for k, v in row.items()}
                area = row.get("area", "").strip()
                nome_virus = row.get("name", "").strip()

                if area and nome_virus:
                    area_norm = self.normalize(area)
                    # Busca exata ou parcial
                    if area_proc == area_norm or area_proc in area_norm:
                        virus_encontrados.append(nome_virus)

            if not virus_encontrados:
                await ctx.send(f"❌ Nenhum vírus encontrado na área **{area_nome}**.")
                return

            virus_encontrados = sorted(virus_encontrados)
            texto = f"🦠 **Vírus encontrados na área {area_nome} ({len(virus_encontrados)}):**\n" + "\n".join(f"• {v}" for v in virus_encontrados)

            # Divide em blocos se muito longo
            if len(texto) > 2000:
                partes = [texto[i:i + 1990] for i in range(0, len(texto), 1990)]
                for parte in partes:
                    await ctx.send(f"```{parte}```")
            else:
                await ctx.send(f"```{texto}```")

        except Exception as e:
            print(f"❌ Erro no comando !local: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar os vírus da área.")

# Setup assíncrono para discord.py 2.x
async def setup(bot):
    await bot.add_cog(LocalCommand(bot))
