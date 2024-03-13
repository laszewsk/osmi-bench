FROM nvcr.io/nvidia/tensorflow:23.10-tf2-py3
#FROM tensorflow/tensorflow:latest-gpu

# Install additional dependencies
RUN apt-get update 

RUN apt-get install -y \
    lsof \
    python3-pip

# Install TensorFlow Serving
RUN pip install tensorflow-serving-api[and-cuda]

# Install other required packages
RUN pip install grpcio numpy requests tqdm 

# Install Cloudmesh
RUN pip install cloudmesh-common cloudmesh-gpu cloudmesh-apptainer

# Set the working directory
#WORKDIR /app

# Copy your application code to the container
#COPY . /app

# Set the entrypoint command
#CMD ["python", "your_script.py"]





# %post
#     echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list && \
# curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add -
#     apt-get update 
#     apt install -y tensorflow-model-server
#     apt upgrade -y tensorflow-model-server

#     apt install -y lsof
#     apt install -y python3-pip
#     # pip install pip -U


    # #pip install tensorflow[and-cuda]
    # pip install tensorflow-serving-api[and-cuda]


    # pip install grpcio
    # pip install numpy
    # pip install requests
    # pip install tqdm

    
	# pip install cloudmesh-common
	# pip install cloudmesh-gpu
    # pip install cloudmesh-apptainer
    
    # #smartredis==0.3.1
