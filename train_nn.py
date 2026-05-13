from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam
import numpy as np


# Пример генерации данных
def generate_data():
    # Для примера генерируем случайные данные
    X = np.random.rand(100, 10)  # 100 примеров, 10 признаков
    y = np.random.randint(2, size=(100, 1))  # 100 меток классов (0 или 1)
    return X, y


def create_model(input_shape):
    model = Sequential()
    model.add(Flatten(input_shape=input_shape))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    return model


# Пример использования
if __name__ == "__main__":
    X, y = generate_data()
    model = create_model((10,))
    model.fit(X, y, epochs=10, batch_size=8)
    model.save('interface_hierarchy_model.h5')
