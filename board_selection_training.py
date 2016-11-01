import h5py
from keras.layers import Merge, Dense
from keras.models import load_model, Sequential


# Loading autoencoders
left_autoencoder = load_model('/mnt/abobrinhas_new/chess/output_model/1.h5')
right_autoencoder = load_model('/mnt/abobrinhas_new/chess/output_model/1.h5')
left_autoencoder.name = 'left_autoencoder'
right_autoencoder.name = 'right_autoencoder'


# Loading training dataset
h5 = h5py.File('/mnt/abobrinhas_new/chess/training.h5')
X1 = h5.get('chess/X1')
X2 = h5.get('chess/X2')
y = h5.get('chess/y')

# Creating DNN structure
merged = Merge([left_autoencoder, right_autoencoder], mode='concat')

final_model = Sequential()
final_model.add(merged)
final_model.add(Dense(400, activation='relu'))
final_model.add(Dense(200, activation='relu'))
final_model.add(Dense(100, activation='relu'))
final_model.add(Dense(1, activation='relu'))

final_model.compile(optimizer='adagrad', loss='binary_crossentropy')

# Train model
final_model.fit([X1, X2], y, shuffle='batch', verbose=2)

# Save model
final_model.save('/mnt/abobrinhas_new/chess/final_model.h5')
