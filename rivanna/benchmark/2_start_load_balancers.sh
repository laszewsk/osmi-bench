#!/bin/bash

. ./env.sh

if [ ! -n "$WORKDIR" ]; then
    echo "WORKDIR not set... exiting"
    exit
fi

if [ ! -n "$NUM_HOSTS" ]; then
    echo "NUM_HOSTS not set... setting NUM_HOSTS=1"
    NUM_HOSTS=1
fi

if [[ "${protocol}" == "HTTP" ]]; then
  CFG_FILE=haproxy-http.cfg
elif [[ "${protocol}" == "gRPC" ]]; then
  CFG_FILE=haproxy-grpc.cfg
else
  echo "ERROR: protocol ${protocol} not supported"
  exit 1
fi

echo "launching load balancer on all nodes"
$LAUNCH_PER_NODE singularity exec --bind `pwd`:/home --pwd /home \
    haproxy_latest.sif haproxy -d -f $CFG_FILE >& $WORKDIR/haproxy.log &
echo checking port 8443 to see if HAProxy is running...
sleep_countdown 5 
$LAUNCH_PER_NODE lsof -i :8443
