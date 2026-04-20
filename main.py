import discord
from discord.ext import commands
import os
import asyncio
import traceback
from manter_vivo import manter_vivo

manter_vivo()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

async def setup_extensoes():
    try:
        # ───────── VIRUS ────────��
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

        # ───────── 🔄 TRADER ─────────
        try:
            await bot.load_extension("Mercado.trader")
            print("✅ Trader carregado com sucesso!")
        except Exception as e:
            print("❌ ERRO AO CARREGAR TRADER:")
            print(e)
            traceback.print_exc()

        # ───────── 🔥 TESTE ─────────
        try:
            await bot.load_extension("Teste.trader_test")
            print("✅ Teste.trader_test carregado com sucesso!")
        except Exception as e:
            print("❌ ERRO AO CARREGAR TESTE.TRADER_TEST:")
            print(e)
            traceback.print_exc()

        print("✅ Todas as extensões carregadas!")

    except Exception as e:
        print(f"❌ Erro ao carregar extensões: {e}")
        traceback.print_exc()

@bot.event
async def on_ready():
    print(f"✅ Bot está online como {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.reference:
        try:
            msg_ref = await message.channel.fetch_message(message.reference.message_id)
            if msg_ref.author == bot.user:
                await bot.process_commands(message)
                return
        except:
            pass

    if bot.user in message.mentions:
        await message.channel.send(
            f"👋 Oi {message.author.mention}! Se precisar de ajuda, use **!sos**."
        )

    await bot.process_commands(message)

@bot.command()
async def oi(ctx):
    await ctx.send(f"Fala {ctx.author.mention}! Eu tô vivo aqui no servidor!")

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
