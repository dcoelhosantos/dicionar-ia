from collections.abc import Callable

from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from game.feedback import LetterFeedback
from game.termo import GameState, GuessResult, TermoGame

InputFunction = Callable[[str], str]

FEEDBACK_STYLES = {
    LetterFeedback.CORRECT: "bold white on green",
    LetterFeedback.PRESENT: "bold black on yellow",
    LetterFeedback.WRONG: "bold white on grey37",
}


def build_tile(letter: str = " ", feedback: LetterFeedback | None = None) -> Text:
    style = FEEDBACK_STYLES.get(feedback, "bold white on grey15")
    return Text(f" {letter} ", style=style, justify="center")


def _build_result_tiles(result: GuessResult) -> list[Text]:
    tiles: list[Text] = []

    for letter, feedback in zip(result.guess, result.feedback):
        tiles.append(build_tile(letter, feedback))

    return tiles


def build_board(state: GameState) -> Table:
    board = Table.grid(padding=(0, 1))
    board.expand = False

    for result in state.history:
        board.add_row(*_build_result_tiles(result))

    remaining_rows = len(state.history)
    while remaining_rows < 6:
        board.add_row(
            build_tile(),
            build_tile(),
            build_tile(),
            build_tile(),
            build_tile(),
        )
        remaining_rows += 1

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
        tiles.add_row(*(build_tile(letter, LetterFeedback.WRONG) for letter in wrong_letters))
        content = Group(Text("Letras ausentes:", style="bold"), tiles)
    else:
        content = Text("Nenhuma letra ausente ainda.", style="dim")

    return Panel(
        content,
        title="Letras usadas",
        border_style="grey50",
        padding=(1, 1),
    )


def build_game_view(state: GameState, message: str | None = None) -> Panel:
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
        title="Tabuleiro",
        border_style="cyan",
        padding=(1, 2),
    )

    content = Group(
        Text("Dicionar-IA", style="bold magenta", justify="center"),
        Text("Digite uma palavra de 5 letras.", style="dim", justify="center"),
        Columns([board_panel, build_wrong_letters_panel(state)], expand=True, padding=(1, 2)),
    )

    if message:
        content = Group(content, Text(message, style="bold red", justify="center"))

    return Panel(content, box=box.ROUNDED, padding=(1, 1))


def show_main_menu(console: Console) -> None:
    menu = Panel(
        Group(
            Text("Dicionar-IA", style="bold magenta", justify="center"),
            Text("1. Jogar", style="bold green"),
            Text("2. Sair", style="bold red"),
        ),
        title="Menu principal",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(menu)


def play_manual_game(
    console: Console,
    input_function: InputFunction = input,
) -> bool:
    game = TermoGame()

    while True:
        state = game.state
        console.print(build_game_view(state))

        if state.over:
            if state.won:
                console.print(Panel("Você venceu!", border_style="green"))
            else:
                console.print(Panel(f"A resposta era: {game.answer}", border_style="red"))

            console.print("Pressione Enter para voltar ao menu.")
            try:
                input_function("")
            except (EOFError, KeyboardInterrupt):
                return True

            return True

        try:
            guess = input_function("Digite uma palavra: ")
        except EOFError:
            return False
        except KeyboardInterrupt:
            return False

        try:
            game.make_guess(guess)
        except ValueError as error:
            console.print(Panel(str(error), border_style="red"))


def run_cli(
    console: Console | None = None,
    input_function: InputFunction = input,
) -> None:
    console = console or Console()

    while True:
        try:
            show_main_menu(console)
            choice = input_function("Escolha uma opção: ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        if choice == "1":
            try:
                play_manual_game(console, input_function=input_function)
            except KeyboardInterrupt:
                break
            continue

        if choice == "2":
            console.print("Jogo finalizado!")
            break

        console.print(Panel("Opção inválida. Tente novamente.", border_style="red"))
