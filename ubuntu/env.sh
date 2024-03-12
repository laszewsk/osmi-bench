

hostname=$(hostname -f)
if echo "$hostname" | grep -q "crusher"; then
    echo "Host 'crusher'"
    
    module load cray-python
    module load rocm
    GPU=nvidia
    PYTHON=python
    CONTAINER="NONE"

elif echo "$hostname" | grep -q "summit"; then
    echo "Host 'summit'"
    module load open-ce/1.1.3-py38-0
    module load cuda/11.0.2
    GPU=rocm
    PYTHON=python
    CONTAINER="NONE"
else
    echo "Regular Linux machine"
    PYTHON=python3.11
    GPU=nvidia
    CONTAINER="apptainer"
fi



which $PYTHON
$PYTHON --version

$PYTHON -m venv ENV3-OSMI
source ENV3-OSMI/bin/activate

which python
python --version
pip install -v pip -U

pip install -v -r requirements-$GPU.txt
