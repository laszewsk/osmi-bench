VENV=ENV3-NEW


banner() {
    echo "################################################"
    echo "$@"
    echo "################################################"
}


banner "MODULE PURGE"

source /opt/cray/pe/cpe/23.12/restore_lmod_system_defaults.sh

banner "MODULE LOAD"

module load cray-python
module load rocm
module list

if [ ! -d "$VENV" ]; then

    banner "PYTHON INITIALIZE $VENV"
    
    python -m venv $VENV
    source ENV3-NEW/bin/activate
    which python
    python --version
    pip install pip -U
    pip install tensorflow-rocm

else

    banner "PYTHON REUSE $VENV"
    
    source ENV3-NEW/bin/activate
    which python
    python --version

fi

python test-tf.py

# #module load cray-python
# #cray-python/3.9.12.1
# #cray-python/3.9.13.1
# #cray-python/3.10.10

# #The following have been reloaded with a version change:
# #  1) cray-python/3.9.13.1 => cray-python/3.11.5
# #
# #The following have been reloaded with a version change:
# #  1) rocm/5.3.0 => rocm/6.0.0

# source /opt/cray/pe/cpe/23.12/restore_lmod_system_defaults.sh

# #module load cpe-cuda/23.12

# module load cray-python/3.9.13.1
# module load rocm/5.3.0

# # module load cray-python/3.11.5
# #module load rocm/5.5.1

# #https://pypi.org/project/tensorflow-rocm/2.11.1.550

# # module load rocm/6.0.0
# which python
# python --version

# python -m venv $VENV
# source $VENV/bin/activate

# banner "PYTHON"
# which python
# python --version
# banner "PIP"
# pip install -v pip -U

# ##pip install -v -r requirements.txt

# ##pip install protobuf==3.19.0
# banner tensorflow-rocm==2.11.1.550
# #pip install tensorflow-rocm==2.14.0.600

# #banner "PROTOBUF"
# #pip install protobuf==3.19.0

# banner "TENSORFLOW"
# pip install tensorflow==2.11


# #export PYTHONPATH="./.local/lib/python[version]/site-packages:$PYTHONPATH" 

# #python -c 'import tensorflow' 2> /dev/null && echo 'Success' || echo 'Failure'