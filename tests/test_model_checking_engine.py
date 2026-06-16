import unittest
from dataclasses import dataclass

from engines.logic.model_checking.model_checking_engine import ModelCheckingEngine
from game.feedback import LetterFeedback
from game.termo import GameState

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG

@dataclass
class MockResult:
    guess: str
    feedback: tuple


class ModelCheckingEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = ModelCheckingEngine()

    def test_initially_all_words_are_possible(self):
        self.assertTrue(self.engine.is_word_possible("TERMO"))
        self.assertTrue(self.engine.is_word_possible("SAGAZ"))

    def test_correct_feedback_filters_words(self):
        self.engine.process_feedback("PORTA", (W, W, W, C, W))
        self.assertTrue(self.engine.is_word_possible("LENTE"))
        self.assertFalse(self.engine.is_word_possible("TERMO"))

    def test_wrong_feedback_eliminates_letter_completely(self):
        self.engine.process_feedback("SAGAZ", (W, W, W, W, W))
        self.assertTrue(self.engine.is_word_possible("TERMO"))
        self.assertFalse(self.engine.is_word_possible("CASAS"))

    def test_present_feedback_rules(self):
        self.engine.process_feedback("TERMO", (P, W, W, W, W))
        self.assertTrue(self.engine.is_word_possible("BASTA"))
        self.assertFalse(self.engine.is_word_possible("TOLOS"))

    def test_double_letter_edge_case(self):
        self.engine.process_feedback("ARARA", (W, P, W, W, C))
        self.assertTrue(self.engine.is_word_possible("PORTA"))
        self.assertFalse(self.engine.is_word_possible("AMORA"))
        self.assertFalse(self.engine.is_word_possible("ARARA"))

    def test_make_guess_initial_state_returns_rosea_if_in_vocab(self):
        state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        vocab = ("TERMO", "ROSEA", "SAGAZ")
        
        guess = self.engine.make_guess(state, vocab)
        
        self.assertEqual(guess, "ROSEA")
        self.assertEqual(self.engine._possible_answers, ["TERMO", "ROSEA", "SAGAZ"])

    def test_make_guess_fallback_if_rosea_not_in_vocab(self):
        state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        vocab = ("TERMO", "SAGAZ", "LIVRO") 
        
        guess = self.engine.make_guess(state, vocab)
        
        self.assertEqual(guess, "TERMO")

    def test_make_guess_filters_and_returns_valid_word(self):
        initial_state = GameState(history=(), attempts_remaining=6, won=False, lost=False, over=False)
        vocab = ("PORTA", "VESTE", "TERMO")
        self.engine.make_guess(initial_state, vocab)
        
        history = (MockResult(guess="PORTA", feedback=(W, W, W, C, W)),)
        state = GameState(history=history, attempts_remaining=5, won=False, lost=False, over=False)
        
        guess = self.engine.make_guess(state, vocab)
        
        self.assertEqual(guess, "VESTE")
        self.assertEqual(self.engine._possible_answers, ["VESTE"])


if __name__ == "__main__":
    unittest.main()