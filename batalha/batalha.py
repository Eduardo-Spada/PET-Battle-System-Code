import discord
from discord.ext import commands
import random
import copy

batalhas_ativas = {}
batalhas_pvp = {}
navis_registrados = {}
desafios_net = {}
netbatalhas = {}

class Batalha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # REGISTRAR NAVI
    # ==========================
    @commands.command()
    async def registrarnavi(self, ctx, nome: str, corpo: int, mente: int, alma: int):

        user_id = ctx.author.id

        if user_id in navis_registrados:
            await ctx.send("âš ï¸ VocÃª jÃ¡ possui um Navi registrado! Use !editarnavi.")
            return

        if corpo < 0 or mente < 0 or alma < 0:
            await ctx.send("âŒ Atributos nÃ£o podem ser negativos.")
            return

        hp = corpo * 5

        navis_registrados[user_id] = {
            "user_id": user_id,
            "nome": nome,
            "corpo": corpo,
            "mente": mente,
            "alma": alma,
            "hp": hp,
            "hp_max": hp,
            "chips": [
                {"nome": "Cannon", "base": 10, "tipo": "fisico"},
                {"nome": "Sword", "base": 15, "tipo": "fisico"},
                {"nome": "ZapRing", "base": 12, "tipo": "tecnico"},
                {"nome": "Recover", "base": 10, "tipo": "cura"},
                {"nome": "MiniBomb", "base": 8, "tipo": "fisico"},
            ],
            "defendendo": False
        }

        await ctx.send(f"ðŸ’¾ Navi **{nome}** registrado com {hp} HP!")

    # ==========================
    # EDITAR NAVI
    # ==========================
    @commands.command()
    async def editarnavi(self, ctx, atributo: str, valor: int):

        user_id = ctx.author.id

        if user_id not in navis_registrados:
            await ctx.send("âŒ VocÃª nÃ£o possui Navi registrado.")
            return

        if atributo.lower() not in ["corpo", "mente", "alma"]:
            await ctx.send("âŒ Apenas: corpo, mente ou alma.")
            return

        navis_registrados[user_id][atributo.lower()] = valor

        if atributo.lower() == "corpo":
            novo_hp = valor * 5
            navis_registrados[user_id]["hp"] = novo_hp
            navis_registrados[user_id]["hp_max"] = novo_hp

        await ctx.send(f"ðŸ”§ {atributo} atualizado para {valor}.")

    # ==========================
    # MOSTRAR NAVI
    # ==========================
    @commands.command()
    async def meunavi(self, ctx):

        user_id = ctx.author.id

        if user_id not in navis_registrados:
            await ctx.send("âŒ VocÃª nÃ£o registrou um Navi.")
            return

        n = navis_registrados[user_id]

        await ctx.send(
            f"ðŸ“œ {n['nome']}\n"
            f"â¤ï¸ {n['hp']}/{n['hp_max']}\n"
            f"ðŸ’ª Corpo: {n['corpo']}\n"
            f"ðŸ§  Mente: {n['mente']}\n"
            f"âœ¨ Alma: {n['alma']}"
        )

    # ==========================
    # DESAFIAR
    # ==========================
    @commands.command()
    async def desafiar(self, ctx, membro: discord.Member):

        if membro.bot:
            await ctx.send("âŒ NÃ£o pode desafiar bots.")
            return

        desafios_net[membro.id] = ctx.author.id

        await ctx.send(
            f"âš”ï¸ {membro.mention} foi desafiado!\nDigite !aceitar"
        )

    # ==========================
    # ACEITAR
    # ==========================
    @commands.command()
    async def aceitar(self, ctx):

        if ctx.author.id not in desafios_net:
            await ctx.send("âŒ Sem desafios pendentes.")
            return

        desafiante_id = desafios_net.pop(ctx.author.id)
        desafiante = ctx.guild.get_member(desafiante_id)

        if not desafiante:
            await ctx.send("âŒ Desafiante nÃ£o encontrado.")
            return

        if desafiante.id not in navis_registrados or ctx.author.id not in navis_registrados:
            await ctx.send("âŒ Ambos precisam ter Navi.")
            return

        p1 = copy.deepcopy(navis_registrados[desafiante.id])
        p2 = copy.deepcopy(navis_registrados[ctx.author.id])

        netbatalhas[ctx.channel.id] = {
            "p1_id": desafiante.id,
            "p2_id": ctx.author.id,
            "p1": p1,
            "p2": p2,
            "escolhas": {}
        }

        await ctx.send(
            f"ðŸ”¥ NETBATTLE INICIADA!\n"
            f"{p1['nome']} â¤ï¸ {p1['hp']} VS {p2['nome']} â¤ï¸ {p2['hp']}\n"
            f"Use !usar 0-4"
        )

    # ==========================
    # USAR CHIP
    # ==========================
    @commands.command()
    async def usar(self, ctx, indice: int):

        if ctx.channel.id not in netbatalhas:
            await ctx.send("âŒ Nenhuma batalha ativa.")
            return

        batalha = netbatalhas[ctx.channel.id]

        batalha["escolhas"][ctx.author.id] = indice
        await ctx.send(f"âœ… {ctx.author.display_name} escolheu.")

        if len(batalha["escolhas"]) < 2:
            return

        p1 = batalha["p1"]
        p2 = batalha["p2"]

        i1 = batalha["escolhas"][batalha["p1_id"]]
        i2 = batalha["escolhas"][batalha["p2_id"]]

        chip1 = p1["chips"][i1]
        chip2 = p2["chips"][i2]

        pr1 = chip1["base"] + p1["corpo"] + random.randint(1, 6)
        pr2 = chip2["base"] + p2["corpo"] + random.randint(1, 6)

        if pr1 > pr2:
            ordem = [(p1, chip1), (p2, chip2)]
        else:
            ordem = [(p2, chip2), (p1, chip1)]

        def aplicar(atacante, defensor, chip):

            if chip["tipo"] == "cura":
                cura = chip["base"] + atacante["alma"]
                atacante["hp"] += cura
                return f"ðŸ’š {atacante['nome']} curou {cura}!"

            if chip["tipo"] == "fisico":
                dano = chip["base"] + atacante["corpo"]
            else:
                dano = chip["base"] + atacante["mente"]

            reducao = defensor["alma"] // 2
            dano_real = max(dano - reducao, 0)
            defensor["hp"] -= dano_real

            return f"ðŸ’¥ {atacante['nome']} causou {dano_real}!"

        msg1 = aplicar(ordem[0][0], ordem[1][0], ordem[0][1])
        await ctx.send(msg1)

        if ordem[1][0]["hp"] > 0:
            msg2 = aplicar(ordem[1][0], ordem[0][0], ordem[1][1])
            await ctx.send(msg2)

        await ctx.send(
            f"ðŸ“Š {p1['nome']} â¤ï¸ {p1['hp']} | {p2['nome']} â¤ï¸ {p2['hp']}"
        )

        batalha["escolhas"] = {}

        if p1["hp"] <= 0 or p2["hp"] <= 0:

            if p1["hp"] <= 0 and p2["hp"] <= 0:
                await ctx.send("ðŸ¤ Empate!")
            elif p1["hp"] <= 0:
                await ctx.send(f"ðŸ† {p2['nome']} venceu!")
            else:
                await ctx.send(f"ðŸ† {p1['nome']} venceu!")

            del netbatalhas[ctx.channel.id]


async def setup(bot):
    await bot.add_cog(Batalha(bot))
