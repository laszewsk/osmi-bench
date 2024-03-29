""" test-cm-hap-yaml.
Usage:
  test-cm-hap-yaml.py [--config=CONFIG]
  test-cm-hap-yaml.py [--model=MODEL] [--batch=SIZE] [--instances=INSTANCES] [--port=PORT] [--haproxy=[0|1]] [--tfs=NUMBER_TFS] [--host=HOST]
    
Options:
  --model=MODEL         Specify the model name [default: medium]
  --batch=SIZE           Specify the batch size [default: 32]
  --instances=INSTANCES  Specify the number of instances [default: 1]
  --port=PORT            Specify the port [default: 8443]
  --haproxy=HAPROXY      Specify whether to use haproxy or not allowed values 0 or 1 [default: 1]
  --tfs=NUMBER_TFS       Specify the number of TFS instances [default: 1]
  --host=HOST            Specify the host address [default: localhost]
  --config=CONFIG        Specify the config file [default: config.yaml]
"""

import subprocess
import os
import sys
import textwrap
import time

from cloudmesh.apptainer.apptainer import Apptainer
from tabulate import tabulate
import textwrap
from cloudmesh.common.util import writefile
from cloudmesh.common.util import readfile    
from cloudmesh.common.FlatDict import FlatDict
from cloudmesh.common.FlatDict import expand_config_parameters
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from docopt import docopt
from tabulate import tabulate

# TODO: make sure the config files are unique for each instance
# TODO: make sure the ports are unique for each instance
# TODO: make sure the names are unique for each instance
# TODO: make sure the script names  are unique whenever a script is used


N = n =1 # number of tfs instances
M = m =10 # number of benchmarks
MODEL = "medium_cnn"
#MODEL = "large_tcnn"
#MODEL = "small_lstm"
BATCH = 32

TARGET = os.environ["OSMI_TARGET"]
IMAGES = f"{TARGET}/images"
MODELS = f"{TARGET}/models/models.conf"
BENCHMARK = f"{TARGET}/benchmark"
banner("target")
print(TARGET)
print(IMAGES)
print(MODELS)
print(BENCHMARK)


