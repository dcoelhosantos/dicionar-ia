import unittest

from engines.dpll_solver.dpll_solver_engine import LogicEngine
from game.feedback import LetterFeedback

C = LetterFeedback.CORRECT
P = LetterFeedback.PRESENT
W = LetterFeedback.WRONG


class LogicEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = LogicEngine()

    def test_initially_all_words_are_possible(self):
        # Sem nenhum feedback, qualquer palavra do dicionário deve ser aceita
        self.assertTrue(self.engine.is_word_possible("TERMO"))
        self.assertTrue(self.engine.is_word_possible("SAGAZ"))

    def test_correct_feedback_filters_words(self):
        # Chute: "PORTA". Feedback diz que APENAS o 'T' (pos 3) está correto.
        self.engine.process_feedback("PORTA", (W, W, W, C, W))

        # "LENTE" tem 'T' na pos 3 e não usa P, O, R ou A -> Deve ser possível
        self.assertTrue(self.engine.is_word_possible("LENTE"))
        # "TERMO" tem 'M' na pos 3 -> Deve ser impossível
        self.assertFalse(self.engine.is_word_possible("TERMO"))

    def test_wrong_feedback_eliminates_letter_completely(self):
        # Chute: "SAGAZ". Todas as letras não existem na palavra secreta.
        self.engine.process_feedback("SAGAZ", (W, W, W, W, W))

        # "TERMO" não tem S, A, G ou Z -> Deve ser possível
        self.assertTrue(self.engine.is_word_possible("TERMO"))
        # "CASAS" tem S e A -> Deve ser impossível
        self.assertFalse(self.engine.is_word_possible("CASAS"))

    def test_present_feedback_rules(self):
        # Chute: "TERMO". O 'T' existe, mas NÃO na pos 0. E, R, M, O não existem.
        self.engine.process_feedback("TERMO", (P, W, W, W, W))

        # "BASTA" tem T na pos 3 e não usa E, R, M ou O -> Possível
        self.assertTrue(self.engine.is_word_possible("BASTA"))
        # "TOLOS" tem T na pos 0 (onde recebemos amarelo) -> Impossível
        self.assertFalse(self.engine.is_word_possible("TOLOS"))

    def test_double_letter_edge_case(self):
        # Resposta seria "PORTA", o chute foi "ARARA".
        # O primeiro 'A' fica cinza, o R do meio amarelo, e o último 'A' fica verde.
        self.engine.process_feedback("ARARA", (W, P, W, W, C))

        # "PORTA" atende a todos os requisitos acima!
        self.assertTrue(self.engine.is_word_possible("PORTA"))
        # "AMORA" tem 'A' na pos 0 (onde deu cinza), então tem que ser barrada.
        self.assertFalse(self.engine.is_word_possible("AMORA"))
        # "ARARA" original tem que ser barrada porque as posições 0, 1 e 2 deram erro.
        self.assertFalse(self.engine.is_word_possible("ARARA"))


if __name__ == "__main__":
    unittest.main()