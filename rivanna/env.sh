export USER_SCRATCH=/scratch/$USER
export USER_LOCALSCRATCH=/localscratch/$USER

export CLOUDMESH_CONFIG_DIR=$USER_SCRATCH/.cloudmesh
export APPTAINER_CACHEDIR=$USER_SCRATCH/.apptainer/cache

export OSMI_PROJECT=`pwd`
export OSMI_TARGET=$OSMI_PROJECT/rivanna

mkdir -p $APPTAINER_CACHEDIR

echo "============================================================="
echo "USER_SCRATCH:        " $USER_SCRATCH
echo "USER_LOCALSCRATCH:   " $USER_LOCALSCRATCH
echo "CLOUDMESH_CONFIG_DIR:" $CLOUDMESH_CONFIG_DIR
echo "APPTAINER_CACHEDIR:  " $APPTAINER_CACHEDIR
echo "OSMI_PROJECT:        " $OSMI_PROJECT
echo "OSMI_TARGET:         " $OSMI_TARGET
echo "============================================================="

echo "Load apptainer ..."
module load apptainer

echo "Create Python OSMI environment ..."
module load gcc/11.4.0  openmpi/4.1.4 python/3.11.4
python -m venv $USER_SCRATCH/OSMI # takes about 5.2s
source $USER_SCRATCH/OSMI/bin/activate
pip install --upgrade pip > /dev/null

echo "============================================================="
echo "Python version: " $(python --version)
echo "Python path:    " $(which python)
echo "Pip version:    " $(pip --version)
echo "============================================================="
