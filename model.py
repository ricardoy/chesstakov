from keras.layers import Input, Dense
from keras.models import Model


def generate_autoencoder():
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

    full_autoencoder = Model(input=chess_board, output=decoded4)
    autoencoder = Model(input=chess_board, output=encoded4)

    return (full_autoencoder, autoencoder)


def generate_encoder():
    autoencoder, encoder = generate_autoencoder()
    return encoder
