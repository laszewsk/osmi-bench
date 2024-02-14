import argparse
import json
import numpy as np
import os
import pickle
import requests
import sys
import time

from tqdm import tqdm

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('server', help='server ip:port, e.g. 10.1.1.37:8080')
parser.add_argument('-b', '--batch', type=int, default=1, help='batch size')
parser.add_argument('-m', '--model', required=True, default='medium_cnn', type=str)
parser.add_argument('-n', default=128, type=int, help='number of requests')
parser.add_argument('-o', '--outfile', default='results.csv', help='name of output file')
parser.add_argument('-q', '--query', action='store_true', help="query the model and exit")
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
args = parser.parse_args()

# Send random data and get response
url = "http://" + args.server + "/v1/models/" + args.model
#print(f"sending requests to {url}")
elapsed = 0
#print(args.n)

times = []

if args.query:
    response = requests.get(url)
    print(response.text)
    response = requests.get(url+"/metadata")
    print(response.text)
    sys.exit()

if args.model == "small_lstm":
    shape = (args.batch, 8, 48)
elif args.model == "medium_cnn":
    shape = (args.batch, 101, 82, 9)
elif args.model == "large_tcnn":
    shape = (args.batch, 3, 101, 82, 9)
else:
    raise ValueError("model not supported")

method_name = ":predict"
headers = {"content-type": "application/json"}

for _ in tqdm(range(args.n)):
    data = np.array(np.random.random(shape))
    payload = json.dumps({"instances": data.tolist()})
    
    response = requests.post(url + method_name, data=payload, headers=headers)
    times.append(response.elapsed.total_seconds())

    # Raise exception if anything other than HTTP 200 status code returned
    response.raise_for_status()

    # Consume data
    data_received = response.content
    if args.verbose: print(data_received)

elapsed = sum(times)
avg_inference_latency = elapsed/args.n

print(f"elapsed time: {elapsed:.1f}s | average inference latency: {avg_inference_latency:.3f}s | 99th percentile latency: {np.percentile(times, 99):.3f}s | ips: {1/avg_inference_latency:.1f}")

write_header = True if not os.path.exists(args.outfile) else False

with open(args.outfile, 'a+') as f:
    if write_header: f.write("# batch size,elapse,avg_inf_latency,99% tail latency,throughput\n")
    f.write(f"{args.batch},{elapsed:.1f},{avg_inference_latency:.3f},{np.percentile(times, 99):.3f},{1/avg_inference_latency:.1f}\n")
