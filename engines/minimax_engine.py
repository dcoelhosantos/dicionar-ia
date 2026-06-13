from collections import defaultdict
from game.termo import GameState
from game.feedback import evaluate_guess, LetterFeedback

class MinimaxEngine:
    def __init__(self):
        self._possible_answers: list[str] = []

    def _is_valid_candidate(self, candidate: str, guess: str, feedback: tuple[LetterFeedback, ...]) -> bool:
        return evaluate_guess(candidate, guess) == feedback

    def _min_value(self, guess: str, candidates: list[str]) -> int:
        buckets = defaultdict(int)
        for answer in candidates:
            feedback = evaluate_guess(answer, guess)
            buckets[feedback] += 1

        return max(buckets.values())

    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        #ESTADO INICIAL
        if not state.history:
            self._possible_answers = list(vocabulary)
            return "SAROE"

        #ATUALIZAÇÃO
        last_result = state.history[-1]
        self._possible_answers = [
            word for word in self._possible_answers
            if self._is_valid_candidate(word, last_result.guess, last_result.feedback)
        ]

        if len(self._possible_answers) == 1:
            return self._possible_answers[0]

        #BUSCA COMPETITIVA
        best_guess = ""
        best_value = float('inf')

        #AVALIA TODAS AS PALAVRAS
        for guess in vocabulary:
            value = self._min_value(guess, self._possible_answers)

            if value < best_value:
                best_value = value
                best_guess = guess
            #SE DUAS FOREM BOAS, PRIORIZE A VITÓRIA
            elif value == best_value and guess in self._possible_answers:
                best_guess = guess

        return best_guess