from pathlib import Path

from engines.dpll_solver.dpll_solver_engine import LogicEngine
from engines.minimax.minimax_engine import MinimaxEngine
from game.cli import run_cli
from game.termo import load_words
from metrics.evaluator import Evaluator


def run_evaluation() -> None:
    print("Iniciando...\n")

    dataset_path = Path(__file__).resolve().parent / "dataset" / "words.txt"
    vocabulary = load_words(dataset_path)
    num_games = 50

    print(f"Vocabulário carregado com sucesso: {len(vocabulary)} palavras.")

    for engine in (MinimaxEngine(), LogicEngine()):
        name = engine.__class__.__name__
        print(f"\nAvaliando motor [{name}] em {num_games} partidas...\n")

        try:
            evaluator = Evaluator(
                engine=engine,
                vocabulary=vocabulary,
                num_games=num_games,
            )
            results = evaluator.run()
        # A falha de um motor não deve impedir a avaliação dos demais.
        except Exception as error:
            print(f"Erro ao avaliar motor [{name}]: {error}")
            continue

        print("------------------------------")
        print("      RESULTADOS FINAIS      ")
        print("------------------------------")
        print(f"Partidas Jogadas : {results['num_games']}")
        print(f"Taxa de Vitória  : {results['win_rate']:.2f}%")
        print(f"Média Tentativas : {results['avg_attempts']} (apenas nas vitórias)")
        print(f"Tempo Total      : {results['time_seconds']} segundos")
        print("-" * 30)


if __name__ == "__main__":
    run_cli(evaluation_function=run_evaluation)
