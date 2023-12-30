#!/bin/bash

### Benchmark sweep scenario
num_requests=32768
batch_sizes=(2048)
# Note: divide num_client_threads by NGPUS/node to get concurrency level
num_client_threads=(6)
###

if [  $# -lt 1 ] 
then 
  echo "Usage: $0 modelname"
  exit 1
else
  model=$1
fi 

. ./env.sh

if [[ ! -n "$WORKDIR" ]]; then
  echo "WORKDIR not set... exiting"
  exit
fi

if [[ "${protocol}" == "gRPC" ]]; then
  PORT=8500
  CLIENT=tfs_grpc_client.py
elif [[ "${protocol}" == "HTTP" ]]; then
  PORT=8501
  CLIENT=tfs_http_client.py
else
  echo "ERROR: protocol ${protocol} not supported"
  exit
fi

if [[ "${use_proxy}" = true ]]; then
  PORT=8443
fi

# Only output critical messages by TensorFlow
export TF_CPP_MIN_LOG_LEVEL=3

pids=()

OUTFILE=/mnt/bb/${USER}/results-n${NUM_HOSTS}.csv

echo "model: $model"

for BS in "${batch_sizes[@]}"; do
  echo batch-size: $BS

  NR=$(($num_requests/$BS))
  echo "# requests: $NR"

  for NTHREADS in "${num_client_threads[@]}"; do

    START=$(date +%s.%N)
    date
    echo num_client_threads: $NTHREADS

    # Launch concurrent clients
    for _ in $(seq -w 1 $NTHREADS); do
      CMD="$LAUNCH_PER_NODE python $CLIENT -m $model -b $BS -n $num_requests --redux -o $OUTFILE localhost:$PORT"
      echo $CMD && $CMD &
      pids+=($!)
    done

    # Barrier
    echo "Waiting for processes to finish to continue..."
    for pid in ${pids[*]}; do
      wait $pid
    done

    # Report timings - https://unix.stackexchange.com/a/334152/270049
    END=$(date +%s.%N)
    DIFF=$( echo "scale=3; (${END} - ${START})" | bc )
    echo "time taken (s): ${DIFF}"
    echo
  done
done

cat << EOF > .tmp/copy.sh
cp ${OUTFILE} ${WORKDIR}/${LSB_JOBID}-results-n${NUM_HOSTS}-\${OMPI_COMM_WORLD_RANK}.csv
EOF
# copy back per node results
$LAUNCH_PER_NODE bash .tmp/copy.sh

echo all done

