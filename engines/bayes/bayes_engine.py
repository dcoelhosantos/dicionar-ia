from collections import Counter
import math

from game.feedback import WORD_LENGTH, evaluate_guess
from game.termo import GameState

ALPHABET_SIZE = 26


class NaiveBayesEngine:
    def __init__(self, alpha: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("alpha deve ser maior que zero")

        self._alpha = alpha
        self._possible_answers: list[str] = []

    def _position_counts(
        self,
        vocabulary: tuple[str, ...],
    ) -> tuple[Counter[str], ...]:
        counts = tuple(Counter() for _ in range(WORD_LENGTH))

        for word in vocabulary:
            for index, letter in enumerate(word):
                counts[index][letter] += 1

        return counts

    def _log_probability(
        self,
        word: str,
        position_counts: tuple[Counter[str], ...],
        vocabulary_size: int,
    ) -> float:
        denominator = vocabulary_size + self._alpha * ALPHABET_SIZE

        return sum(
            math.log((position_counts[index][letter] + self._alpha) / denominator)
            for index, letter in enumerate(word)
        )

    def _matches_history(self, candidate: str, state: GameState) -> bool:
        return all(
            evaluate_guess(candidate, result.guess) == result.feedback
            for result in state.history
        )

    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        if not vocabulary:
            raise ValueError("vocabulário não deve estar vazio")

        position_counts = self._position_counts(vocabulary)
        candidates = [
            word for word in vocabulary if self._matches_history(word, state)
        ]

        if not candidates:
            self._possible_answers = []
            raise ValueError(
                "Nenhum candidato restante no vocabulário para este histórico."
            )

        self._possible_answers = sorted(
            candidates,
            key=lambda word: self._log_probability(
                word,
                position_counts,
                len(vocabulary),
            ),
            reverse=True,
        )
        return self._possible_answers[0]