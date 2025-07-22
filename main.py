import discord
from discord.ext import commands
import os
import asyncio
from manter_vivo import manter_vivo

# Ativa o sistema de manter o bot online (em ambientes como Replit)
manter_vivo()

# Permissões do bot
intents = discord.Intents.default()
intents.message_content = True

# Inicializa o bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ──▼ Carregar extensões assíncronas ────────────────────────────────────────
async def setup_extensoes():
    try:
        # Extensões locais (virus e chips)
        if "virus.virus_command" not in bot.extensions:
            await bot.load_extension("virus.virus_command")
            print("🦠 Extensão virus.virus_command carregada com sucesso!")

        if "virus.viruslist" not in bot.extensions:
            await bot.load_extension("virus.viruslist")
            print("📜 Extensão virus.viruslist carregada com sucesso!")

        if "Chip.chip_command" not in bot.extensions:
            await bot.load_extension("Chip.chip_command")
            print("💾 Extensão Chip.chip_command carregada com sucesso!")

        if "Chip.chips_list" not in bot.extensions:
            await bot.load_extension("Chip.chips_list")
            print("📜 Extensão Chip.chips_list carregada com sucesso!")

        # Extensões do módulo Navi
        if "Navi.Pecas" not in bot.extensions:
            await bot.load_extension("Navi.Pecas")
            print("🧩 Extensão Navi.Pecas carregada com sucesso!")

        if "Navi.pecaslist" not in bot.extensions:
            await bot.load_extension("Navi.pecaslist")
            print("📜 Extensão Navi.pecaslist carregada com sucesso!")

        # Extensão de Batalha
        if "batalha.batalha" not in bot.extensions:
            await bot.load_extension("batalha.batalha")
            print("⚔️ Extensão batalha.batalha carregada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao carregar extensões: {e}")
# ──▲------------------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"✅ Bot está online como {bot.user}")

# ──▼ Comando de teste ------------------------------------------------------
@bot.command()
async def oi(ctx):
    await ctx.send(f"Fala {ctx.author.mention}! Eu tô vivo aqui no servidor!")
# ──▲------------------------------------------------------------------------

# ──▼ Comando !ajuda --------------------------------------------------------
@bot.command()
async def ajuda(ctx):
    ajuda_texto = (
        "📘 **Comandos disponíveis:**\n\n"
        "🔹 `!virus NomeDoVirus`\n"
        " Mostra todos os dados cadastrados daquele vírus (HP, Atk, Dmg, etc.).\n\n"
        "🔹 `!viruslist`\n"
        " Exibe a lista de todos os vírus disponíveis na planilha, em ordem alfabética.\n\n"
        "🔹 `!chipslist`\n"
        " Exibe a lista de todos os chips disponíveis na planilha, em ordem alfabética.\n\n"
        "🔹 `!chip NomeDoChip`\n"
        " Mostra os dados de um chip específico.\n\n"
        "🔹 `!pecaslist`\n"
        " Exibe a lista de todas as peças disponíveis na planilha.\n\n"
        "🔹 `!batalha Aliado1 10/10, Aliado2 15/15 vs Inimigo1 12/12, Inimigo2 20/20`\n"
        " Inicia uma nova batalha com os personagens e seus PVs.\n\n"
        "🔹 `!rodada Nome faz algo com Alvo 3`\n"
        " Ou `Nome faz algo (3) no Alvo`\n"
        " Registra uma ação com dano, seguindo a ordem dos turnos.\n\n"
        "🔹 `!passar NomeDoPersonagem`\n"
        " O personagem atual decide passar sua vez.\n\n"
        "🔹 `!status`\n"
        " Exibe o status atual da batalha em andamento.\n\n"
        "🔹 `!encerrar`\n"
        " Encerra a batalha atual manualmente.\n\n"
        "🔹 `!oi`\n"
        " Só confirma que o bot está vivo no servidor 😄\n\n"
        "🛠️ Novos comandos serão adicionados conforme o sistema evolui!"
    )
    await ctx.send(ajuda_texto)
# ──▲------------------------------------------------------------------------

# ──▼ Executa o bot ---------------------------------------------------------
async def main():
    async with bot:
        await setup_extensoes()
        try:
            await bot.start(os.environ["TOKEN"])
        except KeyError:
            print("❌ TOKEN não encontrado! Certifique-se de definir a variável de ambiente 'TOKEN'.")
        except Exception as e:
            print(f"❌ Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
# ──▲------------------------------------------------------------------------
