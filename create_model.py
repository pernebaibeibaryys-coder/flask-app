import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Қарапайым модель жасау
model = Sequential([
    Dense(16, activation='relu', input_shape=(1,)),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='mse')

# Жалған деректермен үйрету (модель файлын жасау үшін)
X = np.random.randint(1, 100, size=(200, 1)).astype(float)
y = (X / 100).astype(float)

model.fit(X, y, epochs=10, verbose=1)

# Модельді сақтау
model.save('interface_hierarchy_model.h5')
print("Модель сақталды!")