#!/usr/bin/env bash

#SBATCH --job-name={identifier}
#SBATCH --output=osmi-{identifier}-%u-%j.out
#SBATCH --error=osmi-{identifier}-%u-%j.err
{slurm.sbatch}
#SBATCH --nodes=1
#SBATCH --ntasks=6
#SBATCH --mem=64GB
#SBATCH --cpus-per-task=1
#SBATCH --time={ee.time}

PROGRESS() {
    echo "# ###############################################"
    echo "# cloudmesh status=$1 progress=$2 msg=$3 pid=$$"
    echo "# ###############################################"
}

PROGRESS "running" "configure" 1

nvidia-smi

PROGRESS "running" "configure" 2

MODELS_DIR=../../models

# ls -l $MODELS_DIR

export USER_SCRATCH=/scratch/$USER


RESULT_DIR=`pwd`

if [ -z "$OSMI_TARGET" ]; then
    echo "OSMI_TARGET is not set"
    exit 1
fi
export CONTAINER_DIR=$OSMI_TARGET/images

module purge
module load apptainer

MODEL={experiment.model}
CONTAINER=$CONTAINER_DIR/cloudmesh-tfs-23-10-nv.sif
CONTAINER2={data.tfs_sif}

echo "============================================================"
echo "PROJECT_ID: {identifier}"
echo "MODELS_DIR: $MODELS_DIR"
echo "MODEL: $MODEL"
echo "REPEAT: {experiment.repeat}"
echo "CONTAINER: $CONTAINER"
echo "OSMI_TARGET: $OSMI_TARGET"
echo "RESULT_DIR: $RESULT_DIR"

PROGRESS "running" "training" 3


cd $OSMI_TARGET
#pwd
#ls -lisa 
PROGRESS "running" "configure" 4

source env-slurm.sh

PROGRESS "running" "configure" 5

cd $RESULT_DIR

PROGRESS "running" "configure" 6


# time apptainer exec --nv $CONTAINER python train.py $MODEL

which python
python --version

PROGRESS "running" "configure" 7

python 1-test-cm-hap-yaml.py --config=config.yaml

PROGRESS "completed" "done" 100

#tr -cd '\11\12\15\40-\176' < $OUTPUT > tmp-output
#mv tmp-output $OUTPUT