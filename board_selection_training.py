import argparse
import h5py
import numpy as np
import model
import keras
import datetime
import os
from keras.layers import Dense, Merge
from keras.optimizers import SGD
from keras.models import Sequential
from keras.models import load_model

from aux import ChessDatasetGenerator


class LossHistory(keras.callbacks.Callback):
    def __init__(self):
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        self.logs.append(logs)


def get_trained_encoder(autoencoder_model_file, temp_dir):
    autoencoder, encoder = model.generate_autoencoder()
    autoencoder.load_weights(autoencoder_model_file)
    encoder.trainable = False
    return encoder


def generate_model(autoencoder_model_file, temp_dir):
    left = get_trained_encoder(autoencoder_model_file, temp_dir)
    right = get_trained_encoder(autoencoder_model_file, temp_dir)

    merged = Merge([left, right], mode='concat')

    model = Sequential()
    model.add(merged)
    model.add(Dense(2048, activation='relu'))
    model.add(Dense(2048, activation='relu'))
    model.add(Dense(2048, activation='relu'))
    model.add(Dense(2, activation='relu'))

    # optimizer = SGD(lr=0.01, nesterov=True)
    optimizer = SGD(lr=0.01)

    model.compile(optimizer=optimizer, loss='categorical_crossentropy')

    return model, left, right


def model_filename(output_directory, validation_loss_value):
    filename = '%s_model_%.10f' % (timestamp(), validation_loss_value)
    return os.path.join(output_directory, filename)


def timestamp():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d_%H:%M')


def main(args):
    if (args.resume is not None):
        model = load_model(args.resume)
    else:
        model, _, _ = generate_model(args.autoencoder, args.tempdir)

    test_dataset = h5py.File(args.test_dataset)
    X1_test = test_dataset.get('chess/X1')
    X2_test = test_dataset.get('chess/X2')
    y_test = test_dataset.get('chess/y')

    dataset_generator = ChessDatasetGenerator()
    dataset_generator.init(args.input)

    history = LossHistory()

    if args.resume is None:
        with open(args.log, 'w') as f:
                f.write('>')
                f.write(str(args))
                f.write('\n')

    for i in range(0, args.epoch):
        X1, X2, y = dataset_generator.generate_dataset(args.training_size)
        model.fit([X1, X2], y,
                  verbose=1,
                  callbacks=[history],
                  validation_data=([X1_test, X2_test], y_test),
                  nb_epoch=1)
        model.optimizer.lr.set_value(model.optimizer.lr.get_value() * np.float32(0.99))

        model.save(model_filename(args.output, history.logs[-1]['val_loss']))

        with open(args.log, 'a') as f:
            f.write(str(history.logs[-1]))
            f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chess trainer')
    parser.add_argument('-input', type=str, help='HDF5 input file')
    parser.add_argument('-output', type=str, help='Directory where models will be saved')
    parser.add_argument('-autoencoder', type=str, help='Autoencoder model file')
    parser.add_argument('-tempdir', type=str, help='Temporary directory')
    parser.add_argument('-log', type=str, help='Log file')
    parser.add_argument('-resume', type=str, help='Existent model file')
    parser.add_argument('-training_size', type=int, help='Training size')
    parser.add_argument('-epoch', type=int, help='Number of epochs')
    parser.add_argument('-test_dataset', type=str, help='Testing dataset file')

    args = parser.parse_args()
    main(args)
