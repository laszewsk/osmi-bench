#!/bin/bash

. ./env.sh

if [[ ! -n "$WORKDIR" ]]; then
  echo "WORKDIR not set... exiting"
  exit 1
fi

if [[ ! -n "$NUM_HOSTS" ]]; then
  echo "NUM_HOSTS not set... exiting"
  echo "try setting `export NUM_HOSTS=1` then re-run this script"
  exit 1
fi

if [[ -f "models.conf" ]]; then
  OPTS="--model_config_file=models.conf"
else
  echo "ERROR: models.conf file missing"
  exit 1
fi

for i in $(seq -w 0 $((NUM_HOSTS-1)))
do
  for j in $(seq -w 0 $((NGPUS-1)))
  do 
    PORT=850${j}
    if [[ "${set_cuda_visible_devices}" = true ]]; then
      export CUDA_VISIBLE_DEVICES=${j}
    fi 
    if [[ "${protocol}" == "HTTP" ]]; then
      CMD="tensorflow_model_server --rest_api_port=$PORT $OPTS"
    elif [[ "${protocol}" == "gRPC" ]]; then
      CMD="$LAUNCHG tensorflow_model_server --port=$PORT --rest_api_port=0 $OPTS"
    else 
      echo "ERROR: protocol ${protocol} not supported"
      exit 1
    fi
    echo running: $CMD
    $CMD >& $WORKDIR/tfs-h$i-g$j.log &
    pids+=($!)
    ports+=($PORT)
  done
done

echo $NGPUS servers started on ports ${ports[*]}
echo PIDs are ${pids[*]}

echo checking ports 8500-8505 to see if TensorFlow Serving instances are running
echo sleeping 10 seconds to allow time for start up
sleep_countdown 10
$LAUNCH_PER_NODE lsof -i :8500-8505
