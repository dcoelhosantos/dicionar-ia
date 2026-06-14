import unittest

from game.cli.engine_session import ENGINE_REGISTRY, EngineSession
from game.termo import GameState


EMPTY_STATE = GameState(
    history=(),
    attempts_remaining=6,
    won=False,
    lost=False,
    over=False,
)


class FakeEngine:
    def __init__(self):
        self.calls = 0
        self._possible_answers = ["TERMO", "CASAS", "PULAR", "ORGAO", "TERMO"]

    def make_guess(self, state, vocabulary):
        self.calls += 1
        return "TERMO"


class InvalidEngine:
    _possible_answers = []

    def make_guess(self, state, vocabulary):
        return "ABCDE"


class EngineSessionTestCase(unittest.TestCase):
    def test_registry_identifies_available_engines(self):
        availability = {item.name: item.available for item in ENGINE_REGISTRY}

        self.assertTrue(availability["Minimax"])
        self.assertTrue(availability["DPLL Solver"])
        self.assertFalse(availability["Naive Bayes"])
        self.assertFalse(availability["Model Checking"])

    def test_suggestions_include_recommendation_and_unique_candidates(self):
        session = EngineSession(
            "Teste",
            FakeEngine(),
            ("TERMO", "CASAS", "PULAR", "ORGAO"),
        )

        suggestions = session.suggestions(EMPTY_STATE)

        self.assertEqual(suggestions, ("TERMO", "CASAS", "PULAR", "ORGAO"))

    def test_suggestions_are_cached_for_same_history(self):
        engine = FakeEngine()
        session = EngineSession(
            "Teste",
            engine,
            ("TERMO", "CASAS", "PULAR", "ORGAO"),
        )

        session.suggestions(EMPTY_STATE)
        session.suggestions(EMPTY_STATE)

        self.assertEqual(engine.calls, 1)

    def test_rejects_recommendation_outside_dataset(self):
        session = EngineSession("Teste", InvalidEngine(), ("TERMO",))

        with self.assertRaisesRegex(ValueError, "fora do dataset"):
            session.suggestions(EMPTY_STATE)


if __name__ == "__main__":
    unittest.main()
