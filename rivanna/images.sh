banner() {
    message=$1
    echo "# #############################"
    echo "# $message"
    echo "# ##############################"
}
   

banner "CREATE IMAGES"

cd images

#banner "PULL IMAGE nvcr.io/nvidia/tensorflow:23.12-tf2-py3"
#apptainer pull docker://nvcr.io/nvidia/tensorflow:23.12-tf2-py3

banner "PULL IMAGE nvcr.io/nvidia/tensorflow:23.10-tf2-py3"
apptainer pull docker://nvcr.io/nvidia/tensorflow:23.10-tf2-py3

banner "PULL IMAGE haproxy"
apptainer pull docker://haproxy

#banner "PULL IMAGE tensorflow/serving:latest-gpu"
#apptainer pull docker://tensorflow/serving:latest-gpu

#banner "CREATE cloudmesh-tf"
#make image-tf

banner "CREATE cloudmesh-tfs"
make image-tfs

cd ..
