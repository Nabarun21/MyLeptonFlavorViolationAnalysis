#!/bin/bash                                                                                                                                   

usage='Usage: -a <analyzer name>  -lumi <luminosity in pb> -ns <num_samples> -nf <sampling frequency> -ph <phase position> (-cpt <old pulse type> -cns\
 <old no. of samples> -cnf<old sampling freq>) '

args=`getopt rdlp: -- "$@"`
if test $? != 0
     then
         echo $usage
         exit 1
fi

eval set -- "$args"


for i
 do
    case "$i" in
      -analyzer) shift; analyzer=$2;shift;;
      -lumi) shift; luminosity=$2;shift;;
      -jobid) shift;jobid=$2;shift;;
      -analtype) shift;analtype=$2;shift;;
      -kinplots) shift;kinplots=$2;shift;;
      -sys) shift;sys=$2;shift;;
    esac
done

echo Preprocessing results for Analyzer: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
echo Type of Analyzer: $analtype

#remove earlier preprocessed files with analyzer of same name
rm -r LFVHEMuAnalyzerMVA$analyzer$luminosity*


#copy results into current directory in the form wanted
cp -r results/$jobid/LFVHEMuAnalyzerMVA$analyzer LFVHEMuAnalyzerMVA$analyzer$luminosity

#combine relevant backgrounds
cp combine_backgrounds.sh LFVHEMuAnalyzerMVA$analyzer$luminosity
cd LFVHEMuAnalyzerMVA$analyzer$luminosity
source combine_backgrounds.sh
rm combine_backgrounds.sh
cd -


#get QCD (data-MC) in ss *2.30(SF)
python computeQCD.py --aName $analyzer --lumi $luminosity --jobid $jobid --aType $analtype  


#folder for plotting
mv QCD$analyzer.root LFVHEMuAnalyzerMVA$analyzer$luminosity'plot'/QCD.root

#final preprocessing : weight lumi, fill empty bins etc, create separate root file for each variable for plotting .
do_lumiweight_inclusive.py
