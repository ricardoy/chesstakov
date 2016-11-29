import h5py
import sys
from keras.layers import Merge, Dense
from keras.models import load_model, Sequential
from keras.optimizers import SGD


# Loading training dataset
# h5 = h5py.File('/mnt/abobrinhas_new/chess/training_new.h5', 'r')
h5 = h5py.File(sys.argv[1], 'r')
X1 = h5.get('chess/X1')
X2 = h5.get('chess/X2')
y = h5.get('chess/y')

left = Sequential()
left.add(Dense(600, activation='relu', input_dim=773))
left.add(Dense(400, activation='relu'))
left.add(Dense(200, activation='relu'))
left.add(Dense(100, activation='relu'))

right = Sequential()
right.add(Dense(600, activation='relu', input_dim=773))
right.add(Dense(400, activation='relu'))
right.add(Dense(200, activation='relu'))
right.add(Dense(100, activation='relu'))

# Creating DNN structure
merged = Merge([left, right], mode='concat')

final_model = Sequential()
final_model.add(merged)
final_model.add(Dense(2048, activation='relu'))
final_model.add(Dense(2048, activation='relu'))
final_model.add(Dense(2048, activation='relu'))
final_model.add(Dense(2, activation='softmax'))

# optimizer = SGD(momentum=0.00001, nesterov=True)
optimizer = SGD(nesterov=True)
final_model.compile(optimizer=optimizer, loss='binary_crossentropy')

# Train model
# final_model.fit([X1, X2], y, shuffle='batch')
final_model.fit([X1, X2], y, shuffle='batch', verbose=2, nb_epoch=1000)

# Save model
final_model.save('/mnt/abobrinhas_new/chess/final_model.h5')