class HAProxyServer:
    """
    Represents an instance of HAProxy server.

    Attributes:
        name (str): The name of the haproxy instance.
        port (int): The port number to be used.
        image (str): The path to the haproxy image.
        logfile (str): The name of the log file.
        apptainer (Apptainer): An instance of the Apptainer class.
        images (list): A list of available images.
        ports (list): List of ports to be used in the configuration.
        filename (str): Name of the configuration file.
    """

    def __init__(self, name="haproxy", port=8443, image_dir=None, image="haproxy_latest.sif", logfile="haproxy.log"):
        """
        Initialize the Haproxy class.

        Args:
            name (str): The name of the haproxy instance. Default is "haproxy".
            port (int): The port number to be used. Default is 8443.
            image (str): The path to the haproxy image. Default is "images/haproxy_latest.sif".
            logfile (str): The name of the log file. Default is "haproxy.log".
        """
        image_dir = image_dir or IMAGES 

        self.apptainer = Apptainer()
        self.apptainer.add_location(image_dir)
        self.images = self.apptainer.images

        self.name = name
        self.port = port
        self.image = self.apptainer.find_image(image, smart=True)
        self.ports = None
        self.filename = None
        self.logfile = f"{name}.log"

    def check_config(self):
        """
        Checks the configuration of HAProxy by running the 'haproxy -f haproxy-grpc.cfg -c' command.
        
        Returns:
            The output of the command execution.
        """
        command = "haproxy -f haproxy-grpc.cfg -c"
        return self.apptainer.exec(name=self.name, command=command)

    def create_config(self, ports=None, host="localhost", filename="haproxy-grpc.cfg"):
        """
        Create a configuration file for HAProxy with the specified ports, host, and filename.

        Args:
            ports (list, optional): List of ports to be used in the configuration. Defaults to ["8500"].
            host (str, optional): Host address to bind the configuration to. Defaults to "localhost".
            filename (str, optional): Name of the configuration file. Defaults to "haproxy-grpc.cfg".
        """
        self.ports = ports or ["8500"]
        self.filename = filename
        configuration = textwrap.dedent(f"""
            global
            tune.ssl.default-dh-param 1024
            
            defaults
            timeout connect 10000ms
            timeout client 60000ms
            timeout server 60000ms
            
            frontend fe_https
            mode tcp
            bind 0.0.0.0:{self.port} npn spdy/2 alpn h2,http/1.1
            #bind *:{self.port} npn spdy/2 alpn h2,http/1.1
            default_backend be_grpc

            backend be_grpc
            mode tcp
            balance roundrobin
            """)

        for port in ports:
            server = f"server tfs0 localhost:{port}\n"
            configuration += server
        # configuration += "\n"

        writefile(filename, configuration)

    def start(self, clean=False, dt=0):
        """
        Start the HAPROXY service.

        Args:
            clean (bool, optional): Flag indicating whether to stop the HAPROXY before starting. Defaults to False.
            dt (int, optional): Delay time in seconds before stopping the HAPROXY. Defaults to 0.
        """
        if clean:
            self.stop(dt=0)
            
        pwd = os.getcwd()
    
        if os.path.exists(self.logfile):
            os.remove(self.logfile)        
 
        image_path = self.image["path"]
        print("Image Path", image_path)
        print("start ...", end="")
        stdout, stderr = self.apptainer.start(name=self.name, home=pwd, image=image_path)
        print("ok")
        print(stdout)

        command = f"haproxy -d -f {self.filename} > {self.logfile} 2>&1 &"
        print(command)

        banner("Start HAProxy")

        self.apptainer.exec(name=self.name, command=command)
        # r = self.apptainer.system("apptainer instance list")
        #
        # if wait:
        #    self.wait_for_port(name=self.name, port=self.port)
        #
        # print ("Server is up")

        # figure out a way to see if haproxy is up and working

    def stop(self, dt=0):
        """
        Stops the HAPROXY container.

        Args:
            dt (int): Delay time in seconds before checking if the container has stopped. Default is 0.

        Raises:
            AssertionError: If the container is still running after stopping.

        """
        try:
            r = self.apptainer.stop(self.name)
        except:
            r = ""

        time.sleep(dt)

        assert "no instance found" not in r

        r = self.apptainer.list()
        assert self.name not in r

    def status(self):
        pass
        
    def exec(self, command=None, bind=None, nv=False, home=None, verbose=True):
        """
        Executes a command on the HAPROXY instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            bind ():
            nv ():
            home ():
            verbose ():

        Returns:
            str: The output of the executed command.

        """
        stdout, stderr = self.apptainer.exec(name=self.name, command=command, bind=bind, nv=nv, home=home, verbose=True)

        if verbose:        
            banner(f"stdout {command}")
            print(stdout)
            banner(f"stderr {command}")
            print(stderr)
        return stdout, stderr

    def script(self, script, name=None):
        """
        Executes a script on the haproxy instance.

        Args:
            script (str): The script to execute. It can be multiline.
            name (str, optional): The name of the script file. Defaults to "tmp-benchmark.sh".

        Returns:
            str: The output of the executed script.

        """
        name = name or f"tmp-script-{self.name}.sh"
        with open(name, "w") as file:
            file.write(script)
        result = self.instance_exec(command=f"sh {name}")
        return result


