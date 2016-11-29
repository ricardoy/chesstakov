import argparse
import h5py
import os.path
import keras
from model import generate_autoencoder


class LossHistory(keras.callbacks.Callback):
    def __init__(self):
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(logs)


def train(input_file, output_directory, log_file):
    full_autoencoder, autoencoder = generate_autoencoder()
    full_autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')

    history = LossHistory()

    output_filepath = os.path.join(output_directory, 'model.epoch_{epoch:03d}.loss_{val_loss:.4f}.h5')
    checkpoint = keras.callbacks.ModelCheckpoint(output_filepath, monitor='val_loss', verbose=0,
                                                 save_best_only=False, save_weights_only=False, mode='auto')

    with h5py.File(input_file) as h5:
        X_train = h5.get('chess/X_train')
        X_test = h5.get('chess/X_test')

        full_autoencoder.fit(X_train, X_train,
                             nb_epoch=300,
                             batch_size=256,
                             shuffle='batch',
                             verbose=2,
                             validation_data=(X_test, X_test),
                             callbacks=[history, checkpoint])

        with open(log_file, 'w') as f:
            for x in history.logs:
                f.write(str(x))
                f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Autoencoder trainer')
    parser.add_argument('-input', type=str, help='HDF5 input file')
    parser.add_argument('-output', type=str, help='Directory where models will be saved')
    parser.add_argument('-log', type=str, help='Log file')

    args = parser.parse_args()

    train(args.input, args.output, args.log)
