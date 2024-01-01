import subprocess
import os
import subprocess
import time
import os

INSTANCE = "tfs"
EXEC = f"apptainer exec instance://{INSTANCE}"

def exec(command=None, directory=None):
    print("==============================")
    print(command)
    print("==============================")
    if directory is None:
        result = str(subprocess.check_output(command, shell=True))
    else:
        result = str(subprocess.check_output(command, shell=True, cwd=directory))  
    print(result)
    return result

def app_exec(command=None, directory=None):
    command = f"{EXEC} {command}"
    result = exec(command)
    return result

try:
    r = exec(f"apptainer instance stop {INSTANCE}")
except:
    r = ""

assert "no instance found" not in r

r = exec("apptainer instance list")
assert INSTANCE not in r


exec(f"apptainer instance start images/cloudmesh-tfs.sif {INSTANCE} --nv")
exec("apptainer instance list")
app_exec("ls")

app_exec(f"tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& log &")

r = exec("apptainer instance list")

while True:
    try:
        r = app_exec(f"lsof -i :8500")
    except:
        r = ""
    if 'LISTEN' in r:
         break
    time.sleep(1)

# done
print ("Server is up")

# Change the current working directory to "benchmark"

script = """
#!/bin/sh
cd benchmark
python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
"""

with open("tmp-benchmark.sh", "w") as file:
    file.write(script)

r = app_exec(command="sh tmp-benchmark.sh")