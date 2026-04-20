import discord
from discord.ext import commands
import os
import asyncio
import traceback
import sys
from manter_vivo import manter_vivo

print("\n" + "="*70)
print("🚀 BOT INICIANDO...")
print("="*70)

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
    print("\n" + "="*70)
    print("📦 CARREGANDO EXTENSÕES...")
    print("="*70 + "\n")
    
    extensoes_base = [
        "virus.virus_command",
        "virus.viruslist",
        "virus.local_command",
        "Chip.chip_command",
        "Chip.chips_list",
        "Navi.Pecas",
        "Navi.pecaslist",
        "batalha.batalha",
        "Links.doc_command",
        "Ajuda.sos_command",
        "virus.encontro_command",
        "Mercado.mercado_command",
    ]
    
    # Carregar extensões base
    for extensao in extensoes_base:
        if extensao not in bot.extensions:
            try:
                await bot.load_extension(extensao)
            except Exception as e:
                print(f"❌ Erro ao carregar {extensao}: {e}")
                traceback.print_exc()
    
    # MERCADO.TRADER
    print("\n" + "-"*70)
    print("🔄 Tentando carregar: Mercado.trader")
    print("-"*70)
    
    if "Mercado.trader" not in bot.extensions:
        try:
            print("   ⏳ Carregando Mercado.trader...")
            await bot.load_extension("Mercado.trader")
            print("   ✅ Mercado.trader carregado com sucesso!")
        except commands.ExtensionNotFound as e:
            print(f"   ❌ EXTENSÃO NÃO ENCONTRADA: {e}")
            traceback.print_exc()
        except commands.ExtensionAlreadyLoaded as e:
            print(f"   ⚠️ JÁ ESTAVA CARREGADA: {e}")
        except commands.NoEntryPointError as e:
            print(f"   ❌ SEM FUNÇÃO setup(): {e}")
            traceback.print_exc()
        except commands.ExtensionFailed as e:
            print(f"   ❌ FALHA NA EXECUÇÃO: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"   ❌ ERRO INESPERADO: {type(e).__name__}: {e}")
            traceback.print_exc()
    else:
        print("   ⚠️ Já estava carregada")
    
    # TESTE.TRADER_TEST
    print("\n" + "-"*70)
    print("🔥 Tentando carregar: Teste.trader_test")
    print("-"*70)
    
    if "Teste.trader_test" not in bot.extensions:
        try:
            print("   ⏳ Carregando Teste.trader_test...")
            await bot.load_extension("Teste.trader_test")
            print("   ✅ Teste.trader_test carregado com sucesso!")
        except commands.ExtensionNotFound as e:
            print(f"   ❌ EXTENSÃO NÃO ENCONTRADA: {e}")
            traceback.print_exc()
        except commands.ExtensionAlreadyLoaded as e:
            print(f"   ⚠️ JÁ ESTAVA CARREGADA: {e}")
        except commands.NoEntryPointError as e:
            print(f"   ❌ SEM FUNÇÃO setup(): {e}")
            traceback.print_exc()
        except commands.ExtensionFailed as e:
            print(f"   ❌ FALHA NA EXECUÇÃO: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"   ❌ ERRO INESPERADO: {type(e).__name__}: {e}")
            traceback.print_exc()
    else:
        print("   ⚠️ Já estava carregada")
    
    print("\n" + "="*70)
    print(f"✅ Total de extensões carregadas: {len(bot.extensions)}")
    print("="*70 + "\n")

@bot.event
async def on_ready():
    print(f"\n✅ Bot está online como {bot.user}")

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
