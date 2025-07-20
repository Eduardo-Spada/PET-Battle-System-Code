from discord.ext import commands
import aiohttp
import csv

# ──▼  coloque abaixo do import csv (ou onde achar melhor) ───────────
def adicionar_comando_viruslist(bot):
    @bot.command(name="viruslist")
    async def viruslist(ctx):
        """Lista todos os vírus cadastrados na planilha."""
        try:
            url = (
                "https://docs.google.com/spreadsheets/d/e/"
                "2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/"
                "pub?gid=1726418026&single=true&output=csv"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await ctx.send("⚠️ Não foi possível acessar a planilha.")
                        return
                    csv_text = await resp.text()

            linhas = csv_text.splitlines()
            if "Name" not in linhas[0]:
                linhas = linhas[1:]

            reader = csv.DictReader(linhas)
            reader.fieldnames = [h.strip().replace("\ufeff", "") for h in reader.fieldnames]

            nomes = []
            for row in reader:
                col_nome = next((k for k in row if "name" in k.lower()), None)
                if col_nome:
                    nome_virus = row[col_nome].strip()
                    if nome_virus and nome_virus not in nomes:
                        nomes.append(nome_virus)

            if not nomes:
                await ctx.send("❌ Nenhum vírus encontrado na planilha.")
                return

            nomes.sort()

            # Novo cabeçalho com contador
            header = f"📒 Lista de Vírus Disponíveis ({len(nomes)}):\n"
            corpo = "\n".join(f"• {n}" for n in nomes)
            texto = header + corpo

            if len(texto) > 2000:
                partes = [texto[i:i+1990] for i in range(0, len(texto), 1990)]
                for parte in partes:
                    await ctx.send(f"```{parte}```")
            else:
                await ctx.send(f"```{texto}```")

        except Exception as e:
            print(f"❌ Erro no comando !viruslist: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar listar os vírus.")
# ──▲  fim do comando !viruslist ─────────────────────────────────────

def setup(bot):
    adicionar_comando_viruslist(bot)
