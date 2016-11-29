import h5py
import sys
from keras.models import load_model


def main(model_filename, test_filename):
    model = load_model(model_filename)

    h5 = h5py.File(test_filename)

    X1 = h5.get('chess/X1')
    X2 = h5.get('chess/X2')
    y_test = h5.get('chess/y')

    y2 = model.predict([X1, X2])

    h5.close()

    ok = 0
    for i in range(0, len(y2)):
        if y2[i][0] > y2[i][1] and y_test[i][0] == 1:
            ok += 1
        elif y_test[i][1] == 1:
            ok += 1
    print ok / float(len(y2))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
