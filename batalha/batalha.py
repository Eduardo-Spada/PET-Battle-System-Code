import discord
from discord.ext import commands
import random

batalhas_ativas = {}

batalhas_pvp = {}        # batalhas ativas por canal
navis_registrados = {}   # ficha permanente dos jogadores

# ðŸ”¥ Sistema NetBattle automÃ¡tico
desafios_net = {}       # {desafiado_id: desafiante_id}
netbatalhas = {}        # {canal_id: dados}


class Batalha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========== Comandos de registrar, editar e mostrar navis ==========

    @commands.command()
async def registrarnavi(self, ctx, nome: str, corpo: int, mente: int, alma: int):
    user_id = ctx.author.id

    if user_id in navis_registrados:
        await ctx.send("âš ï¸ VocÃª jÃ¡ possui um Navi registrado! Use !editarnavi para alterar.")
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
        "chips": [],
        "defendendo": False
    }

    await ctx.send(
        f"ðŸ’¾ Navi **{nome}** registrado com sucesso!\n"
        f"â¤ï¸ HP: {hp}\n"
        f"ðŸ’ª Corpo: {corpo} | ðŸ§  Mente: {mente} | âœ¨ Alma: {alma}"
    )

    @commands.command()
async def editarnavi(self, ctx, atributo: str, valor: int):
    user_id = ctx.author.id

    if user_id not in navis_registrados:
        await ctx.send("âŒ VocÃª nÃ£o possui um Navi registrado.")
        return

    if atributo.lower() not in ["corpo", "mente", "alma"]:
        await ctx.send("âŒ VocÃª sÃ³ pode editar: corpo, mente ou alma.")
        return

    if valor < 0:
        await ctx.send("âŒ Valor invÃ¡lido.")
        return

    navis_registrados[user_id][atributo.lower()] = valor

    # Atualiza HP se corpo mudar
    if atributo.lower() == "corpo":
        novo_hp = valor * 5
        navis_registrados[user_id]["hp_max"] = novo_hp
        navis_registrados[user_id]["hp"] = novo_hp

    await ctx.send(
        f"ðŸ”§ {atributo.capitalize()} atualizado para {valor} com sucesso!"
    )

    @commands.command()
async def meunavi(self, ctx):
    user_id = ctx.author.id

    if user_id not in navis_registrados:
        await ctx.send("âŒ VocÃª ainda nÃ£o registrou um Navi.")
        return

    navi = navis_registrados[user_id]

    await ctx.send(
        f"ðŸ“œ **{navi['nome']}**\n"
        f"â¤ï¸ HP: {navi['hp']}/{navi['hp_max']}\n"
        f"ðŸ’ª Corpo: {navi['corpo']}\n"
        f"ðŸ§  Mente: {navi['mente']}\n"
        f"âœ¨ Alma: {navi['alma']}"
    )

    # =========================================
    # âš”ï¸ DESAFIAR
    # =========================================
    @commands.command()
    async def desafiar(self, ctx, membro: discord.Member):

        if membro.bot:
            await ctx.send("âŒ VocÃª nÃ£o pode desafiar bots.")
            return

        if membro.id in desafios_net:
            await ctx.send("âš ï¸ Esse jogador jÃ¡ possui um desafio pendente.")
            return

        desafios_net[membro.id] = ctx.author.id

        await ctx.send(
            f"âš”ï¸ {membro.mention}, vocÃª foi desafiado por {ctx.author.mention}!\n"
            f"Digite **!aceitar** para iniciar a NetBattle."
        )

    # =========================================
