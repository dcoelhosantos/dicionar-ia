import time
from typing import Any, Protocol
from game.termo import GameState, TermoGame

class TermoEngine(Protocol):
    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        ...

class Evaluator:
    def __init__(self, engine: TermoEngine, vocabulary: tuple[str, ...], num_games: int = 100):
        self._engine = engine
        self._vocabulary = vocabulary
        self._num_games = num_games

    def run(self) -> dict[str, Any]:
        wins = 0
        total_attempts = 0
        start_time = time.time()

        import random

        for _ in range(self._num_games):
            game = TermoGame()

            game._answer = random.choice(self._vocabulary)

            while not game.state.over:
                guess = self._engine.make_guess(game.state, self._vocabulary)
                game.make_guess(guess)

            if game.state.won:
                wins += 1
                total_attempts += len(game.state.history)

        end_time = time.time()
        win_rate = (wins / self._num_games) * 100

        avg_attempts = total_attempts / wins if wins > 0 else 0.0

        return {
            "num_games": self._num_games,
            "win_rate": win_rate,
            "avg_attempts": round(avg_attempts, 2),
            "time_seconds": round(end_time - start_time, 3)
        }