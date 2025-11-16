from discord.ext import commands
import aiohttp
import csv

class LocalCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = (
            "https://docs.google.com/spreadsheets/d/e/"
            "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
            "pub?gid=1726418026&single=true&output=csv"
        )

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
            # Pula a primeira linha se não tiver 'Area' no cabeçalho
            if "Area" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            areas = set()
            for row in reader:
                col_area = next((k for k in row if "area" in k.lower()), None)
                if col_area:
                    area = row[col_area].strip()
                    if area:
                        areas.add(area)

            if not areas:
                await ctx.send("❌ Nenhuma área encontrada na planilha.")
                return

            areas_list = sorted(areas)
            texto = f"📍 **Áreas Disponíveis ({len(areas_list)}):**\n" + "\n".join(f"• {a}" for a in areas_list)
            await ctx.send(texto)

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
            if "Area" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            area_proc = area_nome.lower().strip()
            virus_encontrados = []

            for row in reader:
                col_area = next((k for k in row if "area" in k.lower()), None)
                col_nome = next((k for k in row if "name" in k.lower()), None)
                if col_area and col_nome:
                    area = row[col_area].strip()
                    nome_virus = row[col_nome].strip()
                    if area and nome_virus:
                        if area_proc == area.lower() or area_proc in area.lower():
                            virus_encontrados.append(nome_virus)

            if not virus_encontrados:
                await ctx.send(f"❌ Nenhum vírus encontrado na área **{area_nome}**.")
                return

            virus_encontrados = sorted(virus_encontrados)
            texto = f"🦠 **Vírus encontrados na área {area_nome} ({len(virus_encontrados)}):**\n" + "\n".join(f"• {v}" for v in virus_encontrados)
            await ctx.send(texto)

        except Exception as e:
            print(f"❌ Erro no comando !local: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar os vírus da área.")

# Setup assíncrono para discord.py 2.x
async def setup(bot):
    await bot.add_cog(LocalCommand(bot))
