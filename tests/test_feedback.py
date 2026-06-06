import unittest
from game.feedback import LetterFeedback, evaluate_guess, is_correct_guess, validate_word

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG

class FeedbackTestCase(unittest.TestCase):

    def test_marks_all_letters_correct(self):
        feedback = evaluate_guess("TERMO", "TERMO")
        self.assertEqual(feedback, (C, C, C, C, C))
        self.assertTrue(is_correct_guess(feedback))

    def test_marks_present_letters_in_wrong_positions(self):
        feedback = evaluate_guess("TERMO", "OMTRE")
        self.assertEqual(feedback, (P, P, P, P, P))
        self.assertFalse(is_correct_guess(feedback))

    def test_marks_wrong_letters(self):
        feedback = evaluate_guess("TERMO", "SALAS")
        self.assertEqual(feedback, (W, W, W, W, W))

    def test_handles_repeated_letters_without_extra_present_matches(self):
        feedback = evaluate_guess("CARTA", "CACAU")
        self.assertEqual(feedback, (C, C, W, P, W))

    def test_normalizes_accents_and_case(self):
        self.assertEqual(validate_word("órgão"), "ORGAO")

    def test_rejects_words_with_invalid_length(self):
        with self.assertRaises(ValueError):
            validate_word("CASA")

    def test_rejects_words_with_non_letters(self):
        with self.assertRaises(ValueError):
            validate_word("AB12C")

if __name__ == "__main__":
    unittest.main()
