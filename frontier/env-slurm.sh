export USER_SCRATCH=/scratch/$USER
export USER_LOCALSCRATCH=/localscratch/$USER

export CLOUDMESH_CONFIG_DIR=$USER_SCRATCH/.cloudmesh
export APPTAINER_CACHEDIR=$USER_SCRATCH/.apptainer/cache

export OSMI_PROJECT=`pwd`
export OSMI_TARGET=$OSMI_PROJECT


mkdir -p $APPTAINER_CACHEDIR

echo "============================================================="
echo "USER_SCRATCH:        " $USER_SCRATCH
echo "USER_LOCALSCRATCH:   " $USER_LOCALSCRATCH
echo "CLOUDMESH_CONFIG_DIR:" $CLOUDMESH_CONFIG_DIR
echo "APPTAINER_CACHEDIR:  " $APPTAINER_CACHEDIR
echo "OSMI_PROJECT:        " $OSMI_PROJECT
echo "OSMI_TARGET:         " $OSMI_TARGET
echo "============================================================="

echo -n "Load   apptainer ... "
module load apptainer
echo "done"


echo -n "Load   python/3.11.4, cuda/12.2.2 ... " 
module load gcc/11.4.0  openmpi/4.1.4 python/3.11.4 cuda/12.2.2
echo "done"
#echo -n "Create $USER_SCRATCH/OSMI/bin/python ... "
#python -m venv $USER_SCRATCH/OSMI # takes about 5.2s
#echo "done"
echo -n "Load   Python $USER_SCRATCH/OSMI/bin/activate ... "
source $USER_SCRATCH/OSMI/bin/activate
#pip install --upgrade pip > /dev/null
echo "done"

echo "============================================================="
echo "Python version: " $(python --version)
echo "Python path:    " $(which python)
echo "Pip version:    " $(pip --version)
echo "============================================================="
