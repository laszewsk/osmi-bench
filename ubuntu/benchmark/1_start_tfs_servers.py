import os
import subprocess
import time

def sleep_countdown(seconds):
    for remaining in range(seconds, 0, -1):
        print(f"Sleeping... {remaining} seconds remaining", end='\r')
        time.sleep(1)
    print("")

WORKDIR = os.getenv("WORKDIR") or os.getcwd()
NUM_HOSTS = int(os.getenv("NUM_HOSTS")) or 1
NGPUS = 2  # Assuming NGPUS is 2; you can modify it accordingly

if os.path.isfile("models.conf"):
    OPTS = "--model_config_file=models.conf"
else:
    print("ERROR: models.conf file missing")
    exit(1)

pids = []
ports = []

protocol = "HTTP"  # Assuming the protocol is HTTP; modify if needed

LAUNCHG= "????"

for i in range(0,NUM_HOSTS):
    for j in range(0,NGPUS):
        PORT = 8500 + j
        set_cuda_visible_devices = True  # Assuming this condition is true; modify if needed
        if set_cuda_visible_devices:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(j)

        if protocol == "HTTP":
            CMD = f"tensorflow_model_server --rest_api_port={PORT} {OPTS}"
        elif protocol == "gRPC":
            CMD = f"$LAUNCHG tensorflow_model_server --port={PORT} --rest_api_port=0 {OPTS}"
        else:
            print(f"ERROR: protocol {protocol} not supported")
            exit(1)

        print(f"running: {CMD}")
        process = subprocess.Popen(CMD, shell=True, cwd=WORKDIR, stdout=open(f"{WORKDIR}/tfs-h{i}-g{j}.log", "w"))
        pids.append(str(os.getpid()))
        pids.append(process.pid)
        ports.append(str(PORT))

print(f"{NGPUS} servers started on ports {' '.join(ports)}")
print(f"PIDs are {' '.join(pids)}")

print("checking ports 8500-8501 to see if TensorFlow Serving instances are running")
print("sleeping 10 seconds to allow time for start up")

sleep_countdown(10)

for i in range(0,NUM_HOSTS):
    for j in range(0,NGPUS):
        PORT = 8500 + j
        subprocess.Popen(f"lsof -i :{PORT}", shell=True)


