""" The TCNN architecture is described in the following paper:

    Pandey, Ashutosh, and DeLiang Wang. "TCNN: Temporal convolutional neural 
    network for real-time speech enhancement in the time domain." In ICASSP 
    2019-2019 IEEE International Conference on Acoustics, Speech and Signal 
    Processing (ICASSP), pp. 6875-6879. IEEE, 2019.
"""

import numpy as np
import tensorflow.keras.layers as tfkl

from tensorflow.keras.models import Model
from tensorflow.keras.layers import TimeDistributed, Cropping2D, Add, Conv1D, Conv2D, \
                                    Conv2DTranspose, Input, MaxPooling2D, Reshape, \
                                    UpSampling2D, ZeroPadding2D


def resblock(inputs, units, settings):
    x1 = TimeDistributed(Conv2D(units, **settings))(inputs)
    x2 = TimeDistributed(Conv2D(units, **settings))(x1)
    return tfkl.Add()([x1, x2])


def build_model(input_shape, af='elu'):
    pool = (2, 2)

    inputs = Input(shape=input_shape, name='inputs')
    settings = dict(kernel_size=(4, 4), padding='same', activation=af)

    # Encoder region

    x = resblock(inputs, 9, settings)
    x = resblock(x, 16, settings)
    x = resblock(x, 32, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)

    x = resblock(x, 64, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)

    x = resblock(x, 128, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)
    x = TimeDistributed(Cropping2D(cropping=((3, 1), (2, 0)), \
                                   data_format="channels_last"))(x)

    x = resblock(x, 256, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)

    x = resblock(x, 512, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)
    x = TimeDistributed(Cropping2D(cropping=((0, 0), (0, 0)), \
                                   data_format="channels_last"))(x)

    x = resblock(x, 1024, settings)
    x = TimeDistributed(MaxPooling2D(pool_size=pool))(x)

    x = Reshape((3, 1024))(x)

    # Temporal convolutional model (TCM)

    filters = 2*int(x.shape[2])
    settings2 = dict(kernel_size=2, padding='causal', activation=af)
 
    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=1, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=2, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=2, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=2, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=12, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    y = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = Conv1D(filters, dilation_rate=32, **settings2)(y)
    x = Conv1D(filters, dilation_rate=1, **settings2)(x)
    x = tfkl.Add()([y, x])

    x = Reshape((3, 1, 1, 2048))(x)

    # Decoder region

    x = resblock(x, 1024, settings)
    x = TimeDistributed(UpSampling2D(size=pool))(x)

    x = resblock(x, 512, settings)
    x = TimeDistributed(UpSampling2D(size=pool))(x)
    x = TimeDistributed(Cropping2D(cropping=((0, 0), (0, 0)), \
                                   data_format="channels_last"))(x)

    x = resblock(x, 256, settings)
    x = TimeDistributed(UpSampling2D(size=pool))(x)
    x = TimeDistributed(Cropping2D(cropping=((0, 0), (0, 0)), \
                                   data_format="channels_last"))(x)

    x = resblock(x, 128, settings)
    x = TimeDistributed(UpSampling2D(size=(4, 4)))(x)
    x = TimeDistributed(Cropping2D(cropping=((3, 4), (6, 6)), 
                                   data_format="channels_last"))(x)

    x = resblock(x, 64, settings)
    x = TimeDistributed(UpSampling2D(size=pool))(x)
    x = TimeDistributed(ZeroPadding2D(padding=((0, 0), (1, 0))))(x)

    x = resblock(x, 32, settings)
    x = TimeDistributed(UpSampling2D(size=pool))(x)
    x = TimeDistributed(ZeroPadding2D(padding=((1, 0), (0, 0))))(x)

    x = resblock(x, 16, settings)

    x = resblock(x, 9, settings)

    x = TimeDistributed(Conv2DTranspose(4, **settings))(x)

    x = TimeDistributed(Conv2DTranspose(2, **settings))(x)

    settings['activation'] = 'linear'
    outputs = TimeDistributed(Conv2DTranspose(1, **settings), name='outputs')(x)

    return Model(inputs=[inputs], outputs=[outputs])


if __name__ == '__main__':
    model = build_model((3, 101, 82, 9))
    model.summary()
