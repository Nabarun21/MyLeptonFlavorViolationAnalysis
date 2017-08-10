#!/bin/bash
# Setup the UWHiggs dependencies in this working area 
# 
#  Usage: ./install.sh
#  
#  Author: Evan K. Friis, UW Madison

${CMSSW_BASE:?"Please run cmsenv before running install.sh"}

set -o errexit
set -o nounset

echo "Symlinking FinalStateAnalysis into working area"

pushd $CMSSW_BASE/src
if ! [ -L FinalStateAnalysis ]; then
  if ! [ -d FinalStateAnalysis ]; then
    ln -s UWHiggs/dependencies/FinalStateAnalysis FinalStateAnalysis
  fi
fi

echo "Checking out FSA dependencies"
pushd FinalStateAnalysis/recipe
# Do no do this - make sure you first run the FSA installation
#source environment.sh
#LUMI=1 LIMITS=1 PATPROD=${PATPROD:-0} ./recipe.sh

# The Nuke idea is great, but it needs fixing now...
#echo "Deleting unneeded PAT dependencies"
#FORCENUKE=1 ./nuke_pat_tools.sh

echo "Manually creating FinalStateAnalysis python symlinks"
./symlink_python.sh

echo "Installing python tools"
./install_python.sh

popd
popd

echo "Now run scram b -j 8 to compile"
