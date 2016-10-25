import sys
import os
import chess, chess.pgn
import random
from tqdm import tqdm


class GamePositionsIterator:
    def __init__(self, input_file):
        self.fh = open(input_file)
        self.end = False

    def has_finished(self):
        return self.end

    """Returns at most 10 random positions from a game

        Returns: list of pairs:
            winner: chess.WHITE or chess.BLACK
            position: board features
    """
    def random_positions(self):
        while (not self.end):
            game = self._next_game_no_draw()
            if (game is None):
                continue
            return self._get_n_random_states(game, 10)
        return None

    def _count_pieces(self, game_state):
        board = game_state.board()
        total_pieces = 0
        for i in range(0, 64):
            p = board.piece_at(i)
            if (p is not None):
                total_pieces = total_pieces + 1
        return total_pieces

    def _get_n_random_states(self, game, n):
        positions = []
        previous_game_state = game.end()
        previous_total_pieces = self._count_pieces(previous_game_state)
        game_state = previous_game_state.parent
        while game_state is not None:
            if (game_state.board().fullmove_number <= 5):
                break
            total_pieces = self._count_pieces(game_state)
            if game_state.board().turn == chess.BLACK and \
                    total_pieces == previous_total_pieces:
                positions.append(game_state)
            previous_game_state = game_state
            previous_total_pieces = total_pieces
            game_state = game_state.parent
        return random.sample(positions, min(n, len(positions)))

    """Returns the next game where the result is not a draw
    """
    def _next_game_no_draw(self):
        while True:
            game = chess.pgn.read_game(self.fh)
            if (game is None):
                self.fh.close()
                self.end = True
                return None
            result = game.headers['Result']
            if result == '1-0' or result == '0-1':
                return game


def position_to_vector(position):
    return str(position)


def parse(input_dir, output_file):
    files = []
    for f in os.listdir(input_dir):
        if not f.lower().endswith('.pgn'):
            continue
        path = os.path.join(input_dir, f)
        files.append(path)

    out = open(output_file, 'w')
    for f in files:
        it = GamePositionsIterator(f)
        while True:
            positions = it.random_positions()
            if (positions is None):
                break
            for position in positions:
                out.write(position_to_vector(position))
                out.write('\n')

    out.close()


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print '$ parser.py <directory> <outputfile>'
        sys.exit(-1)
    parse(sys.argv[1], sys.argv[2])
