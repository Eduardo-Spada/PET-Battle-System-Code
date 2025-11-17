import discord
from discord.ext import commands
import os
import asyncio
from manter_vivo import manter_vivo

# Mantém o bot vivo (Replit)
manter_vivo()

# Permissões
intents = discord.Intents.default()
intents.message_content = True

# Inicializa o bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ──▼ Carregar extensões ───────────────────────────────────────────────
async def setup_extensoes():
    try:
        # Extensões de Vírus
        if "virus.virus_command" not in bot.extensions:
            await bot.load_extension("virus.virus_command")
            print("🦠 Extensão virus.virus_command carregada com sucesso!")

        if "virus.viruslist" not in bot.extensions:
            await bot.load_extension("virus.viruslist")
            print("📜 Extensão virus.viruslist carregada com sucesso!")

        if "virus.local_command" not in bot.extensions:
            await bot.load_extension("virus.local_command")
            print("📍 Extensão virus.local_command carregada com sucesso!")

        # Extensões de Chips
        if "Chip.chip_command" not in bot.extensions:
            await bot.load_extension("Chip.chip_command")
            print("💾 Extensão Chip.chip_command carregada com sucesso!")

        if "Chip.chips_list" not in bot.extensions:
            await bot.load_extension("Chip.chips_list")
            print("📜 Extensão Chip.chips_list carregada com sucesso!")

        # Extensões de Peças / Navi
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

        # Extensão DOC
        if "Links.doc_command" not in bot.extensions:
            await bot.load_extension("Links.doc_command")
            print("📘 Extensão Links.doc_command carregada com sucesso!")

        # Extensão SOS (Ajuda)
        if "Ajuda.sos_command" not in bot.extensions:
            await bot.load_extension("Ajuda.sos_command")
            print("🆘 Extensão Ajuda.sos_command carregada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao carregar extensões: {e}")
# ──▲──────────────────────────────────────────────────────────────────


@bot.event
async def on_ready():
    print(f"✅ Bot está online como {bot.user}")


# ──▼ Comando simples ----------------------------------------------------
@bot.command()
async def oi(ctx):
    await ctx.send(f"Fala {ctx.author.mention}! Eu tô vivo aqui no servidor!")
# ──▲──────────────────────────────────────────────────────────────────


# ──▼ Executar o bot -----------------------------------------------------
async def main():
    async with bot:
        await setup_extensoes()
        try:
            await bot.start(os.environ["TOKEN"])
        except KeyError:
            print("❌ TOKEN não encontrado! Configure 'TOKEN' nas variáveis de ambiente.")
        except Exception as e:
            print(f"❌ Erro ao iniciar o bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
# ──▲──────────────────────────────────────────────────────────────────
