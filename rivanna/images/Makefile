IMAGE_TF=cloudmesh-tensorflow
IMAGE_TFS=cloudmesh-tfs


images: image-tf image-tfs


image-tf: cloudmesh-tensorflow.def
	apptainer build --force ${IMAGE_TF}.sif ${IMAGE_TF}.def

shell-tf:
	singularity shell --nv ${IMAGE_TF}.sif

image-tfs: cloudmesh-tfs.def
	apptainer build --force ${IMAGE_TFS}.sif ${IMAGE_TFS}.def



# watch: 
# 	watch squeue --format=\"%.18i %.9P %.50j %.8u %.8T %.10M %.9l %.6D %R\" --me

# run:
# 	cd ${CODE_DIR}; mkdir -p outputs
# 	cd ${CODE_DIR}; singularity exec ${BIND} --nv cloudmask.sif bash -c "python cloudmask_v2.py --config=config-new.yaml"




# image-haproxy: haproxy_latest.sif
# 	mkdir -p image-singularity
# 	cd image-singularity; time singularity pull docker://haproxy


# run-localscratch:
# 	cd ${CODE_DIR}; mkdir -p outputs
# 	cd ${CODE_DIR}; singularity exec ${BIND_LOCALSCRATCH} --nv cloudmask.sif bash -c "python cloudmask_v2.py --config=config-new.yaml"

# #singularity exec --nv ${NAME}.sif papermill ${NAME}.ipynb ${NAME}_output.ipynb

# shell-localscratch:
# 	singularity ${BIND_LOCALSCRATCH} shell --nv ${IMAGE}

# shell-rivanna:
# 	singularity shell --nv ${IMAGE}



# cancel: stop

# stop:
# 	for i in "$$(squeue --user $$USER | awk 'NR>1{print $$1}')"; do scancel $$i ; done

# view:
# 	watch tail -n 50 *.err

# all: delete clean image submit view
