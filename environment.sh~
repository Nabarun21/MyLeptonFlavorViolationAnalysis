#!/bin/bash 

echo "Setting up CMSSW runtime environment"
eval `scramv1 ru -sh`

echo "Sourcing FSA environment"
source $CMSSW_BASE/src/FinalStateAnalysis/environment.sh

if [ -z $CONDOR_ID ]; then
    echo "Sourcing HiggsAnalysis/HiggsToTauTau environment"
    source $CMSSW_BASE/src/HiggsAnalysis/HiggsToTauTau/environment.sh
fi

#Is the analysis blinded?
export blind='YES'
export TARGET_LUMI_8TeV=19.4
export TARGET_LUMI_7TeV=4.9

#check if dev area is up to date
check_git_updates.sh
