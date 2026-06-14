from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel

from game.cli.cli_views import (
    show_engine_menu,
    show_engine_mode_menu,
    show_main_menu,
)
from game.cli.engine_session import ENGINE_REGISTRY, EngineDefinition
from game.cli.game_modes import (
    compare_engines,
    pause,
    play_assisted_game,
    play_automatic_game,
    play_manual_game,
)

InputFunction = Callable[[str], str]


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
