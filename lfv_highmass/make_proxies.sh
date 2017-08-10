#!/bin/bash

# Generate the cython proxies used in the analyses

source jobid.sh

export jobid=$jobid13
#export datasrc=/hdfs/store/user/$USER/$jobid
export datasrc=/hdfs/store/user/ndev/$jobid
if [ -z $1 ]; then
    export afile=`find $datasrc/ | grep root | head -n 1`
else
    export afile=$1
fi

echo 'Filename:  '$afile

echo "Building cython wrappers from file: $afile"

#rake "make_wrapper[$afile, ee/final/Ntuple, EETree]"
#rake "make_wrapper[$afile, eet/final/Ntuple, EETauTree]"

#rake "make_wrapper[$afile, emme/final/Ntuple, EMMETree]"
rake "make_wrapper[$afile, em/final/Ntuple, EMTree]"

ls *pyx | sed "s|pyx|so|" | xargs -n 1 -P 10 rake 

echo "guji"
#export jobid=$jobidmt
#export datasrc=/hdfs/store/user/$USER/$jobid
#
#if [ -z $1 ]; then
#    export afile=`find $datasrc/ | grep root | head -n 1`
#else
#    export afile=$1
#fi
#
#rake "make_wrapper[$afile, mt/final/Ntuple, MuTauTree]"
#ls *pyx | sed "s|pyx|so|" | xargs -n 1 -P 10 rake 
