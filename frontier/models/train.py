"""usage: python train.py {small_lstm|medium_cnn|large_tcnn}"""
import argparse
import importlib
import numpy as np
import os
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import banner
from cloudmesh.common.debug import VERBOSE

StopWatch.start("total")
StopWatch.start("setup")
parser = argparse.ArgumentParser()
archs = [s.split('.')[0] for s in os.listdir('archs') if s[0:1] != '_']
parser.add_argument('arch', type=str, choices=archs, help='Type of neural network architectures')
args = parser.parse_args()

# parameters
samples = 100 
epochs = 5
batch_size = 32

# compute synthetic data for X and Y
if args.arch == "small_lstm":
    input_shape = (8, 48)
    output_shape = (2, 12)
elif args.arch == "medium_cnn":
    input_shape = (101, 82, 9)
    output_shape = (101, 82)
elif args.arch == "large_tcnn":
    input_shape = (3, 101, 82, 9)
    output_shape = (3, 101, 82, 1)
else:
    raise ValueError("Model not supported. Need to specify input and output shapes")

X = np.random.rand(samples, *input_shape)
Y = np.random.rand(samples, *output_shape)

physical_devices = tf.config.list_physical_devices('GPU')
StopWatch.event("tensorflow", {"version": tf.__version__})
StopWatch.event("gpus", {"gpus": len(physical_devices)})

StopWatch.stop("setup")


# define model
StopWatch.start("define-model")
model = importlib.import_module('archs.' + args.arch).build_model(input_shape)
model.summary()
StopWatch.stop("define-model") 

# compile model
StopWatch.start("compile-model")
model.compile(loss='mae', optimizer='adam')
StopWatch.stop("compile-model")

# train model
StopWatch.start("train-model")
model.fit(X, Y, batch_size=batch_size, epochs=epochs)
StopWatch.stop("train-model")

StopWatch.start("save-model")
model.save(f"{args.arch}/1")
StopWatch.stop("save-model")

StopWatch.stop("total") 

StopWatch.benchmark(tag=args.arch)   