class TFSInstance:
    """
    Represents a TensorFlow Serving (TFS) instance.

    Args:
        instance_name (str): The name of the TFS instance.

    Attributes:
        INSTANCE (str): The name of the TFS instance.
        
    Methods:
        exec(command=None, directory=None): Executes a command on the current shell.
        instance_exec(command=None, directory=None): Executes a command on the TFS instance.
        wait_for_port(port=8500, dt=1): Waits for the specified port to be in the LISTEN state in the TFS instance.
        instance_script(script): Executes a script on the TFS instance.
        start(): Starts the TFS instance.

    """        

    def __init__(self, name="tfs-0", models=None, image_dir=None, image="cloudmesh-tfs-23-10-nv.sif", port=8500, gpu=0):
        """
        Initializes an instance of the TFS.

        Args:
            name (str): The name of the instance (default: "tfs-0").
            image (str): The image to be used (default: "cloudmesh-tfs-23-10-nv.sif").
            port (int): The port number (default: 8500).
            gpu (int): The GPU number (default: 0).
        """

        models = models or MODELS
        image_dir = image_dir or IMAGES
        self.apptainer = Apptainer()
        self.apptainer.add_location(image_dir)
        images = self.apptainer.images

        self.name = name
        self.image = image
        self.port = port
        self.pgpu = gpu
        self.log = f"{name}-serving.log"
        self.models = models

        print(self.apptainer.find_image(self.image, smart=True))
    

    def exec(self, command=None, bind=None, nv=True, home=None, verbose=True):
        """
        Executes a command on the TFS instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            bind (): 
            nv (): 
            home (): 
            verbose (): 
            
            
        Returns:
            str: The output of the executed command.

        """
        stdout, stderr = self.apptainer.exec(name=self.name, command=command, bind=bind, nv=nv, home=home, verbose=True)

        if verbose:        
            banner(f"stdout {command}")
            print(stdout)
            banner(f"stderr {command}")
            print(stderr)
        return stdout, stderr

    def wait_for_port(self, port=None, dt=1, verbose=False):
        """
        Waits for the specified port to be in the LISTEN state in the instance.

        Args:
            port (int, optional): The port number to wait for. Defaults to 8500.
            dt (int, optional): The time interval between checks in seconds. Defaults to 1.
            verbose ():

        """
        port = port or self.port
        while True:
            try:
                stdout, stderr = self.exec(command=f"lsof -i :{port}", verbose=verbose)
            except:
                stdout = ""
                stderr = ""

            if '(LISTEN)' in stdout:
                break
            time.sleep(dt)

    def script(self, script, name=None):
        """
        Executes a script on the TFS instance.

        Args:
            script (str): The script to execute. It can be multiline.
            name (str, optional): The name of the script file. Defaults to "tmp-benchmark.sh".

        Returns:
            str: The output of the executed script.

        """
        name = name or f"tmp-script-{self.name}.sh"
        with open(name, "w") as file:
            file.write(script)
        result = self.instance_exec(command=f"sh {name}")
        return result

    def stop(self, dt=0):
        """
        Stop the TFS container.

        Args:
            dt (int): Delay time in seconds before checking if the container has stopped. Default is 0.

        Raises:
            AssertionError: If the container is not stopped successfully.

        """
        try:
            r = self.apptainer.stop(self.name)
        except:
            r = ""

        time.sleep(dt)

        assert "no instance found" not in r

        r = self.apptainer.list()
        assert self.name not in r

    def start(self, gpu=None, clean=False, wait=True):
        """
        Starts the TFS instance.

        Args:
            gpu (str, optional): The GPU to use. Defaults to None.
            clean (bool, optional): Whether to stop and clean any existing containers with the same name. Defaults to False.
            wait (bool, optional): Whether to wait for the server to be up and running. Defaults to True.
        
        1. first ist looks for containers with the same name and stops them
        2. it checks if no container with the name is used.
        3. ist starts the container 

        """
        if clean:
            self.stop(dt=0)
            
        pwd = os.getcwd()
        os.system(f"rm -f {self.log}")

        print("start ...", end="")
        stdout, stderr = self.apptainer.start(name=self.name, home=pwd, image=self.image, gpu=gpu)
        print("ok")
        print(stdout)

        banner("command")
        command = f"tensorflow_model_server"\
                  f" --port={self.port} --rest_api_port=0 --model_config_file={self.models} >& {self.log} &"

        print(command)

        self.apptainer.exec(name=self.name, command=command)
        r = self.apptainer.system("apptainer instance list")

        if wait:
            self.wait_for_port(port=self.port)

        print("Server is up")


class TFSBenchmark:
    """
    A class representing a TensorFlow Serving benchmark.

    Attributes:
        name (str): The name of the benchmark.
        port (int): The port number for the TensorFlow Serving server.
        model (str): The name of the TensorFlow model to be used.
        batch (int): The batch size for the benchmark.
        n (int): The number of iterations for the benchmark.
        output_log (str): The name of the output log file.

    Methods:
        run(): Runs the benchmark by executing the TensorFlow Serving client.
        completed(): Checks if the benchmark has completed successfully.
    """

    def __init__(self, name=None, port=8443, model="medium_cnn", batch=32, n=10):
        """
        Initialize the benchmark with the given parameters.

        Args:
            name (str, optional): The name of the instance. Defaults to None.
            port (int, optional): The port number. Defaults to 8443.
            model (str, optional): The model to use. Defaults to "medium_cnn".
            batch (int, optional): The batch size. Defaults to 32.
            n (int, optional): The value of n. Defaults to 10.
        """
        self.name = name
        self.port = port
        self.model = model
        self.batch = batch
        self.n = n
        self.output_log = f"{self.name}.log"
        self.benchmark_dir = BENCHMARK

    def run(self):
        """
        Runs the benchmark by executing the specified command.
        """
        command = f"python {self.benchmark_dir}/tfs_grpc_client.py"\
                  f" --name {self.name}"\
                  f" -m {self.model}"\
                  f" -b {self.batch}"\
                  f" -n {self.n}"\
                  f" localhost:{self.port}"\
                  f" >& {self.output_log} &"
        banner("command")
        print(command)
        print(f"Benchmark {self.name} ...", end="")
        os.system(command)
        
    def completed(self):
        """
        Checks if the task has been completed.

        Returns:
            bool: True if the task is completed, False otherwise.
        """
        if os.path.isfile(self.output_log):
            result = readfile(self.output_log)
            if "# cloudmesh status=done progress=100" in result:
                print("completed")
                return True
        return False


