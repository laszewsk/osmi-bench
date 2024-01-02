import subprocess
import os
import subprocess
import time
import os

INSTANCE = "tfs-1"
EXEC = f"apptainer exec --nv instance://{INSTANCE}"

import subprocess
import time



def exec(command=None, directory=None):
    """
    Executes a command and returns the output.

    Args:
        command (str): The command to be executed.
        directory (str, optional): The directory in which the command should be executed. Defaults to None.
            TODO: in apptainer dir cahnge did not work so i implemented a sh script that does this internally see last lines

    Returns:
        str: The output of the executed command.
    """
    print("==============================")
    print(command)
    print("==============================")
    if directory is None:
        result = str(subprocess.check_output(command, shell=True))
    else:
        result = str(subprocess.check_output(command, shell=True, cwd=directory))  
    print(result)
    return result

def instance_exec(command=None, directory=None):
    """
    Executes a command in an tfs container instance
    
    Args:
        command (str): The command to execute.
        directory (str): The directory in which to execute the command.

    Returns:
        str: The result of the command execution.
    """
    command = f"{EXEC} {command}"
    result = exec(command)
    return result

def wait_for_port(port=8500, dt=1):
    while True:
        try:
            r = instance_exec(f"lsof -i :{port}")
        except:
            r = ""
        if 'LISTEN' in r:
            break
        time.sleep(dt)

try:
    r = exec(f"apptainer instance stop {INSTANCE}")
except:
    r = ""

assert "no instance found" not in r

r = exec("apptainer instance list")
assert INSTANCE not in r

pwd = os.getcwd()

#        apptainer shell --home `pwd` --nv images/cloudmesh-tfs.sif 
exec(f"apptainer instance start --nv --home {pwd} images/cloudmesh-tfs.sif {INSTANCE} ")

instance_exec(f"tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& log &")
r = exec("apptainer instance list")



wait_for_port(port=8500)

# done
print ("Server is up")

# Change the current working directory to "benchmark"

def instance_script(script):
    """
    Executes a script and returns the output.

    Args:
        script (str): The script to be executed.

    Returns:
        str: The output of the executed script.
    """
    with open("tmp-benchmark.sh", "w") as file:
        file.write(script)

    result = instance_exec(command="sh tmp-benchmark.sh")
    return result

script = """
#!/bin/sh
cd benchmark
python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
"""

r = instance_script(script)
