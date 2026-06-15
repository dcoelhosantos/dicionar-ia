import unittest

from engines.bayes.bayes_engine import NaiveBayesEngine
from game.feedback import LetterFeedback, evaluate_guess
from game.termo import GameState, GuessResult

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG


def make_state(
    history: tuple[GuessResult, ...] = (),
    attempts_remaining: int = 6,
) -> GameState:
    return GameState(
        history=history,
        attempts_remaining=attempts_remaining,
        won=False,
        lost=False,
        over=False,
    )


class NaiveBayesEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = NaiveBayesEngine()

    def test_first_guess_prefers_rosea_when_available(self):
        vocabulary = ("ABCDE", "ROSEA", "ABCDF", "ZBCDE")

        guess = self.engine.make_guess(make_state(), vocabulary)

        self.assertEqual(guess, "ROSEA")
        self.assertEqual(self.engine._possible_answers, list(vocabulary))

    def test_first_guess_uses_highest_probability_when_rosea_is_missing(self):
        vocabulary = ("ABCDE", "ABCDF", "ABCDG", "ZBCDE")

        guess = self.engine.make_guess(make_state(), vocabulary)

        self.assertEqual(guess, "ABCDE")
        self.assertEqual(self.engine._possible_answers[0], "ABCDE")

    def test_ranks_possible_answers_by_probability(self):
        vocabulary = ("ABCDE", "ABCDF", "ABCDG", "ZBCDE")

        self.engine.make_guess(make_state(), vocabulary)

        self.assertEqual(
            self.engine._possible_answers,
            ["ABCDE", "ABCDF", "ABCDG", "ZBCDE"],
        )

    def test_filters_candidates_using_feedback(self):
        vocabulary = ("TERMO", "TERRA", "FESTA", "PUDIM")
        result = GuessResult("ROSEA", evaluate_guess("PUDIM", "ROSEA"))

        guess = self.engine.make_guess(
            make_state((result,), attempts_remaining=5),
            vocabulary,
        )

        self.assertEqual(guess, "PUDIM")
        self.assertEqual(self.engine._possible_answers, ["PUDIM"])

    def test_ranks_candidates_using_only_remaining_words(self):
        vocabulary = ("BBBBA", "AAAAA", "ZAAAA", "AAAAZ")
        result = GuessResult("ZZZZZ", (W, W, W, W, W))

        guess = self.engine.make_guess(
            make_state((result,), attempts_remaining=5),
            vocabulary,
        )

        self.assertEqual(guess, "BBBBA")
        self.assertEqual(self.engine._possible_answers, ["BBBBA", "AAAAA"])

    def test_filters_repeated_letters_using_exact_feedback(self):
        vocabulary = ("CARTA", "CACAU", "CASCA", "CARRO")
        result = GuessResult("CACAU", evaluate_guess("CARTA", "CACAU"))

        guess = self.engine.make_guess(
            make_state((result,), attempts_remaining=5),
            vocabulary,
        )

        self.assertEqual(guess, "CARTA")
        self.assertEqual(self.engine._possible_answers, ["CARTA"])

    def test_preserves_vocabulary_order_when_scores_are_equal(self):
        vocabulary = ("ABCDE", "EDCBA")

        self.engine.make_guess(make_state(), vocabulary)

        self.assertEqual(self.engine._possible_answers, list(vocabulary))

    def test_reuses_engine_for_a_new_game(self):
        vocabulary = ("TERMO", "PUDIM", "CASAS")
        result = GuessResult("TERMO", (W, W, W, W, W))
        self.engine.make_guess(
            make_state((result,), attempts_remaining=5),
            vocabulary,
        )

        guess = self.engine.make_guess(make_state(), vocabulary)

        self.assertIn(guess, vocabulary)
        self.assertEqual(set(self.engine._possible_answers), set(vocabulary))

    def test_rejects_empty_vocabulary(self):
        with self.assertRaisesRegex(ValueError, "não deve estar vazio"):
            self.engine.make_guess(make_state(), ())

    def test_rejects_history_without_compatible_candidates(self):
        vocabulary = ("TERMO", "PUDIM")
        impossible_result = GuessResult("TERMO", (C, C, C, C, C))

        with self.assertRaisesRegex(ValueError, "Nenhum candidato restante"):
            self.engine.make_guess(
                make_state((impossible_result, impossible_result)),
                ("PUDIM",),
            )

        self.assertEqual(self.engine._possible_answers, [])

    def test_rejects_non_positive_laplace_alpha(self):
        with self.assertRaisesRegex(ValueError, "alpha deve ser maior que zero"):
            NaiveBayesEngine(alpha=0)


if __name__ == "__main__":
    unittest.main()
