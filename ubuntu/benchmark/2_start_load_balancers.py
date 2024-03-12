import os
import subprocess
import time

# should run source ./env.sh before running this script

WORKDIR = os.getenv("WORKDIR")
NUM_HOSTS = os.getenv("NUM_HOSTS")
protocol = os.getenv("protocol")
LAUNCH_PER_NODE = os.getenv("LAUNCH_PER_NODE")

if not WORKDIR:
    print("WORKDIR not set... exiting")
    exit()

if not NUM_HOSTS:
    print("NUM_HOSTS not set... setting NUM_HOSTS=1")
    NUM_HOSTS = 1

if protocol == "HTTP":
    CFG_FILE = "haproxy-http.cfg"
elif protocol == "gRPC":
    CFG_FILE = "haproxy-grpc.cfg"
else:
    print(f"ERROR: protocol {protocol} not supported")
    exit(1)

print("launching load balancer on all nodes")
subprocess.run(
    f"{LAUNCH_PER_NODE} singularity exec --bind {os.getcwd()}:/home --pwd /home haproxy_latest.sif haproxy -d -f {CFG_FILE} > {WORKDIR}/haproxy.log &",
    shell=True,
)
print("checking port 8443 to see if HAProxy is running...")
time.sleep(5)
subprocess.run(f"{LAUNCH_PER_NODE} lsof -i :8443", shell=True)
