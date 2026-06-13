from sympy import Not

from engines.dpll_solver.cnf_utils import get_symbol, negate_literal


def dpll(clauses, assignment=None):
    """Implementa o algoritmo DPLL com Unit Propagation para satisfatibilidade."""
    if assignment is None:
        assignment = {}

    current_clauses = [c.copy() for c in clauses]
    current_assignment = assignment.copy()

    while True:
        unit_clause_found = False
        for clause in current_clauses:
            if len(clause) == 1:
                literal = list(clause)[0]
                symbol = get_symbol(literal)
                value = True if not isinstance(literal, Not) else False

                if symbol in current_assignment and current_assignment[symbol] != value:
                    return False

                if symbol not in current_assignment:
                    current_assignment[symbol] = value
                    unit_clause_found = True
                    
                    new_current_clauses = []
                    for c in current_clauses:
                        if literal in c:
                            continue
                        if negate_literal(literal) in c:
                            c.remove(negate_literal(literal))
                            if not c:
                                return False
                        new_current_clauses.append(c)
                    
                    current_clauses = new_current_clauses
                    break

        if unit_clause_found:
            continue
        break

    if not current_clauses:
        return current_assignment

    if any(not c for c in current_clauses):
        return False

    unassigned_symbols = set()
    for clause in current_clauses:
        for literal in clause:
            symbol = get_symbol(literal)
            if symbol not in current_assignment:
                unassigned_symbols.add(symbol)

    if not unassigned_symbols:
        return current_assignment

    p = unassigned_symbols.pop()

    result_true = dpll(current_clauses + [{p}], {**current_assignment, p: True})
    if result_true is not False:
        return result_true

    result_false = dpll(current_clauses + [{Not(p)}], {**current_assignment, p: False})
    if result_false is not False:
        return result_false

    return False