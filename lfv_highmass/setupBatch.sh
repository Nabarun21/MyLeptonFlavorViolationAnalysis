export MEGAPATH=/hdfs/store/user/ndev
export farmout=1
export dryrun=1
export CutFlow=1
source jobid.sh 
export jobid=$jobid13


voms-proxy-init --voms cms --valid 100:00