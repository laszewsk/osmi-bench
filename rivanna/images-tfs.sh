banner() {
    message=$1
    echo "# #############################"
    echo "# $message"
    echo "# ##############################"
}
   

banner "CREATE IMAGES"

cd images

banner "create cloudmesh-tfs.sif"

apptainer build --force cloudmesh-tfs.sif cloudmesh-tfs.def 

# banner "create cloudmesh-tf.sif"

# apptainer build --force cloudmesh-tf.sif cloudmesh-tf.def

cd ..

