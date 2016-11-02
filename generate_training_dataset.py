import h5py
import sys
import numpy as np
from tqdm import tqdm


def create_dataset(output_filename, dimension=(None, None)):
    h5 = h5py.File(output_filename, 'w')
    group = h5.create_group('chess')
    X1 = group.create_dataset('X1', dimension, dtype='b')
    X2 = group.create_dataset('X2', dimension, dtype='b')
    y = group.create_dataset('y', (dimension[0], 2))
    return h5, X1, X2, y


def group_permutation(n, k):
    a = range(0, n)
    print 'Generating permutations of size {}'.format(n)
    for i in tqdm(range(0, n)):
        left = k * int(i / k)
        right = min(n, left + k)
        j = np.random.randint(left, right)
        (a[i], a[j]) = (a[j], a[i])
    return a


def main(input_filename, output_filename):
    input_h5 = h5py.File(input_filename, 'r')
    X_white = input_h5.get('chess/X_white')
    X_black = input_h5.get('chess/X_black')
    white_limit = X_white.shape[0]
    black_limit = X_black.shape[0]
    limit = min(white_limit, black_limit)
    white_indexes = group_permutation(limit, 5000)
    black_indexes = group_permutation(limit, 5000)
    output_h5, X1, X2, y = create_dataset(output_filename, (limit, 768 + 5))
    for i in tqdm(range(0, limit)):
        if (np.random.randint(0, 2) == 0):
            X1[i] = X_white[white_indexes[i]]
            X2[i] = X_black[black_indexes[i]]
            y[i] = [1, 0]
        else:
            X1[i] = X_black[black_indexes[i]]
            X2[i] = X_white[white_indexes[i]]
            y[i] = np.array([0, 1])

    input_h5.close()
    output_h5.close()


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
