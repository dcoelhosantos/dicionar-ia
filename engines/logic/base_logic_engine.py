from sympy import Not, Or, symbols

from game.feedback import LetterFeedback
from game.termo import GameState


class BaseLogicEngine:
    def __init__(self):
        self.letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.position_symbols = {}
        self.knowledge_base = []
        self._possible_answers = []

        # Inicializa a matriz de símbolos lógicos (Pos0_A, Pos0_B, etc.)
        for i in range(5):
            for letter in self.letters:
                symbol_name = f"Pos{i}_{letter}"
                self.position_symbols[symbol_name] = symbols(symbol_name)
    
    def process_feedback(self, guess: str, feedback: tuple[LetterFeedback, ...]):
        """Atualiza a Base de Conhecimento (KB) baseado no feedback."""
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
    
    def is_word_possible(self, word: str) -> bool:
        raise NotImplementedError("As classes filhas devem implementar este método.")
    
    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        """Calcula o próximo palpite com base no estado do jogo."""
        
        if not state.history:
            self.knowledge_base = []
            self._possible_answers = list(vocabulary)
            return "ROSEA" if "ROSEA" in vocabulary else vocabulary[0]

        last_play = state.history[-1]
        self.process_feedback(last_play.guess, last_play.feedback)

        self._possible_answers = [
            word for word in self._possible_answers if self.is_word_possible(word)
        ]

        if len(self._possible_answers) == 1:
            return self._possible_answers[0]

        if self._possible_answers:
            return self._possible_answers[0]

        # Fallback de segurança 
        return "TERMO" if "TERMO" in vocabulary else vocabulary[0]