def print_instances(tfs):
    """
    Print the information about the instances.

    Args:
        tfs (object): The tfs object.

    Returns:
        None
    """
    instances = tfs.apptainer.list()
    for i in range(0, n):
        for key in ["logErrPath", "logOutPath", "ip"]:
            del instances[i][key]
    print(
        tabulate(
            instances, headers="keys", tablefmt="simple_grid", showindex="always"
        )
    )


# START SERVERS
banner("Start servers") 
#n=1
server = []     
ports = []
for i in range(0,n):
    name = f"tfs-{i}"
    port = 8500 + i
    ports.append(port)
    print ("Start server", i, name, port)
    tfs = TFSInstance(name=name, port=port)
    server.append(tfs)
    tfs.start(gpu=i, clean=True, wait=False)



print_instances(tfs)

# WAIT FOR SERVERS TO BE READY
banner("Wait for servers to be ready")
for i in range(0,n):
    print (f"Wait for TFS {i} to b ready ...", end="")
    server[i].wait_for_port()
print("servers are up")

port = 8443
# haproxy = HAProxyServer(name="haproxy", port=port, image="images/haproxy_latest.sif", logfile="haproxy.log")
haproxy = HAProxyServer(name="haproxy", port=port)

print ("PORTS:", ports)


haproxy.create_config(ports=ports, host="localhost", filename="haproxy-grpc.cfg")
haproxy.start()


stdout, stderr = haproxy.check_config()
if stderr != "":
    banner("STDOUT")
    print (stdout)
    banner("STDERR")
    print (stderr)

    print ("ERROR: haproxy config is not valid")
    sys.exit()  



#haproxy.wait_for_port(port=port) 


# START HAPROXY

# storr one or 0 haproxy


# benchamrk

# if not haproxy (haproxy = 0)
#    python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
# elif haproxy = 1:
#      python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8443

#script = f"""
##!/bin/sh
#cd benchmark
#python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:{port}
#"""

#m = 1
benchmarks = []
# BENCHMARK ON n SERVERS
banner("Benchmark")
for i in range(0,m):
    name = f"benchmark-{i}"
    benchmark = TFSBenchmark(name=name, port=port, model=MODEL, batch=BATCH, n=N)
    benchmarks.append(benchmark)
    benchmark.run()
    print (" started")

# WAIT FOR BENCHMARK TO BE COMPLETED
banner("Wait for benchmark to be completed")
while True:
    completed = True
    for i in range(0,m):
        benchmark = benchmarks[i]
        if not benchmark.completed():
            completed = False
    if completed:
        break
    time.sleep(1)


# SHUTDOWN SERVERS
banner("Shutdown servers")
for i in range(0,n):
    print (f"TFS {i} to b ready ...", end="")
    server[i].stop()
    print (" ok")

# SHUTDOWN HAPROXY
banner("Shutdown haproxy")
haproxy.stop()

#time.sleep(1)
os.system("cma list")








# r = tfs.instance_script(script)

# os.system("apptainer exec --bind `pwd`:/home --pwd /home images/haproxy_latest.sif haproxy -d -f haproxy-grpc.cfg > haproxy.log 2>&1 &")


# pwd = os.getcwd()
# command = f"apptainer instance start --nv --home {pwd}/benchmark images/haproxy_latest.sif haproxy"} 

# print (command)


#THIS WORKS
#=========================================
# source env.sh
# login-2.sh
# source env.sh
# python test-tfs-gregor-ha-1.py
# cd benchmark
# apptainer instance start --nv --home `pwd` ../images/haproxy_latest.sif haproxy
# apptainer exec instance://haproxy haproxy -d -f haproxy-grpc.cfg > haproxy.log 2>&1 &
# apptainer instance list
# python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8443
# ==================================================   

# assert instance name contains haproxy

# cat haproxy.log 
# Note: setting global.maxconn to 32747.
# Available polling systems :
#       epoll : pref=300,  test result OK
#        poll : pref=200,  test result OK
#      select : pref=150,  test result FAILED
# Total: 3 (2 usable), will use epoll.

# Available filters :
# 	[BWLIM] bwlim-in
# 	[BWLIM] bwlim-out
# 	[CACHE] cache
# 	[COMP] compression
# 	[FCGI] fcgi-app
# 	[SPOE] spoe
# 	[TRACE] trace
# Using epoll() as the polling mechanism.

