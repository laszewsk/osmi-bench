module load cray-python
module load rocm
which python
python --version

python -m venv ENV3-OSMI
source ENV3-OSMI/bin/activate

which python
python --version
pip install -v pip -U

pip install -v -r requirements.txt
