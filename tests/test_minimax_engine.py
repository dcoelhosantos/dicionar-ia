import unittest
from game.termo import GameState
from game.feedback import LetterFeedback
from engines.minimax.minimax_engine import MinimaxEngine

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG

class MockGuessResult:
    def __init__(self, guess, feedback):
        self.guess = guess
        self.feedback = feedback

class MinimaxEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = MinimaxEngine()
        self.vocab = ("ROSEA", "TERMO", "PUDIM", "CASAS")

    def test_first_guess_prefers_rosea_when_available(self):
        state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        guess = self.engine.make_guess(state, self.vocab)
        self.assertEqual(guess, "ROSEA")
        self.assertEqual(self.engine._possible_answers, list(self.vocab))

    def test_first_guess_falls_back_to_vocabulary_when_rosea_missing(self):
        vocab_without_rosea = ("TERMO", "PUDIM", "CASAS")
        state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        guess = self.engine.make_guess(state, vocab_without_rosea)
        self.assertIn(guess, vocab_without_rosea)
        self.assertEqual(self.engine._possible_answers, list(vocab_without_rosea))

    def test_makes_correct_deduction_when_one_option_remains(self):
        # Assumindo que todas as letras de ROSEA estão erradas
        # "TERMO" tem "R, O, E". "CASAS" tem "S". A única restante no vocabulário sem nenhuma letra é "PUDIM"
        history = (MockGuessResult("ROSEA", (W, W, W, W, W)),)
        state = GameState(history=history, attempts_remaining=5, won=False, lost=False, over=False)
        self.engine._possible_answers = list(self.vocab)
        guess = self.engine.make_guess(state, self.vocab)
        self.assertEqual(guess, "PUDIM")

    def test_is_valid_candidate_filters_correctly(self):
        # Verificar feedback -> (C,C,C,W,W), a palavra "TERMO" é compatível com o chute "TERRA"?
        is_valid = self.engine._is_valid_candidate("TERMO", "TERRA", (C, C, C, W, W))
        self.assertTrue(is_valid)

        # Verificar feedback inválido -> (C,C,C,W,W), a palavra "CASAS" é compatível com o chute "TERRA"?
        is_invalid = self.engine._is_valid_candidate("CASAS", "TERRA", (C, C, C, W, W))
        self.assertFalse(is_invalid)

if __name__ == "__main__":
    unittest.main()