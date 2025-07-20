from discord.ext import commands
import aiohttp
import csv

# 👇 importa o dicionário com as imagens
from virus.virus_imagens import virus_imagens

def setup(bot):
    @bot.command()
    async def virus(ctx, *, nome: str = None):
        if not nome:
            await ctx.send("❌ Use: `!virus NomeDoVirus` para buscar os dados.")
            return

        try:
            url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZqlGcNj6u_1zxCt19WvIGYnJ5kxIsyJ9LHscjgSnnKKI5O-7j1en3Ha89PYjFa19zLKErIQMoUrd8/pub?gid=1726418026&single=true&output=csv"

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

            virus_encontrado = None
            nome_proc = nome.lower().strip()

            for row in reader:
                col_nome = next((k for k in row if "name" in k.lower()), None)
                if not col_nome:
                    continue
                if nome_proc == row[col_nome].strip().lower():
                    virus_encontrado = row
                    break

            if not virus_encontrado:
                for row in reader:
                    col_nome = next((k for k in row if "name" in k.lower()), None)
                    if not col_nome:
                        continue
                    if nome_proc in row[col_nome].strip().lower():
                        virus_encontrado = row
                        break

            if not virus_encontrado:
                await ctx.send(f"❌ Nenhum vírus com nome parecido a **{nome}** foi encontrado.")
                return

            def safe(chave):
                return virus_encontrado.get(chave, "Desconhecido")

            resposta = (
                f"📓  **Vírus: {safe('Name')}**\n"
                f"**HP**: {safe('HP')}\n"
                f"**Atk**: {safe('Atk')}\n"
                f"**Dmg**: {safe('Dmg')}\n"
                f"**Dfns**: {safe('Dfns')}\n"
                f"**Init**: {safe('Init')}\n"
                f"**Elemento**: {safe('Elmnto')}\n"
                f"**Plano de Movimento**: {safe('Movement Plan')}\n"
                f"**Área**: {safe('Area')}\n"
                f"**Recompensas**: {safe('Rewards')}\n"
                f"**Special**: {safe('Special')}"
            )

            await ctx.send(resposta)

            # 🔹 Mostra imagem (se tiver) após os dados
            nome_padrao = safe("Name").lower().strip()
            imagem_url = virus_imagens.get(nome_padrao)
            if imagem_url:
                await ctx.send(imagem_url)

        except Exception as e:
            print(f"❌ Erro no comando !virus: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar buscar o vírus.")
