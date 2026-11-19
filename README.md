# Citizen Assist AI

Assistente de terminal, em Python, que orienta pessoas que usam o SUS na cidade de São Paulo. Responde dúvidas em texto livre com base em uma base de conhecimento verificada, mostra a fonte e a data de conferência, e não coleta dados pessoais.

## Integrantes

| Nome | RM |
|---|---|
| Gustavo Melo dos Santos | RM573562 |
| João Pedro Costenari Silva | RM572260 |
| João Victor Canello Ferian | RM573295 |

## Público e problema

**Público:** pessoas que dependem do SUS e têm dificuldade para saber a quem recorrer, em que situação e o que levar.

**Problema:** a informação existe, mas está espalhada em páginas diferentes e em linguagem técnica. O assistente responde, em linguagem simples, perguntas como "onde tomo vacina?", "quando ligo para o 192?" e "como encontro um remédio na rede municipal?".

## ODS relacionados

- **ODS 3:** Saúde e Bem-Estar.
- **ODS 10:** Redução das Desigualdades (acesso à informação para quem usa o sistema público).

## Como executar

Requisitos: Python 3.8 ou superior. Não são necessárias bibliotecas externas.

```bash
python main.py
```

Estrutura:

```text
citizen-assist-ai/
├── README.md
├── main.py
├── orientacao.py
├── base_conhecimento.py
├── assistente.py
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Carrega a base, cria o assistente e mostra o menu principal. |
| `orientacao.py` | Classe `Orientacao`: guarda uma orientação e a exibe na tela. |
| `base_conhecimento.py` | Classe `BaseConhecimento`: lê o JSON, lista categorias, pontua e busca. |
| `assistente.py` | Classe `Assistente`: atende, guarda o histórico, calcula indicadores e exporta o CSV. |

As classes se encaixam por composição: `Assistente` tem uma `BaseConhecimento`, que tem uma lista de objetos `Orientacao`.

## Menu

1. Fazer uma pergunta em texto livre.
2. Navegar por categorias (com "0 para voltar" em todas as telas).
3. Ver indicadores.
4. Exportar atendimentos para CSV.
0. Sair (pede uma nota de facilidade de 1 a 5).

## Regra de pontuação

A pergunta e as palavras-chave são normalizadas (minúsculas, sem acentos e sem pontuação). Cada orientação recebe pontos:

| Regra | Pontos |
|---|---|
| Palavra-chave da orientação aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) aparece no título | +1 |

| Melhor pontuação | Resultado |
|---|---|
| 6 ou mais | Confiança ALTA |
| 3 a 5 | Confiança MÉDIA |
| Menos de 3 | "Não encontrei" e sugestão de categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. Em caso de empate, vale a ordem da base. O assistente mostra a melhor orientação e até duas alternativas.

**Ajuste feito:** palavras comuns como "para", "como", "onde", "saude", "atendimento" e "unidade" não contam como palavras do título (`IGNORAR_NO_TITULO`), porque aparecem em quase todas as perguntas e distorcem a pontuação.

## Base de conhecimento

`data/base_conhecimento.json`: 10 orientações em 5 categorias (Urgência e emergência, Atenção básica, Documentos e aplicativos, Saúde mental, Medicamentos). Todas têm pelo menos 4 palavras-chave, fonte oficial e data de verificação.

## Segurança e transparência

- Perguntas com 8 ou mais dígitos, ou com `@`, são recusadas e não são registradas.
- Toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- Entradas inválidas (opção fora da faixa, letras, resposta vazia, s/n inválido) nunca encerram o programa.
- Base ausente ou corrompida não trava o programa. Histórico corrompido é preservado como `historico.json.corrompido` e um novo é criado.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` (data, origem, pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo). Indicadores calculados: resposta encontrada (%), taxa de acerto (%), tempo médio, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução. A exportação gera `data/atendimentos.csv`.

## Fontes consultadas

- Ministério da Saúde: [SAMU 192](https://www.gov.br/saude/pt-br/composicao/saes/samu-192)
- Ministério da Saúde: [Novo Cartão Nacional de Saúde com CPF](https://www.gov.br/saude/pt-br/assuntos/noticias/2025/setembro/novo-cartao-nacional-de-saude-com-cpf-como-funciona-na-pratica)
- Ministério da Saúde: [O que é o Meu SUS Digital](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/1-o-que-e-o)
- Prefeitura de São Paulo: [Unidades de Pronto Atendimento (UPA)](https://prefeitura.sp.gov.br/web/saude/w/unidades-pronto-atendimento-upa)
- Prefeitura de São Paulo: [Unidades Básicas de Saúde (UBS)](https://prefeitura.sp.gov.br/web/saude/w/unidades-basicas-de-saude-ubs)
- Prefeitura de São Paulo: [Postos de Vacinação](https://prefeitura.sp.gov.br/web/saude/w/vigilancia_em_saude/vacinacao/360678)
- Prefeitura de São Paulo: [Urgências Odontológicas](https://prefeitura.sp.gov.br/web/saude/w/atencao_basica/344440)
- Prefeitura de São Paulo: [UBS: saiba quando procurar](https://www2.prefeitura.sp.gov.br/web/saude/w/ubs-saiba-quando-procurar-este-servi%C3%A7o-na-rede-municipal-5)
- Prefeitura de São Paulo: [Centros de Atenção Psicossocial (CAPS)](https://prefeitura.sp.gov.br/web/saude/w/saude_mental_ad/caps)
- Prefeitura de São Paulo: [Remédio na Hora](https://prefeitura.sp.gov.br/web/saude/w/atencao_basica/207663)

## Teste com usuários

| Indicador | Resultado |
|---|---|
| Atendimentos registrados | 23 |
| Resposta encontrada (%) | 82.6% |
| Taxa de acerto (%) | 82.6% |
| Tempo médio para encontrar | 48.7 s |
| Tentativas por atendimento | 1.0 |
| Facilidade de uso (1 a 5) | 5.0 |

**Dúvidas sem solução:** 
- como tiro meu passaporte?
- preciso tirar meu passaporte

## Limitações

- A base tem 10 orientações e reflete o município de São Paulo. Outras cidades têm regras e serviços diferentes.
- A busca é por palavras-chave. Erros de digitação e sinônimos que não estejam cadastrados não são reconhecidos.
- O assistente não faz diagnóstico, não indica unidades específicas e não verifica disponibilidade de vaga, vacina ou medicamento.
- As orientações podem mudar. Confirme sempre na unidade ou no site oficial.

## Vídeo técnico

Link: https://youtu.be/V2k5JVkw3IU
