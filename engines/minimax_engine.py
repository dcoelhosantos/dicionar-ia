import random
from game.termo import GameState

class MinimaxEngine:
    def make_guess(self, state: GameState, vocabulary: tuple[str, ...]) -> str:
        history_words = {result.guess for result in state.history}
        options = [word for word in vocabulary if word not in history_words]

        return random.choice(options)