module load cray-python
module load rocm


source $PROJWORK/gen150/osmi/venv/bin/activate
virtualenv ENV3-WES

source ENV3-WES/bin/activate

which python
python --version
pip install -v pip -U

pip install -v -r requirements-wes.txt
cms help
