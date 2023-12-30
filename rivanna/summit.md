# Summit Instructions


1. Install software

        git clone https://code.ornl.gov/whb/osmi-bench.git

2. Get interactive debug node

        export PROJ_ID=ABC123 # change ABC123 to your project number
        bsub -Is -q debug -P ${PROJ_ID} -nnodes 1 -W 1:00 -J osmi $SHELL

3. Setup environment

        cd osmi-bench
        . benchmark/env.sh

4. Train models

        cd models
        jsrun -n1 python train.py small_lstm
        jsrun -n1 python train.py medium_cnn
        jsrun -n1 python train.py large_tcnn

Note: Edit benchmark/models.conf to modify paths to point to the individual, e.g., /ccs/home/whbrewer/osmi-bench/models/small_lstm

5. Start up tensorflow model server

        jsrun -n1 tensorflow_model_server --port=8500 --rest_api_port=0 --model_config_file=models.conf >& $MEMBERWORK/$PROJ_ID/tfs.log &

6. Test that server is running

        jsrun -n1 lsof -i :8500

7. Test benchmark

        jsrun -n1 python tfs_grpc_client.py -m small_lstm -b 32 -n 10 localhost:8500
