import os
import subprocess
import time
from datetime import datetime
from multiprocessing import Pool

# should run afte loading source .env.sh

num_requests = 32768
batch_sizes = [2048]
num_client_threads = [6]
WORKDIR = os.getenv('WORKDIR') or os.getcwd()
protocol = os.getenv('protocol') or 'HTTP'
LAUNCH_PER_NODE = os.getenv('LAUNCH_PER_NODE')
use_proxy = os.getenv('use_proxy') == 'true'
model = os.getenv('model')

if not model:
    print("Usage: python script.py modelname")
    exit(1)

if protocol == "gRPC":
    PORT = 8500
    CLIENT = 'tfs_grpc_client.py'
elif protocol == "HTTP":
    PORT = 8501
    CLIENT = 'tfs_http_client.py'
else:
    print(f"ERROR: protocol {protocol} not supported")
    exit()

if use_proxy:
    PORT = 8443


# Only output critical messages by TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

OUTFILE = f'/mnt/bb/{os.getenv("USER")}/results-n{os.getenv("NUM_HOSTS")}.csv'

print(f"model: {model}")

pids=[]


for BS in batch_sizes:
    print(f"batch-size: {BS}")

    NR = num_requests // BS
    print(f"# requests: {NR}")

    for NTHREADS in num_client_threads:
        START = datetime.now().timestamp()
        print(datetime.now())
        print(f"num_client_threads: {NTHREADS}")

        # Launch concurrent clients
        pids = []
        with Pool(NTHREADS) as p:
            for _ in range(NTHREADS):
                CMD = f"{LAUNCH_PER_NODE} python {CLIENT} -m {model} -b {BS} -n {num_requests} --redux -o {OUTFILE} localhost:{PORT}"
                print(CMD)
                pids.append(p.apply_async(os.system, (CMD,)))

            # Barrier
            print("Waiting for processes to finish to continue...")
            for pid in pids:
                pid.get()

        # Report timings
        END = datetime.now().timestamp()
        DIFF = round(END - START, 3)
        print(f"time taken (s): {DIFF}")
        print()

# copy back per node results
copy_cmd = f"cp {OUTFILE} {WORKDIR}/{os.getenv('LSB_JOBID')}-results-n{os.getenv('NUM_HOSTS')}-${{OMPI_COMM_WORLD_RANK}}.csv"
subprocess.run(f'{LAUNCH_PER_NODE} bash -c "{copy_cmd}"', shell=True)

print("all done")

