#!/usr/bin/env bash

#SBATCH --job-name={identifier}
#SBATCH --output=osmi-{identifier}-%u-%j.out
#SBATCH --error=osmi-{identifier}-%u-%j.err
{slurm.sbatch}
#SBATCH --partition=batch
#SBATCH --account=gen150_smartsim
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus=1
#SBATCH --time={time.{experiment.model}}

PROGRESS() {
    echo "# ###############################################"
    echo "# cloudmesh status=$1 progress=$2 msg=$3 pid=$$"
    echo "# ###############################################"
}

VENV=ENV3-NEW

PROGRESS "running" "modules" 1

source /opt/cray/pe/cpe/23.12/restore_lmod_system_defaults.sh

module load cray-python
module load rocm
module list

PROGRESS "running" "python" 1

source ../../../$VENV/bin/activate

which python
python --version
python ../../test-tf.py


PROGRESS "running" "gpus" 1

rocm-smi

PROGRESS "running" "configure" 2

MODELS_DIR=./models

#export USER_SCRATCH=/scratch/$USER


RESULT_DIR=`pwd`

#if [ -z "$OSMI_TARGET" ]; then
#    echo "OSMI_TARGET is not set"
#    exit 1
#fi
#export CONTAINER_DIR=$OSMI_TARGET/images/

#module purge
#module load apptainer

MODEL={experiment.model}
#CONTAINER=$CONTAINER_DIR/cloudmesh-tfs-23-10-nv.sif

echo "============================================================"
echo "PROJECT_ID: {identifier}"
echo "MODELS_DIR: $MODELS_DIR"
echo "MODEL: $MODEL"
echo "REPEAT: {experiment.repeat}"

PROGRESS "running" "training" 3

cd $MODELS_DIR

#time apptainer exec --nv $CONTAINER python train.py $MODEL
time python train.py $MODEL

PROGRESS "completed" "done" 100

#tr -cd '\11\12\15\40-\176' < $OUTPUT > tmp-output
#mv tmp-output $OUTPUT
