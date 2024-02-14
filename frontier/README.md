# Ubuntu

sudo apt install haproxy


# Rivanna OSMI-Bench

The Open Surrogate Model Inference (OSMI) Benchmark is a distributed inference benchmark
for analyzing the performance of machine-learned surrogate models and is described in its original form as "smiBench" in the following paper:

> Brewer, Wesley, Daniel Martinez, Mathew Boyer, Dylan Jude, Andy Wissink, Ben Parsons, Junqi Yin, and Valentine Anantharaj. "Production Deployment of Machine-Learned Rotorcraft Surrogate Models on HPC." In 2021 IEEE/ACM Workshop on Machine Learning in High Performance Computing Environments (MLHPC), pp. 21-32. IEEE, 2021.

Available from https://ieeexplore.ieee.org/abstract/document/9652868. Note that OSMI-Bench differs from SMI-Bench described in the paper only in that the models that are used in OSMI are trained on synthetic data, whereas the models in SMI were trained using data from proprietary CFD simulations. Also, the OSMI medium and large models are very similar architectures as the SMI medium and large models, but not identical.

# Instructions

1. Setup python

```bash
export BASE=/scratch/$USER

mkdir -p $BASE
cd $BASE
git clone https://github.com/laszewsk/osmi-bench.git
cd osmi-bench
```

2. Activate environment

This installs python, aptainer, and sets up soome conveneient environment variables

```bash
b1>
  cd rivanna
  source env.sh
```

3. Prepare the containers

```bash
rivanna>
  sh images.sh
  cd images
  make images
  cd ..
```

4. Interactive usage:


```bash
rivanna>
  sh login-1.sh
```sh

```bash
node>
  hostname
  nvidia-smi
  module load apptainer
```

5. Preparing model

Generate the modesl config file

```bash
python create_model_conf.py 
```

Generate the model in the models directory using:

```bash
node>
    sh create-models.sh
```

Check the model output:

```bash
node>
    sh check-models.sh
```

> Note: we stand in dir rivanna

Update name and path in models.conf file.

### Interactive Test Tensorflow serving

node is an interactive node that you for example can optain with the script

```bash
b1>
    sh login-1.sh
```

if you have not yet done so. It also requires that the models have been compiled as documented in the previous steps.

```bash
node>
    sh bin/convert-model-config.sh `pwd` benchmark/models.in.conf > benchmark/models.conf
```

Make sure name of model is defined in models parameter in tfs_grpc_client.py. 

Launch TensorFlow Serving:

```bash
node>
    apptainer shell --home `pwd` --nv images/cloudmesh-tfs-23-10-nv.sif    
```


```bash
apptainer>  
    rm -f tfs.log
    tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& tfs.log & 
```

Make sure TF Serving started correctly:

```bash
apptainer>
    lsof -i :8500 
```

*Should list a process with status LISTEN if working correctly.*

Send packets to be inference:

```bash
apptainer>
    cd benchmark
    python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
```

Output of timings should be in file results.csv.

### Scripted test with an instance

To run this with a shell script you can do AFTER the login-1.sh

```sh
node>
    source ./env.sh
    python test-tfs.py
```

script source: [test-tfs-gregor.py](https://github.com/laszewsk/osmi-bench/blob/main/rivanna/test-tfs-gregor.py)

### Scripted test with pythonic class for TFServing

To showcase how to use apptainer instences within a python class to execute commands and scripts into a container started from an image we have developed

script source: [test-tfs-gregor-2.py](https://github.com/laszewsk/osmi-bench/blob/main/rivanna/test-tfs-gregor-2.py)


To run this with a shell script you can do AFTER the login-1.sh

```
node>
    source ./env.sh
    python test-tfs-gregor-2.py
```


### GREGOR GOT TILL HERE

1. Using multiple GPUs via HAProxy load balancer

   To use multiple GPUs, we use HAProxy to round-robin the requests across the multiple GPUs. Assuming we have two GPUs we want to use, we first need to edit the file `haproxy-grpc.cfg`` to add lines for each of the inference servers:

        server tfs0 localhost:8500
        server tfs1 localhost:8501

(Note that it is currently setup for six servers, so the remaining four lines will need to be deleted or commented out for only two servers).

Now we need to launch TensorFlow Serving each one pinned to a specific GPU as follows:

```bash
b1>
    source env.sh
    sh login-2.sh
    pip install -r reaquirements.txt

node>
    nvidi-smi # to see if we have 2 gpus

node>
    cd benchmark # if not already in it
    CUDA_VISIBLE_DEVICES=0 apptainer run --home `pwd` --nv ../images/cloudmesh-tfs.sif tensorflow_model_server --port=8500 --model_config_file=models.conf > tfs0.log 2>&1 &
    CUDA_VISIBLE_DEVICES=1 apptainer run --home `pwd` --nv ../images/cloudmesh-tfs.sif tensorflow_model_server --port=8501 --model_config_file=models.conf > tfs1.log 2>&1 &
```

Assuming the HAProxy singularity apptainer has been downloaded, we can launch the container using the following command:

```bash
node>
    cd benchmark
    apptainer exec --bind `pwd`:/home --pwd /home haproxy_latest.sif haproxy -d -f haproxy-grpc.cfg > haproxy.log 2>&1 &
```


???    apptainer run --bind `pwd`:/home --pwd /home ../images/haproxy_latest.sif haproxy -d -f haproxy-grpc.cfg > haproxy.log 2>&1 &


gregor guesses:


    ```bash
    apptainer>
        cd benchmark
        python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8443
    ```


1. Fully automated launch process (from launch/batch node)

   If running on more than one GPU, will need to launch up multiple TF Serving processes, each one bound to a specific GPU. This is what the script `1_start_tfs_servers.sh` will do. `2_start_load_balancers.sh` will launch HAProxy load balancers on each compute node. `3_run_benchmark.sh` automates the launch of multiple concurrent client threads for a sweep of batch sizes. Note, that `1_start_tfs_servers_erf.sh` uses explicit resource (ERF) indexing to launch the servers correctly across multiple GPUs and nodes on Summit.

        # launch the TFS servers
        ./1_start_tfs_servers.sh
       
        # start the load balancer  
        ./2_start_load_balancers.sh
       
        # run the benchmark sweep
        ./3_run_benchmarks.sh # currently this is using tfs_grpc_client.py
                              # but should be changed to using benchmark.py in the future
       
        # run an individual benchmark
        python benchmark.py -b 32 -m small_lstm -n 1024

2. Production run. First update parameters in batch.lsf, then submit to LSF scheduler:

        bsub batch.lsf 
