from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from engines.logic.dpll.dpll_engine import DpllEngine
from engines.logic.model_checking.model_checking_engine import ModelCheckingEngine
from engines.minimax.minimax_engine import MinimaxEngine
from game.termo import GameState


class TermoEngine(Protocol):
    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        ...


EngineFactory = Callable[[], TermoEngine]


@dataclass(frozen=True, slots=True)
class EngineDefinition:
    name: str
    factory: EngineFactory | None

    @property
    def available(self) -> bool:
        return self.factory is not None

    def create_session(self, vocabulary: tuple[str, ...]) -> "EngineSession":
        if self.factory is None:
            raise RuntimeError(f"O motor {self.name} ainda não está disponível.")

        return EngineSession(
            name=self.name,
            engine=self.factory(),
            vocabulary=vocabulary,
        )


ENGINE_REGISTRY = (
    EngineDefinition("Naive Bayes", None),
    EngineDefinition("Minimax", MinimaxEngine),
    EngineDefinition("Model Checking", ModelCheckingEngine), 
    EngineDefinition("DPLL Solver", DpllEngine),            
)


class EngineSession:
    def __init__(
        self,
        name: str,
        engine: TermoEngine,
        vocabulary: tuple[str, ...],
    ) -> None:
        self.name = name
        self._engine = engine
        self._vocabulary = vocabulary
        self._valid_words = set(vocabulary)
        self._cached_history = None
        self._cached_suggestions: tuple[str, ...] = ()

    def suggestions(self, state: GameState, limit: int = 5) -> tuple[str, ...]:
        if limit < 1:
            return ()

        if state.history == self._cached_history:
            return self._cached_suggestions[:limit]

        recommendation = self._engine.make_guess(state, self._vocabulary)
        if recommendation not in self._valid_words:
            raise ValueError(
                f"O motor {self.name} sugeriu uma palavra fora do dataset: "
                f"{recommendation}."
            )

        suggestions = [recommendation]
        candidates = getattr(self._engine, "_possible_answers", ())

        for candidate in candidates:
            if candidate not in self._valid_words:
                continue
            if candidate in suggestions:
                continue

            suggestions.append(candidate)
            if len(suggestions) == limit:
                break

        self._cached_history = state.history
        self._cached_suggestions = tuple(suggestions)
        return self._cached_suggestions
