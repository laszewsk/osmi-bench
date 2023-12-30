

# Function to create a banner
banner() {
    local message="$1"
    local length=80
    local line=""

    for ((i=0; i<$length; i++)); do
        line+="#"
    done

    echo "# $line"
    echo "# $message"
    echo "# $line"
}

cd models
banner small_lstm
apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py small_lstm

banner medium_cnn
apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py medium_cnn

banner large_tcnn
apptainer exec --nv ../images/cloudmesh-tensorflow.sif python train.py large_tcnn

banner "Training completed" 