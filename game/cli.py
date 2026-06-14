from collections.abc import Callable
from dataclasses import dataclass
import time

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from game.engine_session import (
    ENGINE_REGISTRY,
    EngineDefinition,
    EngineSession,
)
from game.feedback import LetterFeedback
from game.termo import GameState, GuessResult, TermoGame, load_words

InputFunction = Callable[[str], str]

FEEDBACK_STYLES = {
    LetterFeedback.CORRECT: "bold white on green",
    LetterFeedback.PRESENT: "bold black on yellow",
    LetterFeedback.WRONG: "bold white on grey37",
}


@dataclass(frozen=True, slots=True)
class EngineRunResult:
    name: str
    status: str
    attempts: int
    elapsed_seconds: float
    error: str | None = None


def build_tile(letter: str = " ", feedback: LetterFeedback | None = None) -> Text:
    style = FEEDBACK_STYLES.get(feedback, "bold white on grey15")
    return Text(f" {letter} ", style=style, justify="center")


def _build_result_tiles(result: GuessResult) -> list[Text]:
    return [
        build_tile(letter, feedback)
        for letter, feedback in zip(result.guess, result.feedback)
    ]


def build_board(state: GameState) -> Table:
    board = Table.grid(padding=(0, 1))
    board.expand = False

    for result in state.history:
        board.add_row(*_build_result_tiles(result))

    for _ in range(len(state.history), 6):
        board.add_row(*(build_tile() for _ in range(5)))

    return board


def build_legend() -> Text:
    legend = Text()
    legend.append("Legenda: ", style="bold")
    legend.append("correta", style=FEEDBACK_STYLES[LetterFeedback.CORRECT])
    legend.append(" | ", style="dim")
    legend.append("presente", style=FEEDBACK_STYLES[LetterFeedback.PRESENT])
    legend.append(" | ", style="dim")
    legend.append("ausente", style=FEEDBACK_STYLES[LetterFeedback.WRONG])
    return legend


def collect_wrong_letters(state: GameState) -> tuple[str, ...]:
    wrong_letters: list[str] = []
    seen: set[str] = set()

    for result in state.history:
        for letter, feedback in zip(result.guess, result.feedback):
            if feedback is LetterFeedback.WRONG and letter not in seen:
                seen.add(letter)
                wrong_letters.append(letter)

    return tuple(wrong_letters)


def build_wrong_letters_panel(state: GameState) -> Panel:
    wrong_letters = collect_wrong_letters(state)

    if wrong_letters:
        tiles = Table.grid(padding=(0, 1))
        tiles.expand = False
        tiles.add_row(
            *(build_tile(letter, LetterFeedback.WRONG) for letter in wrong_letters)
        )
        content = Group(Text("Letras ausentes:", style="bold"), tiles)
    else:
        content = Text("Nenhuma letra ausente ainda.", style="dim")

    return Panel(content, title="Letras usadas", border_style="grey50", padding=(1, 1))


def build_suggestions_panel(
    engine_name: str,
    suggestions: tuple[str, ...],
) -> Panel:
    if suggestions:
        content = Group(
            *(
                Text(f"{index}. {word}", style="bold cyan")
                for index, word in enumerate(suggestions, start=1)
            )
        )
    else:
        content = Text("Nenhuma sugestão disponível.", style="dim")

    return Panel(
        content,
        title=f"Dicas: {engine_name}",
        border_style="magenta",
        padding=(1, 1),
    )


def build_game_view(
    state: GameState,
    message: str | None = None,
    engine_name: str | None = None,
    suggestions: tuple[str, ...] = (),
) -> Panel:
    board_panel = Panel(
        Group(
            Text(
                f"Tentativas restantes: {state.attempts_remaining}",
                style="bold",
                justify="center",
            ),
            build_board(state),
            build_legend(),
        ),
        title="Dicionar-IA",
        border_style="cyan",
        padding=(1, 2),
    )

    side_panels = [build_wrong_letters_panel(state)]
    if engine_name is not None:
        side_panels.append(build_suggestions_panel(engine_name, suggestions))

    content = Group(
        Text("Dicionar-IA", style="bold magenta", justify="center"),
        Text("Digite uma palavra de 5 letras.", style="dim", justify="center"),
        Columns(
            [board_panel, Group(*side_panels)],
            expand=True,
            padding=(1, 2),
        ),
    )

    if message:
        content = Group(content, Text(message, style="bold red", justify="center"))

    return Panel(content, box=box.ROUNDED, padding=(1, 1))


