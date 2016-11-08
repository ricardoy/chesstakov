import chess
import random
import numpy as np
import sys
from parser import position_to_vector
from keras.models import load_model
from flask import Flask
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


CHECKMATE_SCORE = 10
TIE = 5
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


class Chesstakov:
    def __init__(self, filename):
        self.board = None
        self.model = load_model(filename)


@app.route('/init')
def init():
    engine.board = chess.Board()
    return ''


@app.route('/generate_move')
def generate_move():
    move = negamax_base(engine.model, engine.board)
    engine.board.push(chess.Move.from_uci(move))
    r = dict()
    r['from'] = move[:2]
    r['to'] = move[2:4]
    r['promotion'] = 'q'
    print engine.board
    check_end()
    return jsonify(**r)


@app.route('/move/<source>/<to>/<promotion>')
def receive_move(source, to, promotion):
    # print '{} {} {}'.format(source, to, promotion)
    # return str(engine.board)
    if promotion == 'undefined':
        promotion = ''
    engine.board.push(chess.Move.from_uci('{}{}{}'.format(source, to, promotion)))
    check_end()
    return ''


def check_end():
    if (engine.board.result() != '*'):
        print engine.board.result()


if __name__ == '__main__':
    engine = Chesstakov(sys.argv[1])
    app.run()
