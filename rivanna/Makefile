NAME=osmi

SHELL=/bin/bash

OS_TYPE=macos
OS_DIR=..
PROJECT_DIR=..

.PHONY: images image-docker project

benchmark:
	-make project
	-make run  

all: requirements data

# #####################################################################
# REQUIREMENTS
# #####################################################################

requirements:
	time pip install -r ../requirements.txt -U

# #####################################################################
# PROJECT MANAGEMENT
# #####################################################################

project: project_slurm generate

#setup:
#	python setup_env_and_yaml.py
#	source ~/ENV3/bin/activate && pip install -r /scratch/${USER}/mlcommons/benchmarks/${NAME}/experiments/rivanna/requirements.txt

generate: project-jobs-slurm.sh

run: submit

submit:
	-sh project-jobs-slurm.sh

project-slurm:
	mkdir -p project
	cms ee generate \
	        --source=inference.in.slurm \
	        --config=config.in.yaml \
	        --name=project \
	        --noos \
	        --os=USER,HOME \
		   	--nocm \
	        --output_dir=./project \
            --source_dir=. \
		    --verbose \
			--copycode="test-cm-hap-yaml.py"
	cms ee generate submit --name=project --job_type=slurm > project-jobs-slurm.sh
	cms ee list


kill: stop

stop:
	for i in "$$(squeue --user $$USER | awk 'NR>1{print $$1}')"; do scancel $$i ; done

inspect:
	$(eval D=$(shell ls project/$(ls -1) | head -n 1))
	echo ${D}
	$(shell emacs project/${D}/config.yaml project/${D}/job.slurm)

watch: status

status:
	watch squeue --format=\"%.18i %.9P %.50j %.8u %.8T %.10M %.9l %.6D %R\" --me

clean:
	@-rm -rf project project.json jobs-project.sh
	@-rm -rf '__pycache__'
	@-rm -rf *~

# PROJECT_USER=/project/bii_dsc_community/tma5gv
PROJECT_USER=/scratch/tma5gv

get-results:
	-rsync -av --progress rivanna:${PROJECT_USER}/${NAME}/target/rivanna/project .

# #####################################################################
# APPTAINER IMAGE BUILD
# #####################################################################

clean-images:
	@-rm -rf images/*.sif

images: image

image: image-haproxy image-osmi image-tfs

image-haproxy: # images/haproxy_latest.sif
	-cd images; time apptainer pull docker://haproxy

image-serving: # images/serving_latest-gpu.sif
	-cd images; time apptainer pull docker://tensorflow/serving:latest-gpu


image-osmi: # images/osmi.sif
	-cd images; apptainer build osmi.sif osmi.def

# broken?
image-tfs: # images/tfs.sif
	-cd images; time apptainer build tfs.sif tfs.def

# broken?
image-combined: # images/combined.sif
	-cd images; apptainer build combined.sif combined.def


# #####################################################################
# APPTAINER IMAGE SHELL
# #####################################################################

shell:
	apptainer ${BIND} shell --nv ${IMAGE}

shell-serving:
	apptainer ${BIND} shell --nv images/serving.sif

# #####################################################################
# THESE ARE NOT YET DONE AND JUST PLACEHOLDERS
# #####################################################################

# run-osmi:
# 	# cd images; make run


run-apptainer:
	cd images; make run

shell-apptainer:
	cd images; make shell

run-localscratch:
	cd images; make run-localscratch

shell-localscratch:
	cd images; make shell-localscratch

shell-rivanna:
	cd images; make shell-rivanna

run: run-apptainer

# #####################################################################
# THESE COMMANDS ARE ONLY FOR GREGOR
# #####################################################################

push:
	-git push
	ssh -tt rivanna "cd /scratch/thf2bn/mlcommons/benchmarks/${NAME}; ssh-add; git pull"



