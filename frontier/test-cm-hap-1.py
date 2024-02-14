import subprocess
import os
import time
from cloudmesh.common.util import banner
from cloudmesh.apptainer.apptainer import Apptainer
from tabulate import tabulate
import textwrap
from cloudmesh.common.util import writefile
import sys
from cloudmesh.common.util import readfile

# TODO: make sure the config files are unique for each instance
# TODO: make sure the ports are unique for each instance
# TODO: make sure the names are unique for each instance
# TODO: make sure the script names  are unique whenever a scipt is used

class HAProxyServer:

    def __init__(self, name="haproxy", port=8443, image="images/haproxy_latest.sif", logfile="haproxy.log"):

        self.apptainer = Apptainer()
        self.apptainer.add_location("./images")
        self.images = self.apptainer.images

        self.name = name
        self.port = port
        self.image = self.apptainer.find_image(image, smart=True)
        self.ports = None
        self.filename = None
        self.logfile = f"{name}.log"

    def check_config(self):
        command = "haproxy -f haproxy-grpc.cfg -c"
        return self.apptainer.exec(name=self.name, command=command)

    def create_config(self, ports=["8500"], host="localhost", filename="haproxy-grpc.cfg"):
        self.ports = ports
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
        #configuration += "\n"

        writefile(filename, configuration)

    def start(self, clean=False, dt=0):
        pass    
        if clean:
            self.stop(dt=0)
            
        pwd = os.getcwd()
        
        os.system(f"rm -f {self.logfile}")

        image_path = self.image["path"]
        print ("IIII", image_path)
        print ("start ...", end="")
        stdout, stderr= self.apptainer.start(name=self.name, home=pwd, image=image_path)
        print ("ok")
        print (stdout)


        command = f"haproxy -d -f {self.filename} > {self.logfile} 2>&1 &"

        banner("Start HAProxy")

        self.apptainer.exec(name=self.name, command=command)
        #r = self.apptainer.system("apptainer instance list")
        #
        #if wait:
        #    self.wait_for_port(name=self.name, port=self.port)
        #
        #print ("Server is up")

        # figure out a way to see if haproxy is up and working



    def stop(self, dt=0):
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
        Executes a command on the TFS instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            
        Returns:
            str: The output of the executed command.

        """
        stdout, stderr = self.apptainer.exec(name=self.name, command=command, bind=bind, nv=nv, home=home, verbose=True)

        if verbose:        
            banner(f"stdout {command}")
            print (stdout)
            banner(f"stderr {command}")
            print (stderr)
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

    def __init__(self, name="tfs-0", image="cloudmesh-tfs-23-10-nv.sif", port=8500, gpu=0):

        self.apptainer = Apptainer()
        self.apptainer.add_location("./images")
        images = self.apptainer.images

        self.name = name
        self.image = image
        self.port = port
        self.pgpu = gpu
        self.log = f"{name}-serving.log"
        
        print (self.apptainer.find_image(self.image, smart=True))
    

    def exec(self, command=None, bind=None, nv=True, home=None, verbose=True):
        """
        Executes a command on the TFS instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            
        Returns:
            str: The output of the executed command.

        """
        stdout, stderr = self.apptainer.exec(name=self.name, command=command, bind=bind, nv=nv, home=home, verbose=True)

        if verbose:        
            banner(f"stdout {command}")
            print (stdout)
            banner(f"stderr {command}")
            print (stderr)
        return stdout, stderr

    def wait_for_port(self, port=None, dt=1, verbose=False):
        """
        Waits for the specified port to be in the LISTEN state in the instance.

        Args:
            port (int, optional): The port number to wait for. Defaults to 8500.
            dt (int, optional): The time interval between checks in seconds. Defaults to 1.

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
        1. fisrt ist looks for containers with the same name and stops them
        2. it checks if no container with the name is used.
        3. ist starts the container 

        """
        if clean:
            self.stop(dt=0)
            
        pwd = os.getcwd()
        os.system(f"rm -f {self.log}")

        print ("start ...", end="")
        stdout, stderr= self.apptainer.start(name=self.name, home=pwd, image=self.image, gpu=gpu)
        print ("ok")
        print (stdout)

        self.apptainer.exec(name=self.name, command=f"tensorflow_model_server --port={self.port} --rest_api_port=0 --model_config_file=benchmark/models.conf >& {self.log} &")
        r = self.apptainer.system("apptainer instance list")

        if wait:
            self.wait_for_port(name=self.name, port=self.port)

        print ("Server is up")


def print_instances(tfs):
    instances = tfs.apptainer.list()
    for i in range(0,n):
        for key in ["logErrPath", "logOutPath", "ip"]:
            del instances[i][key]
    print(
        tabulate(
            instances, headers="keys", tablefmt="simple_grid", showindex="always"
        )
    )


# START SERVERS
banner("Start servers") 
n=1
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

# BENCHMARK ON n SERVERS
banner("Benchmark")
for i in range(0,n):
    name = f"tfs-{i}"
    # port = 8500 + i
    command = f"python benchmark/tfs_grpc_client.py --name {name} -m medium_cnn -b 32 -n 10 localhost:{port}"
    print (f"Benchmark {i} ...", end="")
    #server[i].exec(command=command)
    os.system(command)
    print (" ok")

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

