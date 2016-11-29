import sys
import os
import chess
import chess.pgn
import numpy as np
import random
import h5py
import multiprocessing


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
            if game is None:
                continue
            if game.headers['Result'] == '1-0':
                return (chess.WHITE, self._get_n_random_states(game, 10))
            else:
                return (chess.BLACK, self._get_n_random_states(game, 10))
        return (None, None)

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
            if total_pieces == previous_total_pieces:
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


def position_to_vector(board):
    """Converts a board into int8 list.

    For each of the 64 squares, there is a one-hot representation
    for the following 7 fields:
        Color: if there is a White piece
        Pawn
        Knight
        Bishop
        Rook
        Queen
        King

    The last 5 positions are:
        Turn: if White is playing
        White can castle kingside
        White can castle queenside
        Black can castle kingside
        Black can castle queenside
    """
    x = np.zeros(768 + 5, dtype=np.bool)
    for i in range(0, 64):
        piece = board.piece_at(i)
        if piece is not None:
            base_offset = i * 7
            if piece.color == chess.WHITE:
                x[base_offset] = 1
            if piece.piece_type == chess.PAWN:
                x[base_offset + 1] = 1
            elif piece.piece_type == chess.KNIGHT:
                x[base_offset + 2] = 1
            elif piece.piece_type == chess.BISHOP:
                x[base_offset + 3] = 1
            elif piece.piece_type == chess.ROOK:
                x[base_offset + 4] = 1
            elif piece.piece_type == chess.QUEEN:
                x[base_offset + 5] = 1
            elif piece.piece_type == chess.KING:
                x[base_offset + 6] = 1
            else:
                raise Exception('invalid piece type {}'.format(piece))

    if (board.turn == chess.WHITE):
        x[768] = 1
    if (board.has_kingside_castling_rights(chess.WHITE)):
        x[769] = 1
    if (board.has_queenside_castling_rights(chess.WHITE)):
        x[770] = 1
    if (board.has_kingside_castling_rights(chess.BLACK)):
        x[771] = 1
    if (board.has_queenside_castling_rights(chess.BLACK)):
        x[772] = 1

    return x


def parse_all(input_dir, output_dir):
    files = []
    for f in os.listdir(input_dir):
        if not f.lower().endswith('.pgn'):
            continue
        input_file = os.path.join(input_dir, f)
        output_file = os.path.join(output_dir, '{}.h5'.format(f))
        files.append((input_file, output_file))

    pool = multiprocessing.Pool()
    pool.map(parse_aux, files)


def parse_aux(files):
    return parse(*files)


def parse(input_file, output_file):
    if os.path.isfile(output_file):
        print 'Output file {} already processed.'.format(output_file)
        return
    print '<a:{} b:{}>'.format(input_file, output_file)
    temp_file = '{}.temp'.format(output_file)
    h5 = h5py.File(temp_file, 'w')
    h5_group = h5.create_group('chess')

    idx_white = 0
    white_maximum_size = 15000
    X_white = h5_group.create_dataset('X_white', (white_maximum_size, 768 + 5), chunks=True, maxshape=(None, 768 + 5), dtype=np.bool)

    idx_black = 0
    black_maaximum_size = 15000
    X_black = h5_group.create_dataset('X_black', (black_maaximum_size, 768 + 5), chunks=True, maxshape=(None, 768 + 5), dtype=np.bool)

    it = GamePositionsIterator(input_file)
    while True:
        winner, positions = it.random_positions()
        if (positions is None):
            break
        for position in positions:
            x = position_to_vector(position.board())
            if winner == chess.WHITE:
                if idx_white + 1 > white_maximum_size:
                    white_maximum_size = white_maximum_size * 2
                    X_white.resize(size=white_maximum_size, axis=0)
                X_white[idx_white] = x
                idx_white = idx_white + 1
            else:
                if idx_black + 1 > black_maaximum_size:
                    black_maaximum_size = black_maaximum_size * 2
                    X_black.resize(size=black_maaximum_size, axis=0)
                X_black[idx_black] = x
                idx_black = idx_black + 1

    X_white.resize(size=idx_white, axis=0)
    X_black.resize(size=idx_black, axis=0)

    h5.close()

    os.rename(temp_file, output_file)


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print '$ parser.py <input directory> <output directory>'
        sys.exit(-1)
    parse_all(sys.argv[1], sys.argv[2])