# ðŸ”¥ ACEITAR
# =========================================
@commands.command()
async def aceitar(self, ctx):

    if ctx.author.id not in desafios_net:
        await ctx.send("âŒ VocÃª nÃ£o tem desafios pendentes.")
        return

    desafiante_id = desafios_net.pop(ctx.author.id)
    desafiante = ctx.guild.get_member(desafiante_id)

    if not desafiante:
        await ctx.send("âŒ O desafiante nÃ£o estÃ¡ mais no servidor.")
        return

    # ðŸ”Ž Verifica se ambos possuem Navi registrado
    if desafiante.id not in navis_registrados:
        await ctx.send(f"âŒ {desafiante.display_name} nÃ£o possui Navi registrado.")
        return

    if ctx.author.id not in navis_registrados:
        await ctx.send("âŒ VocÃª nÃ£o possui Navi registrado.")
        return

    # ðŸ§¬ Copia os dados do Navi (para nÃ£o alterar o original)
    import copy
    p1 = copy.deepcopy(navis_registrados[desafiante.id])
    p2 = copy.deepcopy(navis_registrados[ctx.author.id])

    # Garante HP cheio ao iniciar batalha
    p1["hp"] = p1["corpo"] * 5
    p2["hp"] = p2["corpo"] * 5

    netbatalhas[ctx.channel.id] = {
        "p1_id": desafiante.id,
        "p2_id": ctx.author.id,
        "p1": p1,
        "p2": p2,
        "escolhas": {}
    }

    await ctx.send(
        f"ðŸ”¥ **NETBATTLE INICIADA!** ðŸ”¥\n"
        f"{p1['nome']} â¤ï¸ {p1['hp']} VS "
        f"{p2['nome']} â¤ï¸ {p2['hp']}\n\n"
        f"Escolham um chip com **!usar 0-4**"
    )
    
    # =========================================
    # ðŸŽ´ USAR CHIP
    # =========================================
    @commands.command()
    async def usar(self, ctx, indice: int):

        if ctx.channel.id not in netbatalhas:
            await ctx.send("âŒ NÃ£o hÃ¡ NetBattle ativa neste canal.")
            return

        if indice < 0 or indice > 4:
            await ctx.send("âŒ Escolha um nÃºmero entre 0 e 4.")
            return

        batalha = netbatalhas[ctx.channel.id]

        if ctx.author.id not in [batalha["p1_id"], batalha["p2_id"]]:
            return

        batalha["escolhas"][ctx.author.id] = indice
        await ctx.send(f"âœ… {ctx.author.display_name} escolheu seu chip.")

        if len(batalha["escolhas"]) == 2:

            p1 = batalha["p1"]
            p2 = batalha["p2"]

            i1 = batalha["escolhas"][batalha["p1_id"]]
            i2 = batalha["escolhas"][batalha["p2_id"]]

            chip1 = p1["chips"][i1]
            chip2 = p2["chips"][i2]

            # ðŸŽ° Prioridade
            pr1 = chip1["base"] + p1["corpo"] + random.randint(1, 6)
            pr2 = chip2["base"] + p2["corpo"] + random.randint(1, 6)

            if pr1 > pr2:
                ordem = [(p1, chip1), (p2, chip2)]
            else:
                ordem = [(p2, chip2), (p1, chip1)]

            mensagens = []

            def aplicar(atacante, defensor, chip):

                if chip["tipo"] == "fisico":
                    dano = chip["base"] + atacante["corpo"]
                elif chip["tipo"] == "tecnico":
                    dano = chip["base"] + atacante["mente"]
                else:
                    cura = chip["base"] + atacante["alma"]
                    atacante["hp"] += cura
                    return f"ðŸ’š {atacante['nome']} curou {cura} HP!"

                reducao = defensor["alma"] // 2
                dano_real = max(dano - reducao, 0)
                defensor["hp"] -= dano_real

                return f"ðŸ’¥ {atacante['nome']} usou {chip['nome']} e causou {dano_real} de dano!"

            mensagens.append(aplicar(ordem[0][0], ordem[1][0], ordem[0][1]))

            if ordem[1][0]["hp"] > 0:
                mensagens.append(aplicar(ordem[1][0], ordem[0][0], ordem[1][1]))

            batalha["escolhas"] = {}

            for m in mensagens:
                await ctx.send(m)

            await ctx.send(
                f"ðŸ“Š HP {p1['nome']}: {p1['hp']} | HP {p2['nome']}: {p2['hp']}"
            )

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
