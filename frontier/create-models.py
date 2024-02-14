from cloudmesh.apptainer.apptainer import Apptainer
from cloudmesh.common.util import banner
from cloudmesh.common.StopWatch import StopWatch

import os
from pprint import pprint
# cd models
# banner small_lstm
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py small_lstm

# banner medium_cnn
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py medium_cnn

# banner large_tcnn
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py large_tcnn

# banner "Training completed" 

CONTAINER="cloudmesh-tfs.sif"
CONTAINER="../images/cloudmesh-tfs-23-10-nv.sif"


StopWatch.start("start-apptainer")
container = Apptainer()
images = container.images()
pprint (images)


os.chdir("models")  
pwd = os.getcwd()

container.start(name="tf", image=CONTAINER, gpu=0, home=pwd)
StopWatch.stop("start-apptainer")


banner("small_lstm")
StopWatch.start("small_lstm")
container.exec(name="tf", home=pwd, command="python3 train.py small_lstm")
StopWatch.stop("small_lstm")

banner("medium_cnn")
StopWatch.start("medium_cnn")
container.exec(name="tf", command="python3 train.py medium_cnn")
StopWatch.stop("medium_cnn")

banner("large_tcnn")
StopWatch.start("large_tcnn")
container.exec(name="tf",  command="python3 train.py large_tcnn")
StopWatch.stop("large_tcnn")

banner("Training completed") 

StopWatch.benchmark()