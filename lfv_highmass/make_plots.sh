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
      -analtype) shift;analtype=$2;shift;;
    esac
done

echo Preprocessing results for Analyzer: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
echo Type of Analyzer: $analtype

#make inclusive plots

python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/mPt.root --direc $analyzer --isLog --var mPt 
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/ePt.root --direc $analyzer --isLog --var ePt
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/mPFMET_Mt.root --direc $analyzer --isLog --var mtMuMet
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/ePFMET_Mt.root --direc $analyzer --isLog --var mtEMet
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/ePFMET_DeltaPhi.root --direc $analyzer  --var dphiEMet
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/mPFMET_DeltaPhi.root --direc $analyzer  --var dphiMuMet
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/h_collmass_pfmet.root --direc $analyzer --isLog  --var colmass
python plotter_inclusive.py --inputFile preprocessed_inputs/$analyzer$luminosity/inclusive/em_DeltaPhi.root --direc $analyzer  --var dphiemu
#python plotter_inclusive.py --inputFile preprocessed_inputs/inclusive/$analyzer//BDT_value.root --direc ztautau_CR --isLog --var BDT


#make preselection plots
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/h_collmass_pfmet.root --channel "me"  --prefix "presel" --blind 1 --isLog 1
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/mPt.root --channel "me"  --prefix "presel" --blind 1 --isLog 1 --var mPt
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/ePt.root --channel "me"  --prefix "presel" --blind 1 --isLog 1 --var ePt
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/mPFMET_Mt.root --channel "me"  --prefix "presel" --blind 1 --isLog 1 --var mtMuMet
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/ePFMET_Mt.root --channel "me"  --prefix "presel" --blind 1 --isLog 1 --var mtEMet
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/ePFMET_DeltaPhi.root --channel "me"  --prefix "presel" --blind 1  --var dphiEMet
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/mPFMET_DeltaPhi.root --channel "me"  --prefix "presel" --blind 1  --var dphiMuMet
python plotter.py --inputFile preprocessed_inputs/highmass35847/preselection/em_DeltaPhi.root --channel "me"  --prefix "presel" --blind 1  --var dphiemu
