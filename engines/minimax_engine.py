from collections import defaultdict
from game.termo import GameState
from game.feedback import evaluate_guess, LetterFeedback

class MinimaxEngine:
    def __init__(self):
        self._possible_answers: list[str] = []

    def _is_valid_candidate(self, candidate: str, guess: str, feedback: tuple[LetterFeedback, ...]) -> bool:
        return evaluate_guess(candidate, guess) == feedback

    def _min_value(self, guess: str, candidates: list[str], current_best: float) -> float:
        buckets = defaultdict(int)
        for answer in candidates:
            feedback = evaluate_guess(answer, guess)
            buckets[feedback] += 1

            # Poda
            if buckets[feedback] > current_best:
                return float('inf')

        return max(buckets.values())

    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        # Estado inicial
        if not state.history:
            if not vocabulary:
                raise ValueError("vocabulário não deve estar vazio")
            self._possible_answers = list(vocabulary)
            rreturn "ROSEA" if "ROSEA" in vocabulary else vocabulary[0]

        # Atualização
        self._possible_answers = [
            word for word in vocabulary
            if all(self._is_valid_candidate(word, result.guess, result.feedback) for result in state.history)
        ]

        if len(self._possible_answers) == 1:
            return self._possible_answers[0]

        # Busca competitiva com poda
        best_guess = ""
        best_value = float('inf')

        # Avalia todas as palavras
        for guess in vocabulary:
            value = self._min_value(guess, self._possible_answers, best_value)

            if value < best_value:
                best_value = value
                best_guess = guess
            # Se duas forem boas, priorize a vitória
            elif value != float('inf') and value == best_value and guess in self._possible_answers:
                best_guess = guess

        return best_guess