def show_main_menu(console: Console) -> None:
    console.print(
        Panel(
            Group(
                Text("Dicionar-IA", style="bold magenta", justify="center"),
                Text("1. Jogar manualmente", style="bold green"),
                Text("2. Escolher um motor", style="bold cyan"),
                Text("3. Comparar motores", style="bold cyan"),
                Text("4. Sair", style="bold red"),
            ),
            title="Menu principal",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def show_engine_menu(console: Console) -> None:
    options: list[Text] = []
    for index, definition in enumerate(ENGINE_REGISTRY, start=1):
        suffix = "" if definition.available else " (indisponível)"
        style = "bold cyan" if definition.available else "dim"
        options.append(Text(f"{index}. {definition.name}{suffix}", style=style))

    options.append(Text(f"{len(ENGINE_REGISTRY) + 1}. Voltar", style="bold red"))
    console.print(
        Panel(
            Group(*options),
            title="Escolha um motor",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def show_engine_mode_menu(console: Console, engine_name: str) -> None:
    console.print(
        Panel(
            Group(
                Text("1. Modo manual assistido", style="bold green"),
                Text("2. Resolução automática", style="bold cyan"),
                Text("3. Voltar", style="bold red"),
            ),
            title=engine_name,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def pause(console: Console, input_function: InputFunction) -> None:
    console.print("Pressione Enter para continuar.")
    input_function("")


def show_game_result(console: Console, game: TermoGame) -> None:
    if game.state.won:
        message = f"Vitória em {len(game.state.history)} tentativas!"
        console.print(Panel(message, border_style="green"))
    else:
        console.print(Panel(f"A resposta era: {game.answer}", border_style="red"))


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


def build_comparison_table(results: tuple[EngineRunResult, ...]) -> Table:
    table = Table(title="Comparação dos motores", box=box.ROUNDED)
    table.add_column("Motor", style="cyan")
    table.add_column("Resultado")
    table.add_column("Tentativas", justify="right")
    table.add_column("Tempo", justify="right")

    for result in results:
        table.add_row(
            result.name,
            result.status,
            str(result.attempts),
            f"{result.elapsed_seconds:.3f}s",
        )

    return table


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


def run_engine_mode_menu(
    console: Console,
    definition: EngineDefinition,
    input_function: InputFunction,
) -> None:
    while True:
        show_engine_mode_menu(console, definition.name)
        choice = input_function("Escolha uma opção: ").strip()

        if choice == "1":
            play_assisted_game(console, definition, input_function)
            continue
        if choice == "2":
            play_automatic_game(console, definition, input_function)
            continue
        if choice == "3":
            return

        console.print(Panel("Opção inválida. Tente novamente.", border_style="red"))


def run_engine_menu(console: Console, input_function: InputFunction) -> None:
    back_option = str(len(ENGINE_REGISTRY) + 1)

    while True:
        show_engine_menu(console)
        choice = input_function("Escolha uma opção: ").strip()

        if choice == back_option:
            return

        if choice.isdigit() and 1 <= int(choice) <= len(ENGINE_REGISTRY):
            definition = ENGINE_REGISTRY[int(choice) - 1]
            if not definition.available:
                console.print(
                    Panel(
                        f"O motor {definition.name} ainda não está disponível.",
                        border_style="yellow",
                    )
                )
                continue

            run_engine_mode_menu(console, definition, input_function)
            continue

        console.print(Panel("Opção inválida. Tente novamente.", border_style="red"))


def run_cli(
    console: Console | None = None,
    input_function: InputFunction = input,
) -> None:
    console = console or Console()

    while True:
        try:
            show_main_menu(console)
            choice = input_function("Escolha uma opção: ").strip()

            if choice == "1":
                play_manual_game(console, input_function)
            elif choice == "2":
                run_engine_menu(console, input_function)
            elif choice == "3":
                compare_engines(console)
                pause(console, input_function)
            elif choice == "4":
                console.print("Jogo finalizado!")
                return
            else:
                console.print(
                    Panel("Opção inválida. Tente novamente.", border_style="red")
                )
        except (EOFError, KeyboardInterrupt):
            return
