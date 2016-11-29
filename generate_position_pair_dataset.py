import argparse
import h5py
from aux import ChessDatasetGenerator


def create_dataset(output_filename, dimension=(None, None)):
    h5 = h5py.File(output_filename, 'w')
    group = h5.create_group('chess')
    X1 = group.create_dataset('X1', dimension, dtype='b')
    X2 = group.create_dataset('X2', dimension, dtype='b')
    y = group.create_dataset('y', (dimension[0], 2))
    return h5, X1, X2, y


def main(input_file, output_file, size):
    gen = ChessDatasetGenerator()
    gen.init(input_file)
    X1, X2, y = gen.generate_dataset(size)
    with h5py.File(output_file, 'w') as h5:
        group = h5.create_group('chess')
        group.create_dataset('X1', data=X1)
        group.create_dataset('X2', data=X2)
        group.create_dataset('y', data=y)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Positions pair dataset generator')
    parser.add_argument('-input', type=str, help='HDF5 input file')
    parser.add_argument('-output', type=str, help='Directory where models will be saved')
    parser.add_argument('-size', type=int, help='Number of pairs')

    args = parser.parse_args()
    main(args.input, args.output, args.size)
