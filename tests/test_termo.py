import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from game.feedback import LetterFeedback
from game.termo import GameState, TermoGame, load_words

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG


class LoadWordsTestCase(unittest.TestCase):
    def test_loads_non_empty_lines_without_normalization(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset_path = Path(temporary_directory) / "words.txt"
            dataset_path.write_text(
                "TERMO\nORGAO\n\nTERMO\n",
                encoding="utf-8",
            )

            words = load_words(dataset_path)

        self.assertEqual(words, ("TERMO", "ORGAO", "TERMO"))

class TermoGameTestCase(unittest.TestCase):
    def setUp(self):
        load_words_patcher = patch(
            "game.termo.load_words",
            return_value=("TERMO",),
        )
        self.load_words_mock = load_words_patcher.start()
        self.addCleanup(load_words_patcher.stop)

    def test_starts_with_empty_state_without_exposing_answer(self):
        game = TermoGame()

        self.assertEqual(
            game.state,
            GameState(
                history=(),
                attempts_remaining=6,
                won=False,
                lost=False,
                over=False,
            ),
        )
        self.assertFalse(hasattr(game.state, "answer"))

    def test_records_and_normalizes_valid_guess(self):
        game = TermoGame()

        result = game.make_guess("órgão")

        self.assertEqual(result.guess, "ORGAO")
        self.assertEqual(result.feedback, (W, P, W, W, C))
        self.assertEqual(game.state.history, (result,))
        self.assertEqual(game.state.attempts_remaining, 5)

    def test_repeated_guess_does_not_consume_attempt(self):
        game = TermoGame()
        game.make_guess("casas")

        with self.assertRaisesRegex(ValueError, "já foi utilizada"):
            game.make_guess("cásas")

        self.assertEqual(len(game.state.history), 1)
        self.assertEqual(game.state.attempts_remaining, 5)

    def test_correct_guess_wins_and_ends_game(self):
        game = TermoGame()

        result = game.make_guess("termo")

        self.assertEqual(result.feedback, (C, C, C, C, C))
        self.assertTrue(game.state.won)
        self.assertFalse(game.state.lost)
        self.assertTrue(game.state.over)

    def test_game_ends_after_max_attempts(self):
        game = TermoGame()
        game._max_attempts = 2

        game.make_guess("CASAS")
        game.make_guess("PULAR")

        self.assertFalse(game.state.won)
        self.assertTrue(game.state.lost)
        self.assertTrue(game.state.over)
        self.assertEqual(game.state.attempts_remaining, 0)

    def test_rejects_guess_after_game_ends(self):
        game = TermoGame()
        game._max_attempts = 1
        game.make_guess("CASAS")

        with self.assertRaisesRegex(RuntimeError, "já foi encerrada"):
            game.make_guess("TERMO")

    @patch("game.termo.random.choice", return_value="TERMO")
    def test_creates_game_with_random_answer(self, random_choice_mock):
        game = TermoGame()

        result = game.make_guess("TERMO")

        self.load_words_mock.assert_called_once_with()
        random_choice_mock.assert_called_once_with(("TERMO",))
        self.assertTrue(all(item == C for item in result.feedback))


if __name__ == "__main__":
    unittest.main()
