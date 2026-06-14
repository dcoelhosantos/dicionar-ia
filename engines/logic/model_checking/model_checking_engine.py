from sympy import And

from engines.logic.base_logic_engine import BaseLogicEngine


class ModelCheckingEngine(BaseLogicEngine):
    def __init__(self):
        super().__init__()
        self._cached_kb_formula = None
        self._last_kb_size = 0

    def is_word_possible(self, word: str) -> bool:
        if not self.knowledge_base:
            return True
        
        if self._last_kb_size != len(self.knowledge_base):
            self._cached_kb_formula = And(*self.knowledge_base)
            self._last_kb_size = len(self.knowledge_base)
        
        model = {}
        for i, letter in enumerate(word):
            model[self.position_symbols[f"Pos{i}_{letter}"]] = True

            for other_letter in self.letters:
                if other_letter != letter:
                    model[self.position_symbols[f"Pos{i}_{other_letter}"]] = False
        
        result = self._cached_kb_formula.subs(model)
        return bool(result)