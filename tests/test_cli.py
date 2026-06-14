import io
import unittest
from unittest.mock import Mock, patch

from rich.console import Console

from game.cli import cli, cli_views, game_modes
from game.cli.engine_session import EngineDefinition
from game.feedback import LetterFeedback
from game.termo import GameState, GuessResult, TermoGame


def make_console() -> Console:
    return Console(
        file=io.StringIO(),
        force_terminal=True,
        color_system="truecolor",
        width=100,
        record=True,
    )


def render_text(renderable) -> str:
    console = make_console()
    console.print(renderable)
    return console.export_text()


class TermoCliTests(unittest.TestCase):
    def make_game(self) -> TermoGame:
        with (
            patch("game.termo.load_words", return_value=("TERMO", "AAAAA")),
            patch("game.termo.random.choice", return_value="TERMO"),
        ):
            return TermoGame()

    def test_build_tile_applies_feedback_style(self) -> None:
        tile = cli_views.build_tile("A", LetterFeedback.CORRECT)

        self.assertEqual(tile.plain, " A ")
        self.assertIsNotNone(tile.style)
        self.assertIn("green", str(tile.style))

    def test_build_board_always_renders_six_rows(self) -> None:
        state = GameState(
            history=(
                GuessResult(
                    guess="ABCDE",
                    feedback=(
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                    ),
                ),
            ),
            attempts_remaining=5,
            won=False,
            lost=False,
            over=False,
        )

        output = render_text(cli_views.build_board(state))
        self.assertGreaterEqual(len(output.splitlines()), 6)

    def test_collect_wrong_letters_keeps_unique_order(self) -> None:
        state = GameState(
            history=(
                GuessResult(
                    guess="ABCDE",
                    feedback=(
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                    ),
                ),
                GuessResult(
                    guess="AFGHI",
                    feedback=(
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                    ),
                ),
            ),
            attempts_remaining=4,
            won=False,
            lost=False,
            over=False,
        )

        self.assertEqual(
            cli_views.collect_wrong_letters(state),
            ("A", "B", "C", "D", "E", "F", "G", "H", "I"),
        )

    def test_wrong_letters_panel_displays_title_and_letters(self) -> None:
        state = GameState(
            history=(
                GuessResult(
                    guess="ABCDE",
                    feedback=(
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                        LetterFeedback.WRONG,
                    ),
                ),
            ),
            attempts_remaining=5,
            won=False,
            lost=False,
            over=False,
        )

        output = render_text(cli_views.build_wrong_letters_panel(state))
        self.assertIn("Letras usadas", output)
        self.assertIn("Letras ausentes", output)
        self.assertIn("A", output)
        self.assertIn("E", output)

    def test_menu_inicia_jogo_e_sai(self) -> None:
        console = make_console()
        inputs = iter(["5"])

        with patch("game.cli.cli.play_manual_game") as play_mock:
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        play_mock.assert_not_called()
        self.assertIn("Jogo finalizado!", console.export_text())

    def test_opcao_invalida_solicita_nova_escolha(self) -> None:
        console = make_console()
        inputs = iter(["9", "5"])

        with patch("game.cli.cli.play_manual_game") as play_mock:
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        play_mock.assert_not_called()
        self.assertIn("Opção inválida", console.export_text())

    def test_engine_menu_blocks_unavailable_engine(self) -> None:
        console = make_console()
        inputs = iter(["2", "3", "5", "5"])

        cli.run_cli(console=console, input_function=lambda _: next(inputs))

        output = console.export_text()
        self.assertIn("Escolha um motor", output)
        self.assertIn("Naive Bayes", output)
        self.assertNotIn("Naive Bayes (indisponível)", output)
        self.assertIn("Model Checking (indisponível)", output)
        self.assertIn("ainda não está disponível", output)

    def test_engine_menu_runs_available_engine_mode(self) -> None:
        console = make_console()
        inputs = iter(["2", "1", "1", "3", "5", "5"])

        with patch("game.cli.cli.play_assisted_game") as assisted_mock:
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        assisted_mock.assert_called_once()

    def test_compare_engines_runs_from_main_menu(self) -> None:
        console = make_console()
        inputs = iter(["3", "5"])

        with (
            patch("game.cli.cli.compare_engines") as compare_mock,
            patch("game.cli.cli.pause"),
        ):
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        compare_mock.assert_called_once_with(console)

    def test_evaluation_runs_from_main_menu(self) -> None:
        console = make_console()
        inputs = iter(["4", "5"])
        evaluation_mock = Mock()

        with patch("game.cli.cli.pause") as pause_mock:
            cli.run_cli(
                console=console,
                input_function=lambda _: next(inputs),
                evaluation_function=evaluation_mock,
            )

        evaluation_mock.assert_called_once_with()
        pause_mock.assert_called_once()

    def test_evaluation_without_callback_shows_unavailable_message(self) -> None:
        console = make_console()
        inputs = iter(["4", "5"])

        with patch("game.cli.cli.pause"):
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        self.assertIn(
            "avaliação dos motores não está disponível",
            console.export_text(),
        )

    def test_invalid_guess_does_not_consume_turn(self) -> None:
        game = self.make_game()
        console = make_console()
        inputs = iter(["ABC", "TERMO", ""])

        with patch("game.cli.game_modes.TermoGame", return_value=game):
            result = game_modes.play_manual_game(
                console=console,
                input_function=lambda _: next(inputs),
            )

        self.assertTrue(result)
        self.assertEqual(len(game.state.history), 1)
        self.assertIn("de 5 letras", console.export_text())

    def test_play_manual_game_rejects_guess_outside_dataset(self) -> None:
        game = self.make_game()
        console = make_console()
        inputs = iter(["ABCDE", "TERMO", ""])

        with patch("game.cli.game_modes.TermoGame", return_value=game):
            result = game_modes.play_manual_game(
                console=console,
                input_function=lambda _: next(inputs),
            )

        self.assertTrue(result)
        self.assertEqual(len(game.state.history), 1)
        self.assertIn("não pertence ao dataset", console.export_text())

    def test_play_manual_game_reveals_answer_after_loss(self) -> None:
        game = self.make_game()
        console = make_console()
        inputs = iter(["AAAAA", "AAAAA", "AAAAA", "AAAAA", "AAAAA", "AAAAA", ""])

        with patch("game.cli.game_modes.TermoGame", return_value=game):
            result = game_modes.play_manual_game(
                console=console,
                input_function=lambda _: next(inputs),
            )

        self.assertTrue(result)
        self.assertTrue(game.state.over)
        self.assertTrue(game.state.lost)
        self.assertIn("A resposta era: TERMO", console.export_text())

    def test_automatic_game_displays_metrics(self) -> None:
        class WinningEngine:
            _possible_answers = ["TERMO"]

            def make_guess(self, state, vocabulary):
                return "TERMO"

        definition = EngineDefinition("Teste", WinningEngine)
        game = self.make_game()
        console = make_console()

        with (
            patch("game.cli.game_modes.TermoGame", return_value=game),
            patch(
                "game.cli.game_modes.load_words",
                return_value=("TERMO", "AAAAA"),
            ),
        ):
            result = game_modes.play_automatic_game(console, definition)

        output = console.export_text()
        self.assertEqual(result.status, "Vitória")
        self.assertEqual(result.attempts, 1)
        self.assertIn("Tempo total", output)
        self.assertIn("Tentativas: 1", output)

    def test_automatic_game_pauses_between_attempts(self) -> None:
        class TwoGuessEngine:
            _possible_answers = ["AAAAA", "TERMO"]

            def __init__(self):
                self.guesses = iter(("AAAAA", "TERMO"))

            def make_guess(self, state, vocabulary):
                return next(self.guesses)

        definition = EngineDefinition("Teste", TwoGuessEngine)
        game = self.make_game()
        console = make_console()
        pauses: list[str] = []

        with (
            patch("game.cli.game_modes.TermoGame", return_value=game),
            patch(
                "game.cli.game_modes.load_words",
                return_value=("TERMO", "AAAAA"),
            ),
        ):
            result = game_modes.play_automatic_game(
                console,
                definition,
                input_function=lambda prompt: pauses.append(prompt) or "",
            )

        self.assertEqual(result.status, "Vitória")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(pauses, [""])

    def test_comparison_continues_when_engine_fails(self) -> None:
        class WinningEngine:
            _possible_answers = ["TERMO"]

            def make_guess(self, state, vocabulary):
                return "TERMO"

        class FailingEngine:
            _possible_answers = []

            def make_guess(self, state, vocabulary):
                raise ValueError("falha planejada")

        definitions = (
            EngineDefinition("Vencedor", WinningEngine),
            EngineDefinition("Falha", FailingEngine),
        )
        games = (self.make_game(), self.make_game())
        console = make_console()

        with (
            patch("game.cli.game_modes.ENGINE_REGISTRY", definitions),
            patch(
                "game.cli.game_modes.load_words",
                return_value=("TERMO", "AAAAA"),
            ),
            patch(
                "game.cli.game_modes.TermoGame.create_shared_games",
                return_value=("TERMO", games),
            ),
        ):
            results = game_modes.compare_engines(console)

        self.assertEqual(results[0].status, "Vitória")
        self.assertEqual(results[1].status, "Erro")
        self.assertIn("Palavra compartilhada: TERMO", console.export_text())

    def test_ctrl_c_exits_gracefully(self) -> None:
        console = make_console()

        with patch("game.cli.cli.show_main_menu"):
            result = cli.run_cli(
                console=console,
                input_function=lambda _: (_ for _ in ()).throw(KeyboardInterrupt),
            )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
