from pathlib import Path
from game.termo import GameState, load_words
from metrics.evaluator import Evaluator
from engines.minimax_engine import MinimaxEngine

def main() -> None:
    print("Iniciando...\n")

    dataset_path = Path(__file__).resolve().parent / "dataset" / "words.txt"
    vocabulary = load_words(dataset_path)

    print(f"Vocabulário carregado com sucesso: {len(vocabulary)} palavras.")

    engine = MinimaxEngine()
    evaluator = Evaluator(engine=engine, vocabulary=vocabulary, num_games=50)

    print(f"Avaliando motor [{engine.__class__.__name__}] em {evaluator._num_games} partidas...\n")

    results = evaluator.run()

    print("------------------------------")
    print("      RESULTADOS FINAIS      ")
    print("------------------------------")
    print(f"Partidas Jogadas : {results['num_games']}")
    print(f"Taxa de Vitória  : {results['win_rate']:.2f}%")
    print(f"Média Tentativas : {results['avg_attempts']} (apenas nas vitórias)")
    print(f"Tempo Total      : {results['time_seconds']} segundos")
    print("-" * 30)

if __name__ == "__main__":
    main()