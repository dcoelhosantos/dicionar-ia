from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from game.cli.engine_session import ENGINE_REGISTRY
from game.feedback import LetterFeedback
from game.termo import GameState, GuessResult, TermoGame

FEEDBACK_STYLES = {
    LetterFeedback.CORRECT: "bold white on green",
    LetterFeedback.PRESENT: "bold black on yellow",
    LetterFeedback.WRONG: "bold white on grey37",
}


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
                Text("3. Comparar motores", style="bold yellow"),
                Text("4. Avaliar Motores", style="bold magenta"),
                Text("5. Sair", style="bold red"),
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


def show_game_result(console: Console, game: TermoGame) -> None:
    if game.state.won:
        message = f"Vitória em {len(game.state.history)} tentativas!"
        console.print(Panel(message, border_style="green"))
    else:
        console.print(Panel(f"A resposta era: {game.answer}", border_style="red"))


def build_comparison_table(results) -> Table:
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
