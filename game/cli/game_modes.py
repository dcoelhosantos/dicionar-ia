from collections.abc import Callable
from dataclasses import dataclass
import time

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from game.cli.cli_views import (
    build_comparison_table,
    build_game_view,
    show_game_result,
)
from game.cli.engine_session import (
    ENGINE_REGISTRY,
    EngineDefinition,
    EngineSession,
)
from game.termo import TermoGame, load_words

InputFunction = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class EngineRunResult:
    name: str
    status: str
    attempts: int
    elapsed_seconds: float
    error: str | None = None


def pause(console: Console, input_function: InputFunction) -> None:
    console.print("Pressione Enter para continuar.")
    input_function("")


def play_manual_game(
    console: Console,
    input_function: InputFunction = input,
) -> bool:
    game = TermoGame()

    while not game.state.over:
        console.print(build_game_view(game.state))
        try:
            game.make_guess(input_function("Digite uma palavra: "))
        except ValueError as error:
            console.print(Panel(str(error), border_style="red"))
        except (EOFError, KeyboardInterrupt):
            return False

    console.print(build_game_view(game.state))
    show_game_result(console, game)
    try:
        pause(console, input_function)
    except (EOFError, KeyboardInterrupt):
        return False
    return True


def play_assisted_game(
    console: Console,
    definition: EngineDefinition,
    input_function: InputFunction = input,
) -> bool:
    vocabulary = load_words()
    game = TermoGame()
    session = definition.create_session(vocabulary)

    while not game.state.over:
        try:
            suggestions = session.suggestions(game.state)
        except (RuntimeError, ValueError) as error:
            console.print(Panel(str(error), title="Erro do motor", border_style="red"))
            return False

        console.print(
            build_game_view(
                game.state,
                engine_name=definition.name,
                suggestions=suggestions,
            )
        )

        try:
            game.make_guess(input_function("Digite uma palavra: "))
        except ValueError as error:
            console.print(Panel(str(error), border_style="red"))
        except (EOFError, KeyboardInterrupt):
            return False

    console.print(build_game_view(game.state, engine_name=definition.name))
    show_game_result(console, game)
    try:
        pause(console, input_function)
    except (EOFError, KeyboardInterrupt):
        return False
    return True


def run_engine_game(
    game: TermoGame,
    session: EngineSession,
) -> EngineRunResult:
    started_at = time.perf_counter()
    error_message = None

    try:
        while not game.state.over:
            suggestions = session.suggestions(game.state)
            if not suggestions:
                raise ValueError("O motor não forneceu uma sugestão.")
            game.make_guess(suggestions[0])
    except (RuntimeError, ValueError) as error:
        error_message = str(error)

    elapsed = time.perf_counter() - started_at
    if error_message is not None:
        status = "Erro"
    elif game.state.won:
        status = "Vitória"
    else:
        status = "Derrota"

    return EngineRunResult(
        name=session.name,
        status=status,
        attempts=len(game.state.history),
        elapsed_seconds=elapsed,
        error=error_message,
    )


def play_automatic_game(
    console: Console,
    definition: EngineDefinition,
    input_function: InputFunction = input,
) -> EngineRunResult:
    vocabulary = load_words()
    game = TermoGame()
    session = definition.create_session(vocabulary)
    started_at = time.perf_counter()
    error_message = None

    while not game.state.over:
        try:
            suggestions = session.suggestions(game.state)
            if not suggestions:
                raise ValueError("O motor não forneceu uma sugestão.")
            game.make_guess(suggestions[0])
        except (RuntimeError, ValueError) as error:
            error_message = str(error)
            break

        console.print(
            build_game_view(
                game.state,
                engine_name=definition.name,
                suggestions=suggestions,
            )
        )
        if not game.state.over:
            try:
                pause(console, input_function)
            except (EOFError, KeyboardInterrupt):
                error_message = "Execução interrompida."
                break

    elapsed = time.perf_counter() - started_at
    if error_message:
        status = "Erro"
        console.print(Panel(error_message, title="Erro do motor", border_style="red"))
    elif game.state.won:
        status = "Vitória"
    else:
        status = "Derrota"

    if game.state.over:
        show_game_result(console, game)

    console.print(
        Panel(
            Group(
                Text(f"Resultado: {status}"),
                Text(f"Tentativas: {len(game.state.history)}"),
                Text(f"Tempo total: {elapsed:.3f} segundos"),
            ),
            title=definition.name,
            border_style="cyan",
        )
    )

    return EngineRunResult(
        definition.name,
        status,
        len(game.state.history),
        elapsed,
        error_message,
    )


def compare_engines(console: Console) -> tuple[EngineRunResult, ...]:
    available = tuple(item for item in ENGINE_REGISTRY if item.available)
    vocabulary = load_words()
    answer, games = TermoGame.create_shared_games(len(available))
    results: list[EngineRunResult] = []

    for definition, game in zip(available, games):
        session = definition.create_session(vocabulary)
        results.append(run_engine_game(game, session))

    comparison = tuple(results)
    console.print(build_comparison_table(comparison))
    console.print(Panel(f"Palavra compartilhada: {answer}", border_style="magenta"))
    return comparison
