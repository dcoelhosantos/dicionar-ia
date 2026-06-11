import io
import unittest
from unittest.mock import patch

from rich.console import Console

from game import cli
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
        with patch("game.termo.load_words", return_value=("TERMO",)):
            return TermoGame()

    def test_build_tile_applies_feedback_style(self) -> None:
        tile = cli.build_tile("A", LetterFeedback.CORRECT)

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

        output = render_text(cli.build_board(state))
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

        self.assertEqual(cli.collect_wrong_letters(state), ("A", "B", "C", "D", "E", "F", "G", "H", "I"))

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

        output = render_text(cli.build_wrong_letters_panel(state))
        self.assertIn("Letras usadas", output)
        self.assertIn("Letras ausentes", output)
        self.assertIn("A", output)
        self.assertIn("E", output)

    def test_menu_inicia_jogo_e_sai(self) -> None:
        console = make_console()
        inputs = iter(["2"])

        with patch("game.cli.play_manual_game") as play_mock:
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        play_mock.assert_not_called()
        self.assertIn("Até a próxima!", console.export_text())

    def test_opcao_invalida_solicita_nova_escolha(self) -> None:
        console = make_console()
        inputs = iter(["9", "2"])

        with patch("game.cli.play_manual_game") as play_mock:
            cli.run_cli(console=console, input_function=lambda _: next(inputs))

        play_mock.assert_not_called()
        self.assertIn("Opção inválida", console.export_text())

    def test_play_manual_game_handles_invalid_guess_without_consuming_turn(self) -> None:
        game = self.make_game()
        console = make_console()
        inputs = iter(["ABC", "TERMO", ""])

        with patch("game.cli.TermoGame", return_value=game):
            result = cli.play_manual_game(console=console, input_function=lambda _: next(inputs))

        self.assertTrue(result)
        self.assertEqual(len(game.state.history), 1)
        self.assertIn("de 5 letras", console.export_text())

    def test_play_manual_game_reveals_answer_after_loss(self) -> None:
        game = self.make_game()
        console = make_console()
        inputs = iter(["AAAAA", "AAAAA", "AAAAA", "AAAAA", "AAAAA", "AAAAA", ""])

        with patch("game.cli.TermoGame", return_value=game):
            result = cli.play_manual_game(console=console, input_function=lambda _: next(inputs))

        self.assertTrue(result)
        self.assertTrue(game.state.over)
        self.assertTrue(game.state.lost)
        self.assertIn("A resposta era: TERMO", console.export_text())

    def test_ctrl_c_exits_gracefully(self) -> None:
        console = make_console()

        with patch("game.cli.show_main_menu"):
            result = cli.run_cli(
                console=console,
                input_function=lambda _: (_ for _ in ()).throw(KeyboardInterrupt),
            )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
