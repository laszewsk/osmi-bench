import subprocess
import os
import time
from cloudmesh.common.util import banner
from cloudmesh.apptainer.apptainer import Apptainer

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

    def __init__(self, name="tfs", image="cloudmesh-tfs.sif", port=8500, gpu=0):

        print ("YYYYYYYYY")
        self.apptainer = Apptainer()
        self.apptainer.images(directory="iages")
        print ("UUUUUU")

        self.INSTANCE = name
        self.IMAGE = image
        self.PORT = port
        self.GPU = gpu
    

    def instance_exec(self, name=None, command=None, bind=None, nv=True, home=None, verbose=True):
        """
        Executes a command on the TFS instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            
        Returns:
            str: The output of the executed command.

        """
        stdout, stderr = self.apptainer.exec(name, command, bind=bind, nv=nv, home=home, verbose=True)
        
        print (stdout)
        print (stderr)

    def wait_for_port(self, name=None, port=None, dt=1):
        """
        Waits for the specified port to be in the LISTEN state in the instance.

        Args:
            port (int, optional): The port number to wait for. Defaults to 8500.
            dt (int, optional): The time interval between checks in seconds. Defaults to 1.

        """
        port = port or self.PORT
        while True:
            try:
                r = self.instance_exec(name=name, command=f"lsof -i :{port}")
            except:
                r = ""
            if 'LISTEN' in r:
                break
            time.sleep(dt)

    def instance_script(self, script, name=None):
            """
            Executes a script on the TFS instance.

            Args:
                script (str): The script to execute. It can be multiline.
                name (str, optional): The name of the script file. Defaults to "tmp-benchmark.sh".

            Returns:
                str: The output of the executed script.

            """
            name = name or f"tmp-script-{self.INSTANCE}.sh"
            with open(name, "w") as file:
                file.write(script)
            result = self.instance_exec(command=f"sh {name}")
            return result

    def start(self, gpu=None, clean=False, wait=True):
        """
        Starts the TFS instance.
        1. fisrt ist looks for containers with the same name and stops them
        2. it checks if no container with the name is used.
        3. ist starts the container 

        """
        if clean:
            try:
                r = self.apptainer.stop(self.INSTANCE)
            except:
                r = ""

            assert "no instance found" not in r

            r = self.apptainer.list()
            assert self.INSTANCE not in r

        pwd = os.getcwd()
        print ("start ...", end="")
        stdout, stderr= self.apptainer.start(name=self.INSTANCE, home=pwd, image=self.IMAGE, gpu=gpu)
        print ("ok")
        print (stdout)

        self.apptainer.exec(command=f"tensorflow_model_server --port={self.PORT} --rest_api_port=0 --model_config_file=benchmark/models.conf >& log-{self.INSTANCE}.log &")
        r = self.apptainer.system("apptainer instance list")

        self.wait_for_port(name=self.INSTANCE, port=self.PORT)

        print ("Server is up")

# Usage

n=2
server = []     
for i in range(0,n):
    name = f"tfs-{i}"
    port = 8500 + i
    print (i, name, port)
    tfs = TFSInstance(name=name, port=port)
    server.append(tfs)
    tfs.start(gpu=i, clean=True, wait=False)

# for i in range(0,n):
#     print (i)
#     tfs = server[i]
#     tfs.wait_for_port(port=8500+i)

print("servers are up")

# script = f"""
# #!/bin/sh
# cd benchmark
# python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:{port}
# """

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

