import argparse
import grpc
import numpy as np
import os
import pickle
import sys
import time

from tqdm import tqdm

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('server', help='server ip:port, e.g. 10.1.1.37:8500')
parser.add_argument('-b', '--batch', type=int, default=1, help='batch size')
parser.add_argument('-m', '--model', required=True, default='medium_cnn', type=str)
parser.add_argument('-n', default=128, type=int, help='number of requests')
parser.add_argument('-o', '--outfile', default='results.csv', help='name of output file')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-vv', action='store_true', help='extra verbose output')
parser.add_argument('--redux', action='store_true', help='divide args.n by args.batch')
args = parser.parse_args()

import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

hostport = args.server
print(hostport)

# Increase gRPC's default max limit of 4194304 (4MB)
MAX_MESSAGE_LENGTH = 2147483647 # 2GB gRPC hard limit
channel = grpc.insecure_channel(hostport, 
                                options=[('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)])
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

# Model definitions
isd = lambda a, b, c : {'inputs': a, 'shape': b, 'dtype': c}

models = {
          'small_lstm': isd('inputs', (args.batch, 8, 48), np.float32),
          'medium_cnn': isd('inputs', (args.batch, 101, 82, 9), np.float32),
          'large_tcnn': isd('inputs', (args.batch, 3, 101, 82, 9), np.float32),
          'swmodel': isd('dense_input', (args.batch, 3778), np.float32),
          'lwmodel': isd('dense_input', (args.batch, 1426), np.float32),
         }

times = list()
results = list()

data = np.array(np.random.random(models[args.model]['shape']), dtype=models[args.model]['dtype'])
payload_size = data.nbytes
print("payload size in bytes:", payload_size)

assert payload_size < MAX_MESSAGE_LENGTH, f"Exceeded gRPC payload limit of {MAX_MESSAGE_LENGTH}"

if args.redux:
    num_requests = int(args.n/args.batch)
else:
    num_requests = args.n

for _ in tqdm(range(num_requests)):
    data = np.array(np.random.random(models[args.model]['shape']), dtype=models[args.model]['dtype'])
    tik = time.perf_counter()
    request = predict_pb2.PredictRequest()
    request.model_spec.name = args.model
    request.model_spec.signature_name ='serving_default'
    request.inputs[models[args.model]['inputs']].CopyFrom(tf.make_tensor_proto(data, shape=models[args.model]['shape']))
    results.append(stub.Predict(request))
    if args.vv: print(results[0])
    tok = time.perf_counter()
    times.append(tok - tik)


elapsed = sum(times)
avg_inference_latency = elapsed/num_requests

print(f"elapsed time: {elapsed:.1f}s | average inference latency: {avg_inference_latency:.3f}s | 99th percentile latency: {np.percentile(times, 99):.3f}s | ips: {1/avg_inference_latency:.1f}")

write_header = True if not os.path.exists(args.outfile) else False

with open(args.outfile, 'a+') as f:
    if write_header: f.write("# batch size,elapse,avg_inf_latency,99% tail latency,throughput\n")
    f.write(f"{args.batch},{elapsed:.1f},{avg_inference_latency:.3f},{np.percentile(times, 99):.3f},{1/avg_inference_latency:.1f}\n")

