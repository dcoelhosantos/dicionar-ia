from dataclasses import dataclass
from pathlib import Path
import random
from game.feedback import (
    LetterFeedback,
    evaluate_guess,
    guess_is_correct,
    validate_word,
)

DEFAULT_WORDS_PATH = (
    Path(__file__).resolve().parent.parent / "dataset" / "words.txt"
)

MAX_ATTEMPTS = 6

@dataclass(frozen=True, slots=True)
class GuessResult:
    guess: str
    feedback: tuple[LetterFeedback, ...]


@dataclass(frozen=True, slots=True)
class GameState:
    history: tuple[GuessResult, ...]
    attempts_remaining: int
    won: bool
    lost: bool
    over: bool


def load_words(path: str | Path = DEFAULT_WORDS_PATH) -> tuple[str, ...]:
    dataset_path = Path(path)

    with dataset_path.open(encoding="utf-8") as dataset:
        words: list[str] = []

        for line in dataset:
            stripped_line = line.strip()
            if stripped_line:
                words.append(stripped_line)

    return tuple(words)


class TermoGame:
    def __init__(self) -> None:
        words = load_words()

        self._answer = random.choice(words)
        self._max_attempts = MAX_ATTEMPTS
        self._history = []
        self._won = False

    @property
    def state(self) -> GameState:
        attempts_remaining = self._max_attempts - len(self._history)

        if self._won:
            lost = False
            over = True
        else:
            if attempts_remaining == 0:
                lost = True
                over = True
            else:
                lost = False
                over = False

        return GameState(
            history=tuple(self._history),
            attempts_remaining=attempts_remaining,
            won=self._won,
            lost=lost,
            over=over,
        )

    def make_guess(self, guess: str) -> GuessResult:
        if self.state.over:
            raise RuntimeError("A partida já foi encerrada.")

        normalized_guess = validate_word(guess)

        for previous_result in self._history:
            if previous_result.guess == normalized_guess:
                raise ValueError("Essa palavra já foi utilizada anteriormente.")

        feedback = evaluate_guess(self._answer, normalized_guess)
        result = GuessResult(guess=normalized_guess, feedback=feedback)

        self._history.append(result)
        self._won = guess_is_correct(feedback)

        return result
