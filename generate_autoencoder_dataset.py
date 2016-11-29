import numpy as np
import h5py
import sys
from tqdm import tqdm
from aux import load_chess_dataset_into_memory


def generate(input_file, training_file, testing_file, training_size, testing_size):
    total_positions = training_size + testing_size
    white, white_size, black, black_size = load_chess_dataset_into_memory(input_file, total_positions)

    if total_positions > min(white_size, black_size):
        print 'Total positions invalid: {}'.format(total_positions)
        print 'Input file has {} positions from white winner games.'.format(white.shape[0])
        print 'Input file has {} positions from black winner games.'.format(black.shape[0])
        sys.exit(-1)

    white_idx = np.random.permutation(range(0, white.shape[0]))
    black_idx = np.random.permutation(range(0, black.shape[0]))

    X_train = np.zeros((2 * training_size, 773), dtype=np.bool)
    X_test = np.zeros((2 * testing_size, 773), dtype=np.bool)

    print 'Generating train (white)'
    for i in tqdm(range(0, training_size)):
        X_train[2 * i] = white[white_idx[i]]

    print 'Generating train (black)'
    for i in tqdm(range(0, training_size)):
        X_train[2 * i + 1] = black[black_idx[i]]

    print 'Generating test (white)'
    for i in tqdm(range(0, testing_size)):
        X_test[2 * i] = white[white_idx[training_size + i]]

    print 'Generating test (black)'
    for i in tqdm(range(0, testing_size)):
        X_test[2 * i + 1] = black[black_idx[training_size + i]]

    print 'Saving data'
    h5 = h5py.File(training_file, 'w')
    group = h5.create_group('chess')
    group.create_dataset('X_train', data=X_train)
    group.create_dataset('X_test', data=X_test)

    h5.close()


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print '$ parser.py <input file> <training file> <testing file> <size training> <size testing>'
        sys.exit(-1)
    generate(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
