# OSMI-Bench

The Open Surrogate Model Inference (OSMI) Benchmark is a distributed inference benchmark
for analyzing the performance of machine-learned surrogate models and is described in its original form as "smiBench" in the following paper:

> Brewer, Wesley, Daniel Martinez, Mathew Boyer, Dylan Jude, Andy Wissink, Ben Parsons, Junqi Yin, and Valentine Anantharaj. "Production Deployment of Machine-Learned Rotorcraft Surrogate Models on HPC." In 2021 IEEE/ACM Workshop on Machine Learning in High Performance Computing Environments (MLHPC), pp. 21-32. IEEE, 2021.

Available from https://ieeexplore.ieee.org/abstract/document/9652868. Note that OSMI-Bench differs from SMI-Bench described in the paper only in that the models that are used in OSMI are trained on synthetic data, whereas the models in SMI were trained using data from proprietary CFD simulations. Also, the OSMI medium and large models are very similar architectures as the SMI medium and large models, but not identical. 

# Instructions

1. Setup environment - on Summit login node. Note that this benchmark is currently setup to `module load open-ce/1.1.3-py38-0` and `module load cuda/11.0.2`. Users on other systems may `pip install -r requirements.txt` (it may be preferable to install the packages one by one either by using `pip` or `conda`... sometimes one works better over the other). In addition to TensorFlow and gRPC, users also need to install TensorFlow Serving and if wanting to use multiple GPUs may install an HAProxy Singularity container as follows:

        > singularity pull docker://haproxy

    On x86_64 systems, TensorFlow Serving may be downloaded as a Singularity container using:

        > singularity pull docker://tensorflow/serving:latest-gpu

    On POWER9 systems, TensorFlow Serving may be installed via the conda repository at opence.mit.edu.

        > conda config --prepend channels https://opence.mit.edu
        > conda create -n osmi python=3.8
        > conda activate osmi
        > conda install tensorflow-serving

2. Interactive usage:

        > bsub -Is -P ARD143 -nnodes 1 -W 2:00 $SHELL

    *Note: replace ARD143 with subproject number*
    *Modify both models.conf and models.py to be consistent with your models*

3. Preparing model 

    Generate the model in the models directory using:

        > python train.py medium_cnn

    Check the model output:

        > saved_model_cli show --all --dir medium_cnn

    Update name and path in models.conf file. Make sure name of model is defined in models parameter in tfs_grpc_client.py. 

    Launch TensorFlow Serving:

        > singularity shell --home `pwd` --nv serving_latest-gpu.sif # (if using container)

        > tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=models.conf >& log & 

    Make sure TF Serving started correctly:

        > lsof -i :8500 

    *Should list a process with status LISTEN if working correctly.*

    Send packets to be inference:

        > python tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500

    Output of timings should be in file results.csv.

4. Using multiple GPUs via HAProxy load balancer

    To use multiple GPUs, we use HAProxy to round-robin the requests across the multiple GPUs. Assuming we have two GPUs we want to use, we first need to edit the file haproxy-grpc.cfg to add lines for each of the inference servers: 

        server tfs0 localhost:8500
        server tfs1 localhost:8501

(Note that it is currently setup for six servers, so the remaining four lines will need to be deleted or commented out for only two servers). 

Now we need to launch TensorFlow Serving each one pinned to a specific GPU as follows:

        > CUDA_VISIBLE_DEVICES=0 singularity run --home `pwd` --nv serving_latest-gpu.sif tensorflow_model_server --port=8500 --model_config_file=models.conf >& tfs0.log

        > CUDA_VISIBLE_DEVICES=1 singularity run --home `pwd` --nv serving_latest-gpu.sif tensorflow_model_server --port=8501 --model_config_file=models.conf >& tfs1.log &

Assuming the HAProxy singularity container has been downloaded, we can launch the container using the following command:

        > singularity exec --bind `pwd`:/home --pwd /home \
                      haproxy_latest.sif haproxy -d -f haproxy-grpc.cfg >& haproxy.log &

5. Fully automated launch process (from launch/batch node)

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

6. Production run. First update parameters in batch.lsf, then submit to LSF scheduler:

        bsub batch.lsf 
