import h5py
import sys
import os
from keras.layers import Input, Dense
from keras.models import Model


encoding_dim = 100

chess_board = Input(shape=(773,))
encoded1 = Dense(600, activation='relu')(chess_board)
encoded2 = Dense(400, activation='relu')(encoded1)
encoded3 = Dense(200, activation='relu')(encoded2)
encoded4 = Dense(encoding_dim, activation='relu')(encoded3)
decoded1 = Dense(200, activation='relu')(encoded4)
decoded2 = Dense(400, activation='relu')(decoded1)
decoded3 = Dense(600, activation='relu')(decoded2)
decoded4 = Dense(773, activation='sigmoid')(decoded3)

autoencoder = Model(input=chess_board, output=decoded4)

# this model maps an input to its encoded representation
encoder = Model(input=chess_board, output=encoded4)

autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')


def autoencoder_train(input_file, model_file):
    with h5py.File(input_file) as h5:
        X_white = h5.get('chess/X_white')
        X_black = h5.get('chess/X_black')

        autoencoder.fit(X_white, X_white,
                        nb_epoch=10,
                        batch_size=256,
                        shuffle='batch',
                        validation_data=(X_black, X_black))

        encoder.save(model_file)


def train(input_directory, output_directory):
    total_steps = 1
    for f in os.listdir(input_directory):
        if not f.lower().endswith('.h5'):
            continue
        input_file = os.path.join(input_directory, f)
        model_file = os.path.join(output_directory, '{}.h5'.format(total_steps))
        autoencoder_train(input_file, model_file)
        total_steps = total_steps + 1


if __name__ == '__main__':
    if (len(sys.argv) < 3):
        print '$ parser.py <input directory> <output directory>'
        sys.exit(-1)
    train(sys.argv[1], sys.argv[2])
