import chess
import random
import numpy as np
import h5py
import sys
from parser import position_to_vector
from keras.models import load_model
from tqdm import tqdm


def choose_random_position(board):
    moves = []
    for move in board.legal_moves:
        board.push(chess.Move.from_uci(str(move)))
        if (board.is_checkmate()):
            board.pop()
            return (str(move))
        moves.append(str(move))
        board.pop()
    return random.choice(moves)


def choose_not_so_random_position(model, board):
    moves = dict()
    for move in board.legal_moves:
        board.push(chess.Move.from_uci(str(move)))
        if (board.is_checkmate()):
            board.pop()
            return str(move)
        moves[str(move)] = position_to_vector(board)
        board.pop()

    if len(moves) <= 1:
        return moves.keys()[0]

    X1 = []
    X2 = []
    all_moves = moves.keys()
    for i in range(0, len(all_moves)):
        for j in range(i + 1, len(all_moves)):
            X1.append(moves[all_moves[i]])
            X2.append(moves[all_moves[j]])

    r = model.predict([np.array(X1), np.array(X2)])

    pair_won = np.zeros(len(all_moves), dtype=int)
    k = 0
    for i in range(0, len(all_moves)):
        for j in range(i + 1, len(all_moves)):
            if (r[k][0] > 0.5):
                pair_won[i] = pair_won[i] + 1
            else:
                pair_won[j] = pair_won[j] + 1
            k = k + 1

    best_score = -1
    best_i = -1
    for i in range(0, len(all_moves)):
        if (pair_won[i] > best_score):
            best_score = pair_won[i]
            best_i = i

    return all_moves[best_i]


def main(model_filename):
    chesstakov = load_model(model_filename)
    white = .0
    black = .0
    tie = .0
    while True:
        board = chess.Board()
        turn = chess.WHITE
        number_turns = 0
        while (not board.result() != '*'):
            play = None
            if (turn == chess.WHITE):
                number_turns = number_turns + 1
                play = choose_not_so_random_position(chesstakov, board)
                turn = chess.BLACK
            else:
                play = choose_random_position(board)
                turn = chess.WHITE
            board.push(chess.Move.from_uci(play))

        r = board.result()
        if (r == '1-0'):
            white = white + 1
        elif (r == '0-1'):
            black = black + 1
        else:
            tie = tie + 1

        total = white + black + tie
        print 'white: %d (%.3f) black: %d (%.3f) tie: %d (%.3f)' % \
            (white, (100 * white / total), black, 100 * black / total, tie, 100 * tie / total)


if __name__ == '__main__':
    if (len(sys.argv) == 2):
        main(sys.argv[1])
