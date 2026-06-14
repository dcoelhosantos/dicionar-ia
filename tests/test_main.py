import unittest
from unittest.mock import patch

import main


class MainTestCase(unittest.TestCase):
    def test_run_evaluation_includes_all_available_engines(self):
        results = {
            "num_games": 50,
            "win_rate": 100.0,
            "avg_attempts": 1.0,
            "time_seconds": 0.1,
        }

        with (
            patch("main.load_words", return_value=("TERMO",)),
            patch("main.Evaluator") as evaluator_mock,
            patch("builtins.print"),
        ):
            evaluator_mock.return_value.run.return_value = results

            main.run_evaluation()

        evaluated_engines = [
            call.kwargs["engine"].__class__.__name__
            for call in evaluator_mock.call_args_list
        ]
        self.assertEqual(
            evaluated_engines,
            ["NaiveBayesEngine", "MinimaxEngine", "DpllEngine"],
        )


if __name__ == "__main__":
    unittest.main()
