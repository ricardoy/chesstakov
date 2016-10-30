import h5py
import os
import sys
from tqdm import tqdm


def get_count(input_directory):
    total_rows_white = 0
    total_rows_black = 0
    for file in os.listdir(input_directory):
        if file.endswith('.h5'):
            input_file = os.path.join(input_directory, file)
            with h5py.File(input_file, 'r') as h5:
                white = h5.get('chess/X_white')
                black = h5.get('chess/X_black')
                total_rows_white = total_rows_white + white.shape[0]
                total_rows_black = total_rows_black + black.shape[0]
    return total_rows_white, total_rows_black


def main(input_directory, output_file):
    total_rows_white, total_rows_black = get_count(input_directory)

    big_h5 = h5py.File(output_file, 'w')
    group = big_h5.create_group('chess')
    X_white = group.create_dataset('X_white', (total_rows_white, 768 + 5), dtype='b')
    X_black = group.create_dataset('X_black', (total_rows_black, 768 + 5), dtype='b')

    offset_white = 0
    offset_black = 0
    print 'Merging h5 files:'
    for file in tqdm(os.listdir(input_directory)):
        if file.endswith('.h5'):
            input_file = os.path.join(input_directory, file)
            with h5py.File(input_file, 'r') as h5:
                white = h5.get('chess/X_white')
                total_white = white.shape[0]
                X_white[offset_white:offset_white + total_white, :] = white
                offset_white = offset_white + total_white

                black = h5.get('chess/X_black')
                total_black = black.shape[0]
                X_black[offset_black:offset_black + total_black, :] = black
                offset_black = offset_black + total_black
    big_h5.close()


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print '$ parser.py <input directory> <h5 file>'
        sys.exit(-1)
    main(sys.argv[1], sys.argv[2])
