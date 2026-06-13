import random
from game.termo import GameState
from game.feedback import evaluate_guess, LetterFeedback

class MinimaxEngine:
    def __init__(self):
        self._possible_answers: list[str] = []

    def _is_valid_candidate(self, candidate: str, guess: str, feedback: tuple[LetterFeedback, ...]) -> bool:
        return evaluate_guess(candidate, guess) == feedback

    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        if not state.history:
            self._possible_answers = list(vocabulary)

            return "SAROE"

        last_result = state.history[-1]
        last_guess = last_result.guess
        last_feedback = last_result.feedback

        self._possible_answers = [
            word for word in self._possible_answers
            if self._is_valid_candidate(word, last_guess, last_feedback)
        ]

        if len(self._possible_answers) == 1:
            return self._possible_answers[0]

        return random.choice(self._possible_answers)