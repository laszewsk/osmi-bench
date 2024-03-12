from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Reshape


def build_model(input_shape, af='elu'):

    input_layer = Input(shape=input_shape, name='inputs')
    x = LSTM(256, activation=af, return_sequences=True)(input_layer)
    x = LSTM(256, activation=af, return_sequences=True)(x)
    x = LSTM(256, activation=af, return_sequences=True)(x)
    x = LSTM(256, activation=af, return_sequences=False)(x)
    x = Dense(256, activation=af)(x)
    x = Dense(128, activation=af)(x)
    x = Dense(24, activation='linear')(x)
    outputs = Reshape((2, 12), name='outputs')(x)

    return Model(inputs=[input_layer], outputs=[outputs])
