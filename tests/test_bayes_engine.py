from itertools import product
import unittest
from unittest.mock import patch

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

    def test_ranks_candidates_with_repeated_letters(self):
        vocabulary = ("AAAAA", "AAAAB", "AAABB", "BBCDE")

        self.engine.make_guess(make_state(), vocabulary)

        self.assertEqual(
            self.engine._possible_answers,
            ["AAAAB", "AAAAA", "AAABB", "BBCDE"],
        )

    def test_calculates_distinct_probabilities_for_letter_counts(self):
        vocabulary = ("AAAAA", "AAAAB", "AAABB", "BBCDE")
        self.engine._prepare_vocabulary(vocabulary)
        frequencies = self.engine._letter_count_frequencies(vocabulary)

        all_a_score = self.engine._letter_count_log_probability(
            "AAAAA",
            frequencies,
            len(vocabulary),
        )
        mixed_score = self.engine._letter_count_log_probability(
            "AAABB",
            frequencies,
            len(vocabulary),
        )

        self.assertNotEqual(all_a_score, mixed_score)

    def test_uses_letter_counts_to_break_ties_in_large_candidate_sets(self):
        vocabulary = tuple(
            "".join(letters)
            for letters in product("ABCDE", repeat=5)
        )[:101]
        self.engine._prepare_vocabulary(vocabulary)

        with (
            patch.object(
                self.engine,
                "_position_log_probability",
                return_value=0.0,
            ),
            patch.object(
                self.engine,
                "_letter_count_log_probability",
                side_effect=lambda word, frequencies, size: (
                    1.0 if word == "AAAAA" else 0.0
                ),
            ) as count_probability,
        ):
            ranked = self.engine._rank_candidates(list(vocabulary))

        self.assertEqual(ranked[0], "AAAAA")
        self.assertEqual(count_probability.call_count, len(vocabulary))

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

    def test_filters_only_previous_candidates_for_sequential_history(self):
        vocabulary = (
            "ROSEA",
            "TERMO",
            "TERRA",
            "FESTA",
            "PUDIM",
            "CARTA",
            "CACAU",
            "CASCA",
            "CARRO",
            "MUNDO",
            "FUNDO",
            "JUNTO",
        )
        first_result = GuessResult("PUDIM", evaluate_guess("ROSEA", "PUDIM"))
        second_result = GuessResult("CARTA", evaluate_guess("ROSEA", "CARTA"))

        with patch.object(
            self.engine,
            "_evaluate_known_words",
            wraps=self.engine._evaluate_known_words,
        ) as evaluate_mock:
            self.engine.make_guess(make_state((first_result,), 5), vocabulary)
            remaining_after_first = len(self.engine._possible_answers)
            calls_after_first = evaluate_mock.call_count

            self.engine.make_guess(
                make_state((first_result, second_result), 4),
                vocabulary,
            )

        self.assertEqual(calls_after_first, len(vocabulary))
        self.assertEqual(
            evaluate_mock.call_count - calls_after_first,
            remaining_after_first,
        )

    def test_rebuilds_candidates_for_non_sequential_history(self):
        vocabulary = ("ROSEA", "TERMO", "TERRA", "FESTA", "PUDIM", "CARTA")
        first_result = GuessResult("PUDIM", evaluate_guess("ROSEA", "PUDIM"))
        replacement = GuessResult("PUDIM", evaluate_guess("TERMO", "PUDIM"))

        self.engine.make_guess(make_state((first_result,), 5), vocabulary)
        guess = self.engine.make_guess(make_state((replacement,), 5), vocabulary)

        fresh_engine = NaiveBayesEngine()
        expected_guess = fresh_engine.make_guess(
            make_state((replacement,), 5),
            vocabulary,
        )
        self.assertEqual(guess, expected_guess)
        self.assertEqual(
            self.engine._possible_answers,
            fresh_engine._possible_answers,
        )

    def test_rebuilds_metadata_when_vocabulary_changes(self):
        first_vocabulary = ("ROSEA", "TERMO", "TERRA")
        second_vocabulary = ("PUDIM", "CARTA", "CASCA")

        self.engine.make_guess(make_state(), first_vocabulary)
        first_metadata = self.engine._word_counts
        self.engine.make_guess(make_state(), first_vocabulary)

        self.assertIs(self.engine._word_counts, first_metadata)

        self.engine.make_guess(make_state(), second_vocabulary)

        self.assertIsNot(self.engine._word_counts, first_metadata)
        self.assertEqual(
            set(self.engine._word_counts),
            set(second_vocabulary),
        )
        self.assertEqual(
            set(self.engine._possible_answers),
            set(second_vocabulary),
        )

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
