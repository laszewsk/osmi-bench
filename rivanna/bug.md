bihead1>
    cd /scratch/thf2bn/cm/5/osmi-bench/rivanna
    sh login-1.sh
      # ijob -c 1  \
      #        --gres=gpu:a100:1 \
      #        --time=3:00:00 \
      #        --reservation=bi_fox_dgx \
      #        --partition=bii-gpu \
      #        --account=bii_dsc_community \
      #        --mem=64G 
node>
    source env.sh
    apptainer build --force images/cloudmesh-tfs.sif images/cloudmesh-tfs.def
    cd ..
    apptainer shell --home `pwd` --nv images/cloudmesh-tfs.sif
apptainer> 
    tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& tfs.log & 
    sleep 2
    lsof -i :8500 
    # should show listen
    cd benchmark
    python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500


(OSMI) thf2bn@rivanna:/scratch/thf2bn/cm/5/osmi-bench/rivanna/images$ cd ..
(OSMI) thf2bn@rivanna:/scratch/thf2bn/cm/5/osmi-bench/rivanna$ apptainer shell --home `pwd` --nv images/cloudmesh-tfs.sif
Apptainer> tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=benchmark/models.conf >& tfs.log &
[1] 241753
Apptainer> lsof -i :8500 
COMMAND      PID   USER   FD   TYPE   DEVICE SIZE/OFF NODE NAME
tensorflo 241753 thf2bn   33u  IPv4 14315360      0t0  TCP *:8500 (LISTEN)
Apptainer> cd benchmark
Apptainer> python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
2024-01-10 17:48:45.168665: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
localhost:8500
payload size in bytes: 9540864
  0%|                                                                                                                                                                                                     | 0/10 [00:01<?, ?it/s]
Traceback (most recent call last):
  File "tfs_grpc_client.py", line 67, in <module>
    results.append(stub.Predict(request))
  File "/scratch/thf2bn/cm/5/osmi-bench/rivanna/.local/lib/python3.8/site-packages/grpc/_channel.py", line 1160, in __call__
    return _end_unary_response_blocking(state, call, False, None)
  File "/scratch/thf2bn/cm/5/osmi-bench/rivanna/.local/lib/python3.8/site-packages/grpc/_channel.py", line 1003, in _end_unary_response_blocking
    raise _InactiveRpcError(state)  # pytype: disable=not-instantiable
grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
	status = StatusCode.UNKNOWN
	details = "2 root error(s) found.
  (0) UNKNOWN: JIT compilation failed.
	 [[{{function_node __inference__wrapped_model_4766}}{{node model/conv2d/Elu}}]]
	 [[StatefulPartitionedCall/_241]]
  (1) UNKNOWN: JIT compilation failed.
	 [[{{function_node __inference__wrapped_model_4766}}{{node model/conv2d/Elu}}]]
0 successful operations.
0 derived errors ignored."
	debug_error_string = "UNKNOWN:Error received from peer ipv4:127.0.0.1:8500 {grpc_message:"2 root error(s) found.\n  (0) UNKNOWN: JIT compilation failed.\n\t [[{{function_node __inference__wrapped_model_4766}}{{node model/conv2d/Elu}}]]\n\t [[StatefulPartitionedCall/_241]]\n  (1) UNKNOWN: JIT compilation failed.\n\t [[{{function_node __inference__wrapped_model_4766}}{{node model/conv2d/Elu}}]]\n0 successful operations.\n0 derived errors ignored.", grpc_status:2, created_time:"2024-01-10T17:48:48.768851528-05:00"}"