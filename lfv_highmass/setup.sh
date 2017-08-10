#!/bin/bash
export OVERRIDE_META_TREE_data_EM='em/metaInfo'

export IGNORE_LUMI_ERRORS=1

source jobid.sh
export jobid=$jobid13

echo $jobid
#export datasrc=/hdfs/store/user/$USER/  #$(ls -d /scratch/*/data/$jobid | awk -F$jobid '{print $1}')
#export EMGAPATH=/hdfs/store/user/$USER
export datasrc=/hdfs/store/user/ndev  #$(ls -d /scratch/*/data/$jobid | awk -F$jobid '{print $1}')
export MEGAPATH=/hdfs/store/user/ndev



rake "meta:getinputs[$jobid, $datasrc,em/metaInfo,em/summedWeights]"
rake "meta:getmeta[inputs/$jobid,em/metaInfo, 13,em/summedWeights]"
#./make_proxies.sh
#RakeOA "emta:getinputs[$jobid, $datasrc,ee/emtaInfo]"
#rake "emta:getemta[inputs/$jobid, ee/emtaInfo, 13]"

unset OVERRIDE_META_TREE_data_EM
unset IGNORE_LUMI_ERRORS
