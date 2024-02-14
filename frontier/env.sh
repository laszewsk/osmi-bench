module load cray-python
module load rocm
which python
python --version

python -m venv ENV3
source ENV3/bin/activate

which python
python --version
pip install pip -U

pip install -r requirements.txt
