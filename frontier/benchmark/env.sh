protocol=gRPC
use_proxy=true

if [[ -d "/sw/summit" ]]; then
  echo "using Summit configuration"
  module load open-ce/1.1.3-py38-0
  module load cuda/11.0.2
  WORKDIR=$MEMBERWORK/$PROJ_ID
  host=$(hostname)
  set_cuda_visible_devices=false
  NGPUS=6
  if [[ -n "$LSB_DJOB_RANKFILE" ]]; then
    NUM_HOSTS=$(cat $LSB_DJOB_RANKFILE|uniq|wc -l)
  fi
  [[ -n "$LSB_DJOB_RANKFILE" ]] && NUM_HOSTS=$(cat $LSB_DJOB_RANKFILE|uniq|tail -n +2|wc -l)
  if [[ ${host::5} == "batch" ]]; then 
    LAUNCH="jsrun -n1"
    LAUNCHG="jsrun -n1 -g1"
    LAUNCH_PER_NODE="jsrun -n$NUM_HOSTS -r1 -a1 -c1 --smpiargs off"
  fi
else
  echo "ERROR: this HPC is not supported"
  exit 1
fi

sleep_countdown() {
  for sec in $(seq -w $1 -1 1); do
    echo -en "\r$sec"
    sleep 1
  done
  echo -en "\r"
}
