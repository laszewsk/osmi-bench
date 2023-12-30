from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, MaxPooling2D, Dense, Flatten, Cropping2D
from tensorflow.keras.layers import Reshape, Conv2DTranspose, ZeroPadding2D, Conv2D


def build_model(input_shape, af='elu'):

    input_layer = Input(shape=input_shape, name='inputs')
    pg = 'same'
    ks = (3, 3) 
    ps = (2, 2)
    st = (1, 1) # strides

    x = Conv2D(32, kernel_size=ks, padding=pg, activation=af)(input_layer)

    x = Conv2D(64, kernel_size=ks, padding=pg, activation=af)(x)
    x = MaxPooling2D(pool_size=ps)(x)

    x = Conv2D(128, kernel_size=ks, padding=pg, activation=af)(x)
    x = MaxPooling2D(pool_size=ps)(x)

    x = Conv2D(256, kernel_size=ks, padding=pg, activation=af)(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Cropping2D(cropping=((2, 2), (1, 1)))(x)

    x = Conv2D(512, kernel_size=ks, padding=pg, activation=af)(x)
    x = MaxPooling2D(pool_size=ps)(x)

    x = Conv2D(1024, kernel_size=ks, padding=pg, activation=af)(x)
    x = MaxPooling2D(pool_size=(4, 4))(x)

    units = int(x.shape[3])

    x = Flatten()(x)

    # Dense fully connected regression
    x = Dense(units, activation=af)(x)

    # Reshape before decoding
    x = Reshape((1, 1, units))(x)
    x = Conv2DTranspose(units, kernel_size=ks, strides=(1, 1), padding=pg, activation=af)(x)
    x = Conv2DTranspose(512, kernel_size=ks, strides=(2, 2), padding=pg, activation=af)(x)
    x = Conv2DTranspose(256, kernel_size=ks, strides=(2, 2), padding=pg, activation=af)(x)
    x = Conv2DTranspose(128, kernel_size=ks, strides=(2, 2), padding=pg, activation=af)(x)
    x = Conv2DTranspose(64, kernel_size=ks, strides=(4, 4), padding=pg, activation=af)(x)
    x = Cropping2D(cropping=((4, 3), (6, 6)))(x)

    x = Conv2DTranspose(32, kernel_size=ks, strides=(2, 2), padding=pg, activation=af)(x)
    x = ZeroPadding2D(padding=((0, 0), (1, 0)))(x)

    x = Conv2DTranspose(16, kernel_size=ks, strides=(2, 2), padding=pg, activation=af)(x)
    x = ZeroPadding2D(padding=((1, 0), (0, 0)))(x)

    x = Conv2DTranspose(8, kernel_size=ks, strides=(1, 1), padding=pg, activation=af)(x)
    x = Conv2DTranspose(4, kernel_size=ks, padding=pg, activation=af)(x)
    x = Conv2DTranspose(2, kernel_size=ks, padding=pg, activation=af)(x)

    outputs = Conv2DTranspose(1, kernel_size=ks, padding=pg, activation='linear', name='outputs')(x)

    return Model(inputs=[input_layer], outputs=[outputs])
