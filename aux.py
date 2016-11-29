import h5py
import numpy as np
from tqdm import tqdm

FEATURE_DIMENSION = 773


def load_chess_dataset_into_memory(file):
    h5 = h5py.File(file, 'r')
    white = h5.get('chess/X_white')
    black = h5.get('chess/X_black')

    black_size = black.shape[0]
    white_size = white.shape[0]

    white_ = np.zeros((white_size, 773), dtype=np.bool)
    black_ = np.zeros((black_size, 773), dtype=np.bool)

    print 'Loading positions from white winner games'
    for i in tqdm(range(0, white_size)):
        white_[i] = np.copy(white[i])

    print 'Loading positions from black winner games'
    for i in tqdm(range(0, black_size)):
        black_[i] = np.copy(black[i])

    h5.close()

    return white_, white_size, black_, black_size


def _stratified_left_right_winner(size):
    result = np.zeros(size, dtype=np.bool)
    for i in range(int(size / 2), size):
        result[i] = 1
    return np.random.permutation(result)


class ChessDatasetGenerator:
    def __init__(self):
        self.black = None
        self.white = None
        self.black_size = -1
        self.white_size = -1

    def init(self, file):
        self.white, self.white_size, self.black, self.black_size = load_chess_dataset_into_memory(file)

    def generate_dataset(self, size):
        if size > self.white_size or size > self.black_size:
            raise Exception('erro')

        X1 = np.zeros((size, FEATURE_DIMENSION), dtype=np.bool)
        X2 = np.zeros((size, FEATURE_DIMENSION), dtype=np.bool)
        y = np.zeros((size, 2), dtype=np.bool)

        white_idx = np.random.permutation(range(0, self.white_size))
        black_idx = np.random.permutation(range(0, self.black_size))

        winner = _stratified_left_right_winner(size)

        for i in range(0, size):
            if (winner[i]):
                X1[i] = self.white[white_idx[i]]
                X2[i] = self.black[black_idx[i]]
                y[i] = [1, 0]
            else:
                X1[i] = self.black[black_idx[i]]
                X2[i] = self.white[white_idx[i]]
                y[i] = [0, 1]

        return X1, X2, y
