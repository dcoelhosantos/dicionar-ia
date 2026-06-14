from sympy import Not, Or, symbols

from engines.dpll_solver.cnf_utils import to_cnf_clauses
from engines.dpll_solver.dpll_algorithm import dpll
from game.feedback import LetterFeedback
from game.termo import GameState


class LogicEngine:
    """Motor lógico que gerencia o estado de conhecimento e filtra palavras."""

    def __init__(self):
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.position_symbols = {}
        self.knowledge_base = []
        self._cached_cnf = None
        self._possible_answers = []

        # Inicializa a matriz de símbolos lógicos (Pos0_A, Pos0_B, etc.)
        for i in range(5):
            for letter in self.letters:
                symbol_name = f"Pos{i}_{letter}"
                self.position_symbols[symbol_name] = symbols(symbol_name)

    def process_feedback(self, guess: str, feedback: tuple[LetterFeedback, ...]):
        """Traduz o feedback visual em regras proposicionais na base de conhecimento."""
        letters_with_positive_feedback = {
            guess[i] for i, res in enumerate(feedback)
            if res in (LetterFeedback.CORRECT, LetterFeedback.PRESENT)
        }

        for i, (letter, result) in enumerate(zip(guess, feedback)):
            current_symbol = self.position_symbols[f"Pos{i}_{letter}"]

            if result == LetterFeedback.CORRECT:
                self.knowledge_base.append(current_symbol)

            elif result == LetterFeedback.PRESENT:
                self.knowledge_base.append(Not(current_symbol))
                other_positions = [
                    self.position_symbols[f"Pos{j}_{letter}"]
                    for j in range(5) if j != i
                ]
                self.knowledge_base.append(Or(*other_positions))

            elif result == LetterFeedback.WRONG:
                self.knowledge_base.append(Not(current_symbol))
                if letter not in letters_with_positive_feedback:
                    for j in range(5):
                        self.knowledge_base.append(Not(self.position_symbols[f"Pos{j}_{letter}"]))
        self._cached_cnf = None

    def is_word_possible(self, word: str) -> bool:
        """Verifica se a palavra candidata satisfaz todas as regras da base de conhecimento."""
        if self._cached_cnf is None:
            self._cached_cnf = []
            for formula in self.knowledge_base:
                self._cached_cnf.extend(to_cnf_clauses(formula))

        word_clauses = []
        for i, letter in enumerate(word):
            symbol = self.position_symbols[f"Pos{i}_{letter}"]
            word_clauses.append({symbol})

            for other_letter in self.letters:
                if other_letter != letter:
                    other_symbol = self.position_symbols[f"Pos{i}_{other_letter}"]
                    word_clauses.append({Not(other_symbol)})

        test_clauses = self._cached_cnf + word_clauses
        result = dpll(test_clauses)

        return result is not False
    
    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        """Calcula o próximo palpite com base no estado do jogo."""
        
        if not state.history:
            self.knowledge_base = []
            self._cached_cnf = None
            self._possible_answers = list(vocabulary)
            return "ROSEA" 

        last_play = state.history[-1]
        self.process_feedback(last_play.guess, last_play.feedback)

        survivors = []
        for word in self._possible_answers:
            if self.is_word_possible(word):
                survivors.append(word)

        self._possible_answers = survivors

        if len(self._possible_answers) == 1:
            return self._possible_answers[0]

        if self._possible_answers:
            return self._possible_answers[0]

        # Fallback de segurança 
        return "TERMO"
