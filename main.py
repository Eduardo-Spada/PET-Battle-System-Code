import discord
from discord.ext import commands
import os
import asyncio
import traceback
from manter_vivo import manter_vivo

print("\n" + "="*70)
print("🚀 BOT INICIANDO...")
print("="*70)

# Mantém o bot vivo (Replit)
manter_vivo()

# ==============================
# ⚙️ CONFIGURAÇÕES PERSONALIZÁVEIS
# ==============================

# Mensagem enviada pelo comando !v
MENSAGEM_V = "$wa"

# Emoji usado pelo comando !m
EMOJI_REACAO = "🔥"


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
    print("\n" + "="*70)
    print("📦 CARREGANDO EXTENSÕES...")
    print("="*70 + "\n")

    extensoes = [
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
        "Mercado.trader",
    ]

    for extensao in extensoes:
        if extensao not in bot.extensions:
            try:
                print(f"⏳ Carregando {extensao}...")
                await bot.load_extension(extensao)
                print(f"✅ {extensao} carregado com sucesso!")

            except commands.ExtensionNotFound:
                print(f"❌ NÃO ENCONTRADA: {extensao}")
                traceback.print_exc()

            except commands.NoEntryPointError:
                print(f"❌ {extensao} não tem função setup()")
                traceback.print_exc()

            except commands.ExtensionFailed:
                print(f"❌ ERRO dentro da extensão {extensao}:")
                traceback.print_exc()

            except Exception as e:
                print(f"❌ ERRO inesperado em {extensao}: {e}")
                traceback.print_exc()

        else:
            print(f"⚠️ {extensao} já estava carregada")

    print("\n" + "="*70)
    print(f"✅ Total de extensões carregadas: {len(bot.extensions)}")
    print("="*70 + "\n")


# ──▼ Bot online ───────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"\n✅ Bot está online como {bot.user}")


# ──▼ Mensagens / menções ──────────────────────────────────────────────
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.reference:
        try:
            msg_ref = await message.channel.fetch_message(
                message.reference.message_id
            )

            if msg_ref.author == bot.user:
                await bot.process_commands(message)
                return

        except Exception:
            pass

    if bot.user in message.mentions:
        await message.channel.send(
            f"👋 Oi {message.author.mention}! "
            "Se precisar de ajuda, use **!sos**."
        )

    await bot.process_commands(message)


# ──▼ Comando !oi ──────────────────────────────────────────────────────
@bot.command()
async def oi(ctx):
    await ctx.send(
        f"Fala {ctx.author.mention}! Eu tô vivo aqui no servidor!"
    )


# ──▼ Comando !v ───────────────────────────────────────────────────────
@bot.command()
async def v(ctx):
    await ctx.send(MENSAGEM_V)


# ──▼ Comando !m ───────────────────────────────────────────────────────
@bot.command()
async def m(ctx):
    # Verifica se o comando foi usado como resposta a uma mensagem
    if ctx.message.reference is None:
        await ctx.send(
            "❌ Responda à mensagem desejada com `!m` para eu reagir com 🔥."
        )
        return

    try:
        # Busca a mensagem original
        mensagem_original = await ctx.channel.fetch_message(
            ctx.message.reference.message_id
        )

        # Adiciona a reação de fogo
        await mensagem_original.add_reaction(EMOJI_REACAO)

    except discord.NotFound:
        await ctx.send("❌ Não consegui encontrar a mensagem original.")

    except discord.Forbidden:
        await ctx.send(
            "❌ Não tenho permissão para adicionar reações nesse canal."
        )

    except discord.HTTPException as e:
        print(f"❌ Erro ao adicionar reação: {e}")
        await ctx.send("⚠️ Não consegui adicionar a reação.")


# ──▼ Start ────────────────────────────────────────────────────────────
async def main():
    async with bot:
        await setup_extensoes()

        try:
            await bot.start(os.environ["TOKEN"])

        except KeyError:
            print(
                "❌ TOKEN não encontrado! "
                "Configure 'TOKEN' nas variáveis de ambiente."
            )

        except Exception as e:
            print(f"❌ Erro ao iniciar o bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())
