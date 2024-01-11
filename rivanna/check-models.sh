
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

# cd models
# banner small_lstm
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif saved_model_cli show --all --dir small_lstm/1

# banner medium_cnn
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif saved_model_cli show --all --dir medium_cnn/1

# banner large_tcnn   
# apptainer exec --nv ../images/cloudmesh-tensorflow.sif saved_model_cli show --all --dir large_tcnn/1

# banner "Checking completed"


cd models
banner small_lstm
apptainer exec --nv ../images/cloudmesh-tfs.sif saved_model_cli show --all --dir small_lstm/1

banner medium_cnn
apptainer exec --nv ../images/cloudmesh-tfs.sif saved_model_cli show --all --dir medium_cnn/1

banner large_tcnn   
apptainer exec --nv ../images/cloudmesh-tfs.sif saved_model_cli show --all --dir large_tcnn/1

banner "Checking completed"

