from pathlib import Path

from engines.bayes.bayes_engine import NaiveBayesEngine
from engines.logic.dpll.dpll_engine import DpllEngine
from engines.logic.model_checking.model_checking_engine import ModelCheckingEngine
from engines.minimax.minimax_engine import MinimaxEngine
from game.cli import run_cli
from game.termo import load_words
from metrics.evaluator import Evaluator


def run_evaluation() -> None:
    print("Iniciando avaliação dos motores...\n")

    dataset_path = Path(__file__).resolve().parent / "dataset" / "words.txt"
    vocabulary = load_words(dataset_path)
    num_games = 50

    print(f"Dataset carregado com sucesso: {len(vocabulary)} palavras.")

    engines_to_evaluate = (NaiveBayesEngine(), MinimaxEngine(), DpllEngine())

    for engine in engines_to_evaluate:
        name = engine.__class__.__name__
        print(f"\nAvaliando motor [{name}] em {num_games} partidas...\n")

        try:
            evaluator = Evaluator(
                engine=engine,
                vocabulary=vocabulary,
                num_games=num_games,
            )
            results = evaluator.run()

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
