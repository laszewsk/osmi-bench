"""
Example usage:

Start servers on multiple GPUs:

    ./1_start_tfs_servers.sh

Then run this code e.g. to use 2 GPUs with a sweep of concurrencies 1 2 4 8 16 per GPU:

    export CUDA_VISABLE_DEVICES=0,1
    python sweep.py localhost -g T4 -b 64 -c 1 2 4 8 16 --ports 8500 8501 8502 8503 -n 2

or, can use a YAML file to specify all the options, e.g.:

    python sweep.py rivanna-v100.yaml -o results-v100.csv

"""

import argparse
import csv
import datetime
import glob
import os
import re
import subprocess
import yaml

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Where to store intermediate files
out_path = "/dev/shm"
#out_path = os.environ['WORKDIR']

# Grab the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('server', help='server ip:port, e.g. 10.1.1.37:8080')
parser.add_argument('-g', '--gpu', type=str, default="none", help='enter in the GPU type {V100, P100}')
parser.add_argument('-b', '--batch', nargs='+', type=int)
parser.add_argument('-c', '--concurrency', nargs='+', type=int)
parser.add_argument('-n', '--ngpus', nargs='+', type=int)
parser.add_argument('-p', '--ports',  nargs='+', type=int)
parser.add_argument('-o', '--outfn', default='results.csv')
parser.add_argument('-a', '--algorithm', default='tfs_grpc_client.py'
args = parser.parse_args()

with open (args.outfn, 'w') as csvfile:
    cw = csv.writer(csvfile, delimiter=',')
    cw.writerow("Timestamp:GPU:Server:Concurrency:BatchSize:Throughput (inf/s):Latency (ms)".split(":"))

extract = lambda x: float(re.findall('\d+.\d+', x)[0])

if ".yaml" in args.server:
    # read and parse YAML file
    with open(args.server,'r') as f:
        sections = yaml.load(f.read())

    for section, options in sections.items():
        for option, value in options.items():
            setattr(args, option, value)

print(args)

for batchsize in args.batch: # e.g. [16, 64]
    print(f"\nbatchsize: {batchsize}")
    for ngpus in args.ngpus: # e.g. [1, 2, 4, 8]
        print(f"ngpus: {ngpus}")
        for concurrency in args.concurrency: # e.g. [1, 2, 4, 8, 16]
            print(f"concurrency: {concurrency}")
            proc = []
            for flask_id, port in enumerate(args.ports[:ngpus], start=1): #[8100....8800]
                for client_rank in range(concurrency):
                    cmd = "python tfs_grpc_client.py {}:{} -m batch -b {} >& {}/log{}.{}.txt".format(
                           args.server, port, batchsize, out_path, flask_id, client_rank) 
                    timestamp = datetime.datetime.now().time()
                    print(timestamp, cmd)
                    proc.append(subprocess.Popen(cmd, shell=True))

            # Barrier 
            exit_codes = [p.wait() for p in proc]

            filenames = glob.glob(os.path.join(out_path, "log*"))
            print(filenames)
            num_files = len(filenames)
            throughput = latency = 0

            for fn in filenames:
                with open(fn) as f:
                    lines = f.readlines()

                for line in lines:
                    if re.search("Throughput", line): throughput += extract(line)
                    if re.search("Latency", line): latency += extract(line)
                # Delete log files after getting perf metrics.
                os.unlink(fn)
            
            throughput = int(throughput)
            avg_latency = "{:.2f}".format(latency/num_files)
            print("throughput: {}".format(throughput)) 
            print("avg latency: {}".format(avg_latency))
            with open(args.outfn, 'a') as csvfile:
                cw = csv.writer(csvfile, delimiter=',')
                cw.writerow([timestamp, args.gpu, flask_id, concurrency, batchsize, throughput, avg_latency])

