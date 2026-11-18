import json

from orientacao import Orientacao

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Pontuação (regra da seção 6.2 da atividade)
PONTOS_PALAVRA_CHAVE = 3
PONTOS_PALAVRA_TITULO = 1
LIMITE_MEDIA = 3
LIMITE_ALTA = 6

# Palavras comuns que não contam como "palavra do título" (ajuste explicado no README)
IGNORAR_NO_TITULO = {"para", "como", "onde", "quando", "sobre", "outras", "saude",
                     "atendimento", "unidade", "unidades", "fazer", "preciso", "quero"}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação, com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return None


class BaseConhecimento:
    """O conjunto de todas as orientações (lista de objetos Orientacao)."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Devolve False se não for possível."""
        self.orientacoes = []
        try:
            with open(self.caminho, encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {self.caminho}")
            return False
        except (json.JSONDecodeError, OSError):
            print(f"Arquivo ilegível ou corrompido: {self.caminho}")
            return False

        if not isinstance(dados, list):
            print("A base de conhecimento deve ser uma lista de orientações.")
            return False

        for registro in dados:
            try:
                if any(campo not in registro for campo in CAMPOS):
                    raise KeyError("campo ausente")
                if not isinstance(registro["palavras_chave"], list) \
                        or not isinstance(registro["documentos"], list):
                    raise TypeError("lista esperada")
                self.orientacoes.append(Orientacao(*[registro[c] for c in CAMPOS]))
            except (KeyError, TypeError):
                print("Aviso: um registro inválido da base foi ignorado.")
        return len(self.orientacoes) > 0

    def categorias(self):
        """Categorias na ordem em que aparecem na base, sem repetir."""
        categorias = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in categorias:
                categorias.append(orientacao.categoria)
        return categorias

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta_normalizada, orientacao):
        """+3 por palavra-chave na pergunta; +1 por palavra da pergunta (4+ letras) no título."""
        pontos = 0
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_normalizada:
                pontos += PONTOS_PALAVRA_CHAVE

        palavras_do_titulo = normalizar(orientacao.titulo).split()
        for palavra in set(pergunta_normalizada.split()):
            if len(palavra) >= 4 and palavra not in IGNORAR_NO_TITULO \
                    and palavra in palavras_do_titulo:
                pontos += PONTOS_PALAVRA_TITULO
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação.

        Em empate, vale a ordem da base (as orientações de urgência vêm primeiro)."""
        pergunta_normalizada = normalizar(pergunta)
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta_normalizada, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: -tupla[0])  # sort é estável: empate mantém a ordem
        return resultados
