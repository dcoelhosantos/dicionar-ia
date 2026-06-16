from sympy import Not

from engines.logic.base_logic_engine import BaseLogicEngine
from engines.logic.dpll.cnf_utils import to_cnf_clauses
from engines.logic.dpll.dpll_algorithm import dpll


class DpllEngine(BaseLogicEngine):
    def __init__(self):
        super().__init__()
        self._cached_cnf = None
        self._last_kb_size = 0

    def is_word_possible(self, word: str) -> bool:
        """Valida a palavra transformando a KB em CNF e buscando contradições com o DPLL."""
        
        if self._cached_cnf is None or self._last_kb_size != len(self.knowledge_base):
            self._cached_cnf = []
            for formula in self.knowledge_base:
                self._cached_cnf.extend(to_cnf_clauses(formula))
            self._last_kb_size = len(self.knowledge_base)

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