import os

from assistente import Assistente, PASTA_DATA, ler_numero
from base_conhecimento import BaseConhecimento
from orientacao import AVISO


def menu(assistente):
    """Menu principal. Só termina quando o usuário escolhe 0."""
    while True:
        print("\n=== Citizen Assist AI ===")
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores")
        print("4. Exportar atendimentos para CSV")
        print("0. Sair")
        opcao = ler_numero("Escolha uma opção: ", 0, 4)

        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.mostrar_indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        else:
            assistente.pedir_nota()
            print("Até logo!")
            return


def main():
    caminho_base = os.path.join(PASTA_DATA, "base_conhecimento.json")
    base = BaseConhecimento(caminho_base)
    if not base.carregar():
        print("Não foi possível carregar a base de conhecimento. Encerrando.")
        return

    assistente = Assistente("Citizen Assist AI", base)
    print(AVISO)
    try:
        menu(assistente)
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")


if __name__ == "__main__":
    main()
