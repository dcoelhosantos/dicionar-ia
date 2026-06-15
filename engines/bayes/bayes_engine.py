from collections import Counter
from collections.abc import Sequence
import math

from game.feedback import LetterFeedback, WORD_LENGTH
from game.termo import GameState

ALPHABET_SIZE = 26
LETTER_COUNT_OUTCOMES = WORD_LENGTH + 1
MIN_CANDIDATES_FOR_COUNT_TIEBREAK = 101
OPENING_GUESS = "ROSEA"


class NaiveBayesEngine:
    def __init__(self, alpha: float = 1.0) -> None:
        if alpha <= 0:
            raise ValueError("alpha deve ser maior que zero")

        self._alpha = alpha
        self._possible_answers: list[str] = []
        self._vocabulary: tuple[str, ...] | None = None
        self._vocabulary_order: dict[str, int] = {}
        self._word_counts: dict[str, Counter[str]] = {}
        self._processed_history = ()

    def _prepare_vocabulary(self, vocabulary: tuple[str, ...]) -> None:
        if vocabulary is self._vocabulary or vocabulary == self._vocabulary:
            return

        self._vocabulary = vocabulary
        self._vocabulary_order = {
            word: index for index, word in enumerate(vocabulary)
        }
        self._word_counts = {
            word: Counter(word) for word in vocabulary
        }
        self._possible_answers = []
        self._processed_history = ()

    def _position_counts(
        self,
        words: Sequence[str],
    ) -> tuple[Counter[str], ...]:
        counts = tuple(Counter() for _ in range(WORD_LENGTH))

        for word in words:
            for index, letter in enumerate(word):
                counts[index][letter] += 1

        return counts

    def _letter_count_frequencies(
        self,
        words: Sequence[str],
    ) -> dict[str, Counter[int]]:
        frequencies: dict[str, Counter[int]] = {}

        for word in words:
            for letter, count in self._word_counts[word].items():
                frequencies.setdefault(letter, Counter())[count] += 1

        return frequencies

    def _position_log_probability(
        self,
        word: str,
        position_counts: tuple[Counter[str], ...],
        vocabulary_size: int,
    ) -> float:
        position_denominator = vocabulary_size + self._alpha * ALPHABET_SIZE

        return sum(
            math.log(
                (position_counts[index][letter] + self._alpha)
                / position_denominator
            )
            for index, letter in enumerate(word)
        )

    def _letter_count_log_probability(
        self,
        word: str,
        letter_count_frequencies: dict[str, Counter[int]],
        vocabulary_size: int,
    ) -> float:
        count_denominator = vocabulary_size + self._alpha * LETTER_COUNT_OUTCOMES
        word_counts = self._word_counts[word]

        return sum(
            math.log(
                (
                    letter_count_frequencies[letter][word_counts[letter]]
                    + self._alpha
                )
                / count_denominator
            )
            for letter in word
        )

    def _evaluate_known_words(
        self,
        answer: str,
        guess: str,
    ) -> tuple[LetterFeedback, ...]:
        remaining_letters = self._word_counts[answer].copy()
        feedback = [LetterFeedback.WRONG] * WORD_LENGTH

        for index, guessed_letter in enumerate(guess):
            if guessed_letter == answer[index]:
                feedback[index] = LetterFeedback.CORRECT
                remaining_letters[guessed_letter] -= 1

        for index, guessed_letter in enumerate(guess):
            if feedback[index] == LetterFeedback.CORRECT:
                continue

            if remaining_letters[guessed_letter] > 0:
                feedback[index] = LetterFeedback.PRESENT
                remaining_letters[guessed_letter] -= 1

        return tuple(feedback)

    def _filter_candidates(self, state: GameState) -> list[str]:
        history = state.history
        can_filter_incrementally = (
            bool(self._possible_answers)
            and len(history) == len(self._processed_history) + 1
            and history[:-1] == self._processed_history
        )

        if can_filter_incrementally:
            candidates = self._possible_answers
            results = history[-1:]
        elif history == self._processed_history:
            return self._possible_answers
        else:
            candidates = list(self._vocabulary or ())
            results = history

        for result in results:
            candidates = [
                candidate
                for candidate in candidates
                if self._evaluate_known_words(candidate, result.guess)
                == result.feedback
            ]

        self._processed_history = history
        return candidates

    def _rank_candidates(self, candidates: list[str]) -> list[str]:
        position_counts = self._position_counts(candidates)
        letter_count_frequencies = self._letter_count_frequencies(candidates)
        use_letter_count = len(candidates) >= MIN_CANDIDATES_FOR_COUNT_TIEBREAK

        def ranking_key(word: str) -> tuple[float, ...]:
            key = (
                -self._position_log_probability(
                    word,
                    position_counts,
                    len(candidates),
                ),
            )

            if use_letter_count:
                key += (
                    -self._letter_count_log_probability(
                        word,
                        letter_count_frequencies,
                        len(candidates),
                    ),
                )

            return key + (self._vocabulary_order[word],)

        return sorted(
            candidates,
            key=ranking_key,
        )

    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        if not vocabulary:
            raise ValueError("vocabulário não deve estar vazio")

        self._prepare_vocabulary(vocabulary)

        if not state.history:
            self._possible_answers = list(vocabulary)
            self._processed_history = ()

        if not state.history and OPENING_GUESS in vocabulary:
            return OPENING_GUESS

        candidates = self._filter_candidates(state)

        if not candidates:
            self._possible_answers = []
            raise ValueError(
                "Nenhum candidato restante no vocabulário para este histórico."
            )

        if len(candidates) == 1:
            self._possible_answers = candidates
            return candidates[0]

        self._possible_answers = self._rank_candidates(candidates)
        return self._possible_answers[0]
