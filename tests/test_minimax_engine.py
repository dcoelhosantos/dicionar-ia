import unittest
from game.termo import GameState
from game.feedback import LetterFeedback
from engines.minimax_engine import MinimaxEngine

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
        self.vocab = ("SAROE", "TERMO", "PUDIM", "CASAS")

    def test_first_guess_is_always_saroe(self):
        state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        guess = self.engine.make_guess(state, self.vocab)
        self.assertEqual(guess, "SAROE")
        self.assertEqual(self.engine._possible_answers, list(self.vocab))

    def test_makes_correct_deduction_when_one_option_remains(self):
        #Assumindo que todas as letras de SAROE estão erradas
        #"TERMO" tem "R, O, E". "CASAS" tem "S". A única restante no vocabulário sem nenhuma letra é "PUDIM"
        history = (MockGuessResult("SAROE", (W, W, W, W, W)),)
        state = GameState(history=history, attempts_remaining=5, won=False, lost=False, over=False)
        self.engine._possible_answers = list(self.vocab)
        guess = self.engine.make_guess(state, self.vocab)
        self.assertEqual(guess, "PUDIM")

    def test_is_valid_candidate_filters_correctly(self):
        #Verificar feedback -> (C,C,C,W,W), a palavra "TERMO" é compatível com o chute "TERRA"?
        is_valid = self.engine._is_valid_candidate("TERMO", "TERRA", (C, C, C, W, W))
        self.assertTrue(is_valid)

        #Verificar feedback inválido -> (C,C,C,W,W), a palavra "CASAS" é compatível com o chute "TERRA"?
        is_invalid = self.engine._is_valid_candidate("CASAS", "TERRA", (C, C, C, W, W))
        self.assertFalse(is_invalid)

if __name__ == "__main__":
    unittest.main()