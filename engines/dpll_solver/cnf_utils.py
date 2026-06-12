from sympy import And, Not, Or
from sympy.logic.inference import to_cnf


def get_symbol(literal):
    if isinstance(literal, Not):
        return literal.args[0]
    return literal

def negate_literal(literal):
    if isinstance(literal, Not):
        return literal.args[0]
    return Not(literal)

def to_set_of_literals(clause):
    if isinstance(clause, Or):
        return set(clause.args)
    return {clause}

def to_cnf_clauses(formula):
    cnf_form = to_cnf(formula)
    if isinstance(cnf_form, And):
        return [to_set_of_literals(clause) for clause in cnf_form.args]
    return [to_set_of_literals(cnf_form)]