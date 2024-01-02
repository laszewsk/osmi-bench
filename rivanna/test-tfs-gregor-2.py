import subprocess
import os
import time

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

    def __init__(self, instance_name, image="images/cloudmesh-tfs.sif", port=8500):
        self.INSTANCE = instance_name
        self.EXEC = f"apptainer exec --nv instance://{self.INSTANCE}"
        self.IMAGE = image
        self.PORT = port

    def system(self, command=None, directory=None):
        """
        Executes a command in the Shell.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            directory (str, optional): The directory to execute the command in. Defaults to None.

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

    def instance_exec(self, command=None):
        """
        Executes a command on the TFS instance.

        Args:
            command (str, optional): The command to execute. Defaults to None.
            
        Returns:
            str: The output of the executed command.

        """
        command = f"{self.EXEC} {command}"
        result = self.system(command)
        return result

    def wait_for_port(self, port=None, dt=1):
        """
        Waits for the specified port to be in the LISTEN state in the instance.

        Args:
            port (int, optional): The port number to wait for. Defaults to 8500.
            dt (int, optional): The time interval between checks in seconds. Defaults to 1.

        """
        port = port or self.PORT
        while True:
            try:
                r = self.instance_exec(f"lsof -i :{port}")
            except:
                r = ""
            if 'LISTEN' in r:
                break
            time.sleep(dt)

    def instance_script(self, script, name="tmp-benchmark.sh"):
            """
            Executes a script on the TFS instance.

            Args:
                script (str): The script to execute. It can be multiline.
                name (str, optional): The name of the script file. Defaults to "tmp-benchmark.sh".

            Returns:
                str: The output of the executed script.

            """
            with open(name, "w") as file:
                file.write(script)
            result = self.instance_exec(command="sh tmp-benchmark.sh")
            return result

    def start(self):
        """
        Starts the TFS instance.
        1. fisrt ist looks for containers with the same name and stops them
        2. it checks if no container with the name is used.
        3. ist starts the container 

        """
        try:
            r = self.system(f"apptainer instance stop {self.INSTANCE}")
        except:
            r = ""

        assert "no instance found" not in r

        r = self.system("apptainer instance list")
        assert self.INSTANCE not in r

        pwd = os.getcwd()

        self.system(f"apptainer instance start --nv --home {pwd} {self.IMAGE} {self.INSTANCE} ")

        self.instance_exec(f"tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& log &")
        r = self.system("apptainer instance list")

        self.wait_for_port(port=8500)

        print ("Server is up")

# Usage
name = "tfs-1"
tfs = TFSInstance(name)
tfs.start()

script = """
#!/bin/sh
cd benchmark
python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
"""

r = tfs.instance_script(script)
