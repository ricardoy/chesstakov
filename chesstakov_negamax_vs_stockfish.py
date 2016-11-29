import chess
import chess.uci
import random
import numpy as np
import sys
from parser import position_to_vector
from keras.models import load_model


CHECKMATE_SCORE = 10
MAX_DEPTH = 3


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


def compare_positions(model, p1, p2):
    X1 = np.array([p1])
    X2 = np.array([p2])

    r = model.predict(X1, X2)

    if (r[0][0] > 0.5):
        return 0
    else:
        return 1


def negamax_base(model, board):
    base_position = position_to_vector(board)
    alpha = float('-inf')
    beta = float('inf')
    score, move = negamax(model, base_position, board, MAX_DEPTH, alpha, beta, 0)
    return move


def negamax(model, base_position, board, depth, alpha, beta, color):
    moves = []
    X = []
    for move in board.legal_moves:
        moves.append(str(move))
        board.push(chess.Move.from_uci(str(move)))
        X.append(position_to_vector(board))
        board.pop()

    if (len(X) <= 0):
        return Exception(''), Exception()

    X_base = np.repeat([base_position], len(X), axis=0)

    scores = model.predict([np.array(X), X_base])
    scores = scores[:, color]

    for i, move in enumerate(moves):
        board.push(chess.Move.from_uci(move))
        if board.is_checkmate():
            scores[i] = CHECKMATE_SCORE
        board.pop()

    child_nodes = sorted(zip(scores, moves), reverse=True)

    best_value = float('-inf')
    best_move = None

    for score, move in child_nodes:
        if depth == 1 or score == CHECKMATE_SCORE:
            value = score
        else:
            board.push(chess.Move.from_uci(move))
            neg_value, _ = negamax(model, base_position, board, depth - 1, -alpha, -beta, 1 - color)
            value = -neg_value
            board.pop()

        if value > best_value:
            best_value = value
            best_move = move

        if value > alpha:
            alpha = value

        if alpha > beta:
            break

    return best_value, best_move


def main(model_filename):
    engine = chess.uci.popen_engine("/usr/games/stockfish")
    engine.uci
    chesstakov = load_model(model_filename)
    white = .0
    black = .0
    tie = .0
    while True:
        board = chess.Board()
        turn = chess.WHITE
        number_turns = 0
        while (not board.result() != '*'):
            if (turn == chess.WHITE):
                number_turns = number_turns + 1
                board.push(chess.Move.from_uci(negamax_base(chesstakov, board)))
                turn = chess.BLACK
            else:
                engine.position(board)
                board.push(engine.go(depth=1).bestmove)
                turn = chess.WHITE

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
    else:
        print 'Parameter model is obligatory.'
