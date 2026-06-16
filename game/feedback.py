from collections import Counter
from enum import Enum
import unicodedata

WORD_LENGTH = 5

class LetterFeedback(str, Enum):
    CORRECT = "correct"
    PRESENT = "present"
    WRONG = "wrong"

def normalize_word(word: str) -> str:
    normalized_word = unicodedata.normalize("NFKD", word.strip())
    without_accents = "".join(
        letter for letter in normalized_word if not unicodedata.combining(letter)
    )
    return without_accents.upper()


def validate_word(word: str) -> str:
    normalized = normalize_word(word)

    if len(normalized) != WORD_LENGTH:
        raise ValueError("A palavra deve ter exatamente 5 letras.")

    if not normalized.isalpha() or not normalized.isascii():
        raise ValueError("A palavra deve conter apenas letras de A a Z.")

    return normalized


def evaluate_guess(answer: str, guess: str) -> tuple[LetterFeedback, ...]:
    answer = validate_word(answer)
    guess = validate_word(guess)

    feedback: list[LetterFeedback | None] = [None] * WORD_LENGTH
    remaining_letters: Counter[str] = Counter()

    for index, guessed_letter in enumerate(guess):
        if guessed_letter == answer[index]:
            feedback[index] = LetterFeedback.CORRECT
        else:
            remaining_letters[answer[index]] += 1

    for index, guessed_letter in enumerate(guess):
        if feedback[index] is not None:
            continue

        if remaining_letters[guessed_letter] > 0:
            feedback[index] = LetterFeedback.PRESENT
            remaining_letters[guessed_letter] -= 1
        else:
            feedback[index] = LetterFeedback.WRONG

    return tuple(result for result in feedback if result is not None)


def guess_is_correct(feedback: tuple[LetterFeedback, ...]) -> bool:
    for result in feedback:
        if result != LetterFeedback.CORRECT:
            return False
    
    return True