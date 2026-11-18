import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import LIMITE_MEDIA, nivel_confianca

PASTA_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CAMPOS_CSV = ["data", "origem", "pergunta", "id_orientacao", "encontrou",
              "ajudou", "tentativas", "tempo_segundos"]


def ler_numero(texto, minimo, maximo):
    """Pede um número de minimo a maximo. Entrada inválida nunca encerra o programa."""
    while True:
        resposta = input(texto).strip()
        if resposta.isdecimal() and minimo <= int(resposta) <= maximo:
            return int(resposta)
        print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")


def contem_dado_pessoal(texto):
    """8 ou mais dígitos (CPF, telefone...) ou um @ (e-mail)."""
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto


def media(valores):
    numeros = [v for v in valores if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return round(sum(numeros) / len(numeros), 1) if numeros else None


def porcentagem(parte, total):
    return round(100 * parte / total, 1) if total else None


class Assistente:
    """Quem conversa com o cidadão: atende, guarda o histórico e calcula indicadores."""

    def __init__(self, nome, base, caminho_historico=None, caminho_csv=None):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico or os.path.join(PASTA_DATA, "historico.json")
        self.caminho_csv = caminho_csv or os.path.join(PASTA_DATA, "atendimentos.csv")
        self.historico = self.carregar_historico()
        self.atendimentos_na_sessao = 0

    # ---------- histórico ----------
    def carregar_historico(self):
        try:
            with open(self.caminho_historico, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list):
                raise ValueError("formato inesperado")
            return [registro for registro in dados if isinstance(registro, dict)]
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, ValueError, OSError):
            print("Aviso: histórico ilegível. Uma cópia foi guardada e um novo será criado.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass
            return []

    def salvar_historico(self):
        try:
            os.makedirs(os.path.dirname(self.caminho_historico), exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        self.historico.append({
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
        })
        self.atendimentos_na_sessao += 1
        self.salvar_historico()

    def pedir_nota(self):
        """Ao sair, pede a nota de facilidade de 1 a 5 (só se houve atendimento)."""
        if self.atendimentos_na_sessao == 0:
            return
        nota = ler_numero("De 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
        self.historico.append({
            "data": datetime.now().isoformat(timespec="seconds"),
            "origem": "nota",
            "nota_facilidade": nota,
        })
        self.salvar_historico()

    # ---------- atendimento por pergunta ----------
    def perguntar_sim_nao(self, texto):
        while True:
            resposta = input(texto).strip().lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Digite apenas s ou n.")

    def perguntar(self):
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        while True:
            texto = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                break
            if texto == "":
                print("Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if contem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)
            if not resultados or resultados[0][0] < LIMITE_MEDIA:
                print("Não encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras ou navegue pelas categorias (opção 2 do menu):")
                for categoria in self.base.categorias():
                    print(f"  - {categoria}")
                continue

            pontos, melhor = resultados[0]
            print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
            melhor.exibir()
            alternativas = [o for p, o in resultados[1:3] if p >= LIMITE_MEDIA]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for orientacao in alternativas:
                    print(f"  - {orientacao.titulo}")

            ajudou = self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", texto, melhor.id, True, ajudou, tentativas, tempo)
            return

        if tentativas > 0:  # desistiu sem encontrar: vira "dúvida sem solução"
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", ultima_pergunta, None, False, False, tentativas, tempo)

    # ---------- navegação por categorias ----------
    def navegar(self):
        categorias = self.base.categorias()
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, 1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            escolha = ler_numero("Escolha uma categoria: ", 0, len(categorias))
            if escolha == 0:
                return
            self.escolher_orientacao(categorias[escolha - 1])

    def escolher_orientacao(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        inicio = time.time()
        while True:
            print(f"\n{categoria}:")
            for numero, orientacao in enumerate(orientacoes, 1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")
            escolha = ler_numero("Escolha uma orientação: ", 0, len(orientacoes))
            if escolha == 0:
                return
            orientacao = orientacoes[escolha - 1]
            orientacao.exibir()
            ajudou = self.perguntar_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", orientacao.titulo, orientacao.id, True, ajudou, 1, tempo)
            inicio = time.time()

    # ---------- indicadores e CSV ----------
    def atendimentos(self):
        return [r for r in self.historico if r.get("origem") in ("pergunta", "categoria")]

    def indicadores(self):
        atendimentos = self.atendimentos()
        total = len(atendimentos)
        encontrados = [r for r in atendimentos if r.get("encontrou")]
        ajudaram = [r for r in atendimentos if r.get("ajudou")]
        notas = [r.get("nota_facilidade") for r in self.historico if r.get("origem") == "nota"]
        sem_solucao = sorted({r["pergunta"] for r in atendimentos
                              if not r.get("ajudou") and isinstance(r.get("pergunta"), str)
                              and r["pergunta"]})
        return {
            "atendimentos": total,
            "resposta_encontrada_pct": porcentagem(len(encontrados), total),
            "taxa_acerto_pct": porcentagem(len(ajudaram), total),
            "tempo_medio_s": media([r.get("tempo_segundos") for r in encontrados]),
            "tentativas_por_atendimento": media([r.get("tentativas") for r in atendimentos]),
            "facilidade_media": media(notas),
            "duvidas_sem_solucao": sem_solucao,
        }

    def mostrar_indicadores(self):
        dados = self.indicadores()
        if dados["atendimentos"] == 0:
            print("\nAinda não há atendimentos registrados.")
            return

        def formatar(valor, sufixo=""):
            return "sem dados" if valor is None else f"{valor}{sufixo}"

        print("\n=== Indicadores ===")
        print(f"Atendimentos registrados:       {dados['atendimentos']}")
        print(f"Resposta encontrada:            {formatar(dados['resposta_encontrada_pct'], '%')}")
        print(f"Taxa de acerto (ajudou):        {formatar(dados['taxa_acerto_pct'], '%')}")
        print(f"Tempo médio para encontrar:     {formatar(dados['tempo_medio_s'], ' s')}")
        print(f"Tentativas por atendimento:     {formatar(dados['tentativas_por_atendimento'])}")
        print(f"Facilidade de uso (1 a 5):      {formatar(dados['facilidade_media'])}")
        print("Dúvidas sem solução:")
        if dados["duvidas_sem_solucao"]:
            for duvida in dados["duvidas_sem_solucao"]:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")

    def exportar_csv(self):
        atendimentos = self.atendimentos()
        try:
            os.makedirs(os.path.dirname(self.caminho_csv), exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(atendimentos)
            print(f"{len(atendimentos)} atendimentos exportados para {self.caminho_csv}")
        except OSError:
            print("Não foi possível exportar o CSV.")
