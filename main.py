import discord
from discord.ext import commands
import os
import asyncio
import traceback
from manter_vivo import manter_vivo

# Mantém o bot vivo (Replit)
manter_vivo()

# Permissões
intents = discord.Intents.default()
intents.message_content = True

# Bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# ──▼ Carregar extensões ───────────────────────────────────────────────
async def setup_extensoes():
    try:

        # ───────── VIRUS ─────────
        if "virus.virus_command" not in bot.extensions:
            await bot.load_extension("virus.virus_command")

        if "virus.viruslist" not in bot.extensions:
            await bot.load_extension("virus.viruslist")

        if "virus.local_command" not in bot.extensions:
            await bot.load_extension("virus.local_command")

        # ───────── CHIPS ─────────
        if "Chip.chip_command" not in bot.extensions:
            await bot.load_extension("Chip.chip_command")

        if "Chip.chips_list" not in bot.extensions:
            await bot.load_extension("Chip.chips_list")

        # ───────── NAVI ─────────
        if "Navi.Pecas" not in bot.extensions:
            await bot.load_extension("Navi.Pecas")

        if "Navi.pecaslist" not in bot.extensions:
            await bot.load_extension("Navi.pecaslist")

        # ───────── BATALHA ─────────
        if "batalha.batalha" not in bot.extensions:
            await bot.load_extension("batalha.batalha")

        # ───────── LINKS ─────────
        if "Links.doc_command" not in bot.extensions:
            await bot.load_extension("Links.doc_command")

        # ───────── AJUDA ─────────
        if "Ajuda.sos_command" not in bot.extensions:
            await bot.load_extension("Ajuda.sos_command")

        # ───────── ENCONTRO ─────────
        if "virus.encontro_command" not in bot.extensions:
            await bot.load_extension("virus.encontro_command")

        # ───────── MERCADO ─────────
        if "Mercado.mercado_command" not in bot.extensions:
            await bot.load_extension("Mercado.mercado_command")

        # ───────── 🔄 TRADER (COM DEBUG) ─────────
        if "Mercado.trader" not in bot.extensions:
            try:
                await bot.load_extension("Mercado.trader")
                print("✅ Extensão Mercado.trader carregada com sucesso!")
            except Exception as e:
                print("❌ ERRO AO CARREGAR MERCADO.TRADER:")
                print(f"   Tipo: {type(e).__name__}")
                print(f"   Mensagem: {e}")
                traceback.print_exc()

        # ───────── 🔥 TESTE (COM DEBUG) ─────────
        if "Teste.trader_test" not in bot.extensions:
            try:
                print("\n🔍 Tentando carregar Teste.trader_test...")
                await bot.load_extension("Teste.trader_test")
                print("✅ Extensão Teste.trader_test carregada com sucesso!")
            except Exception as e:
                print("❌ ERRO AO CARREGAR TESTE.TRADER_TEST:")
                print(f"   Tipo: {type(e).__name__}")
                print(f"   Mensagem: {e}")
                print("\n📋 Stack trace completo:")
                traceback.print_exc()

        print("\n✅ Todas as extensões processadas!")

    except Exception as e:
        print(f"❌ Erro geral ao carregar extensões: {e}")
        traceback.print_exc()

# ──▼ Bot online ───────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"\n✅ Bot está online como {bot.user}")
    print(f"✅ Extensões carregadas: {len(bot.extensions)}")

# ──▼ Mensagens / menções ──────────────────────────────────────────────
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # evita conflito com replies
    if message.reference:
        try:
            msg_ref = await message.channel.fetch_message(message.reference.message_id)
            if msg_ref.author == bot.user:
                await bot.process_commands(message)
                return
        except:
            pass

    # menção ao bot
    if bot.user in message.mentions:
        await message.channel.send(
            f"👋 Oi {message.author.mention}! Se precisar de ajuda, use **!sos**."
        )

    await bot.process_commands(message)

# ──▼ comando teste ────────────────────────────────────────────────────
@bot.command()
async def oi(ctx):
    await ctx.send(f"Fala {ctx.author.mention}! Eu tô vivo aqui no servidor!")

# ──▼ start ────────────────────────────────────────────────────────────
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
