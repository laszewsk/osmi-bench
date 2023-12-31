CUDA_VISIBLE_DEVICES=0 apptainer run --home `pwd` --nv ../images/cloudmesh-tfs.sif tensorflow_model_server --port=8500 --model_config_file=models.conf > tfs0.log 2>&1 &
CUDA_VISIBLE_DEVICES=1 appteiner run --home `pwd` --nv ../images/cloudmesh-tfs.sif tensorflow_model_server --port=8501 --model_config_file=models.conf > tfs1.log 2>&1 &
sleep 0.5
tail -f tfs0.log 