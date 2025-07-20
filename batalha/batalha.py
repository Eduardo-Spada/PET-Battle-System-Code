import re
from discord.ext import commands

# Memória das batalhas
batalhas_ativas = {}

class Batalha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ──▼ Função para extrair personagens -----------------------------------
    def extrair_personagens(self, texto):
        personagens = []
        padrao = r"([^,]+?)\s+(\d+)/(\d+)"
        for match in re.finditer(padrao, texto):
            nome = match.group(1).strip().lstrip(",")
            atual = int(match.group(2))
            total = int(match.group(3))
            personagens.append({
                "nome": nome,
                "atual": atual,
                "total": total,
                "desmaiado": False
            })
        return personagens
    # ──▲-------------------------------------------------------------------

    # ──▼ Comando !batalha -------------------------------------------------
    @commands.command()
    async def batalha(self, ctx, *, texto):
        canal_id = ctx.channel.id

        if canal_id in batalhas_ativas:
            await ctx.send(f"{ctx.author.mention} ⚠️ Já existe uma batalha ativa neste canal! Use `!encerrar` para finalizar.")
            return

        try:
            lados = texto.split("vs")
            if len(lados) != 2:
                await ctx.send("❌ Formato inválido! Use: `!batalha Aliados vs Inimigos`")
                return

            aliados = self.extrair_personagens(lados[0].strip())
            inimigos = self.extrair_personagens(lados[1].strip())

            if not aliados or not inimigos:
                await ctx.send("❌ Nenhum personagem ou inimigo detectado corretamente.")
                return

            todos = aliados + inimigos
            ordem = [p["nome"] for p in todos]
            primeiro = ordem[0]

            batalhas_ativas[canal_id] = {
                "aliados": aliados,
                "inimigos": inimigos,
                "turno": 1,
                "ordem": ordem,
                "quem_ta_na_vez": 0
            }

            def formatar_linha(p):
                status = f"{p['atual']}/{p['total']}"
                return f"* {p['nome']} {status}" if not p["desmaiado"] else f"* {p['nome']} {status} – Desmaiou"

            resposta = f"# Battle Start!\nTurno 1 | Rodada de {primeiro}\n\n"
            for p in aliados:
                resposta += formatar_linha(p) + "\n"
            resposta += "------------------------\n"
            for p in inimigos:
                resposta += formatar_linha(p) + "\n"

            await ctx.send(resposta)

        except Exception as e:
            print(f"❌ Erro no comando !batalha: {e}")
            await ctx.send(f"❌ Erro ao iniciar batalha.")
    # ──▲-------------------------------------------------------------------

    # ──▼ Comando !rodada --------------------------------------------------
    @commands.command()
    async def rodada(self, ctx, *, entrada):
        canal_id = ctx.channel.id

        if canal_id not in batalhas_ativas:
            await ctx.send(f"{ctx.author.mention} ❌ Nenhuma batalha ativa nesse canal.")
            return

        try:
            batalha = batalhas_ativas[canal_id]
            todos = batalha["aliados"] + batalha["inimigos"]

            ordem_viva = [p["nome"] for p in todos if not p["desmaiado"]]
            if not ordem_viva:
                await ctx.send("❌ Ninguém pode agir.")
                return

            if batalha["quem_ta_na_vez"] >= len(ordem_viva):
                batalha["quem_ta_na_vez"] = 0

            nome_na_vez = ordem_viva[batalha["quem_ta_na_vez"]]
            entrada = entrada.strip()

            if not entrada.lower().startswith(nome_na_vez.lower()):
                nome_detectado = entrada.split()[0]
                atacante_existe = any(p["nome"].lower() == nome_detectado.lower() for p in todos)
                if atacante_existe:
                    await ctx.send(f"{ctx.author.mention} ⏳ Ainda não é a vez de **{nome_detectado}**. Agora é a vez de **{nome_na_vez}**.")
                else:
                    await ctx.send(f"{ctx.author.mention} ❌ Atacante '{nome_detectado}' não está na batalha.")
                return

            padrao_simples = re.match(rf"{re.escape(nome_na_vez)}\s+\w+\s+([\w\- ]+)\s+(\d+)", entrada, re.IGNORECASE)
            padrao_narrativo = re.match(rf"{re.escape(nome_na_vez)}.*?\((\d+)\).*?([\w\- ]+)$", entrada, re.IGNORECASE)

            if padrao_simples:
                alvo_nome = padrao_simples.group(1).strip()
                dano = int(padrao_simples.group(2).strip())
            elif padrao_narrativo:
                dano = int(padrao_narrativo.group(1).strip())
                alvo_nome = padrao_narrativo.group(2).strip()
            else:
                await ctx.send(f"{ctx.author.mention} ❌ Comando inválido. Exemplos:\n• Sayori ataca Mettaur 3\n• Sayori lança um ataque flamejante no Mettaur (4)")
                return

            atacante = next((p for p in todos if p["nome"].lower() == nome_na_vez.lower()), None)
            alvo = next((p for p in todos if p["nome"].lower() == alvo_nome.lower()), None)

            if not atacante:
                await ctx.send(f"{ctx.author.mention} ❌ Atacante '{nome_na_vez}' não está na batalha.")
                return

            if atacante["desmaiado"]:
                await ctx.send(f"{ctx.author.mention} ❌ {nome_na_vez} está desmaiado e não pode agir.")
                return

            if not alvo:
                await ctx.send(f"{ctx.author.mention} ❌ Alvo '{alvo_nome}' não encontrado na batalha.")
                return

            alvo["atual"] -= dano
            if alvo["atual"] <= 0:
                alvo["atual"] = 0
                alvo["desmaiado"] = True

            batalha["quem_ta_na_vez"] += 1
            ordem_viva = [p["nome"] for p in todos if not p["desmaiado"]]
            if batalha["quem_ta_na_vez"] >= len(ordem_viva):
                batalha["turno"] += 1
                batalha["quem_ta_na_vez"] = 0

            proximo = ordem_viva[batalha["quem_ta_na_vez"]] if ordem_viva else "Fim"

            def formatar_linha(p):
                status = f"{p['atual']}/{p['total']}"
                return f"* {p['nome']} {status}" if not p["desmaiado"] else f"* {p['nome']} {status} – Desmaiou"

            if all(p["desmaiado"] for p in batalha["inimigos"]):
                await ctx.send(f"🗡️ {entrada}\n\n🏆 Vitória dos aliados!")
                del batalhas_ativas[canal_id]
                return
            elif all(p["desmaiado"] for p in batalha["aliados"]):
                await ctx.send(f"🗡️ {entrada}\n\n💀 Todos os aliados desmaiaram! Derrota!")
                del batalhas_ativas[canal_id]
                return

            resposta = (
                f"🗡️ {entrada}\n\n"
                f"# The Battle Continues!\n"
                f"Turno {batalha['turno']} | Rodada de ✨**{proximo}**✨\n\n"
            )

            for p in batalha["aliados"]:
                resposta += formatar_linha(p) + "\n"
            resposta += "------------------------\n"
            for p in batalha["inimigos"]:
                resposta += formatar_linha(p) + "\n"

            await ctx.send(resposta)

        except Exception as e:
            print(f"❌ Erro no comando !rodada: {e}")
            await ctx.send("⚠️ Algo deu errado durante a rodada.")
    # ──▲-------------------------------------------------------------------

    # ──▼ Comando !status --------------------------------------------------
    @commands.command()
    async def status(self, ctx):
        try:
            canal_id = ctx.channel.id
            if canal_id not in batalhas_ativas:
                await ctx.send("❌ Nenhuma batalha ativa neste canal no momento.")
                return

            batalha = batalhas_ativas[canal_id]
            turno = batalha["turno"]
            todos = batalha["aliados"] + batalha["inimigos"]

            ordem_viva = [p["nome"] for p in todos if not p["desmaiado"]]
            if batalha["quem_ta_na_vez"] >= len(ordem_viva):
                batalha["quem_ta_na_vez"] = 0
            atual = ordem_viva[batalha["quem_ta_na_vez"]] if ordem_viva else "Ninguém"

            def formatar(p):
                status = f"{p['atual']}/{p['total']}"
                return f"* {p['nome']} {status}" if not p["desmaiado"] else f"* {p['nome']} {status} – Desmaiou"

            resposta = (
                f"# 📋 Status da Batalha\n"
                f"Turno {turno} | Rodada de ✨**{atual}**✨\n\n"
            )

            for p in batalha["aliados"]:
                resposta += formatar(p) + "\n"
            resposta += "------------------------\n"
            for p in batalha["inimigos"]:
                resposta += formatar(p) + "\n"

            await ctx.send(resposta)
        except Exception as e:
            print(f"❌ Erro no comando !status: {e}")
            await ctx.send("⚠️ Ocorreu um erro ao tentar mostrar o status da batalha.")
    # ──▲-------------------------------------------------------------------

    # ──▼ Comando !passar --------------------------------------------------
    @commands.command()
    async def passar(self, ctx, *, nome: str = None):
        try:
            canal_id = ctx.channel.id
            if canal_id not in batalhas_ativas:
                await ctx.send("❌ Nenhuma batalha ativa para passar a vez.")
                return

            if not nome:
                await ctx.send("❌ Use: `!passar NomeDoPersonagem`.")
                return

            batalha = batalhas_ativas[canal_id]
            todos = batalha["aliados"] + batalha["inimigos"]
            ordem_viva = [p["nome"] for p in todos if not p["desmaiado"]]

            if not ordem_viva:
                await ctx.send("❌ Não há personagens vivos para continuar a batalha.")
                return

            if batalha["quem_ta_na_vez"] >= len(ordem_viva):
                batalha["quem_ta_na_vez"] = 0

            atual_nome = ordem_viva[batalha["quem_ta_na_vez"]]

            if nome.lower() != atual_nome.lower():
                await ctx.send(f"⏳ Calma aí! Agora é a vez de **{atual_nome}**, e não de **{nome}**.")
                return

            personagem = next((p for p in todos if p["nome"].lower() == nome.lower()), None)
            if personagem and personagem["desmaiado"]:
                await ctx.send(f"💤 {nome} está desmaiado e não pode passar a vez.")
                return

            batalha["quem_ta_na_vez"] += 1
            if batalha["quem_ta_na_vez"] >= len(ordem_viva):
                batalha["turno"] += 1
                batalha["quem_ta_na_vez"] = 0

            proximo = ordem_viva[batalha["quem_ta_na_vez"]]

            def formatar(p):
                status = f"{p['atual']}/{p['total']}"
                return f"* {p['nome']} {status}" if not p["desmaiado"] else f"* {p['nome']} {status} – Desmaiou"

            resposta = (
                f"🔁 **{nome}** decidiu passar a vez.\n"
                f"✨ Agora é a vez de **{proximo}**!\n\n"
                f"# 📋 Status da Batalha\n"
                f"Turno {batalha['turno']} | Rodada de ✨**{proximo}**✨\n\n"
            )

            for p in batalha["aliados"]:
                resposta += formatar(p) + "\n"
            resposta += "------------------------\n"
            for p in batalha["inimigos"]:
                resposta += formatar(p) + "\n"

            await ctx.send(resposta)

        except Exception as e:
            print(f"❌ Erro no comando !passar: {e}")
            await ctx.send("⚠️ Algo deu errado ao tentar passar a vez.")
    # ──▲-------------------------------------------------------------------

    # ──▼ Comando !encerrar ------------------------------------------------
    @commands.command()
    async def encerrar(self, ctx):
        canal_id = ctx.channel.id
        if canal_id in batalhas_ativas:
            del batalhas_ativas[canal_id]
            await ctx.send("🛑 A batalha foi encerrada manualmente.")
        else:
            await ctx.send("❌ Não há batalha ativa para encerrar.")
    # ──▲-------------------------------------------------------------------

# ──▼ Setup da extensão -----------------------------------------------------
async def setup(bot):
    await bot.add_cog(Batalha(bot))
# ──▲-----------------------------------------------------------------------
