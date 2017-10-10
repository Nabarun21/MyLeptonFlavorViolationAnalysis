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
      -isTT_DD) shift;isTT_DD=$2;shift;;
      -num_cat) shift;num_cat=$2;shift;;
    esac
done

echo Preprocessing results for Analyzer: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
echo Type of Analyzer: $analtype
echo is TTbar data driven: $isTT_DD
#make inclusive plots

python plotter_inclusive_signalonly.py --inputFile mPt.root --is_TT_DD 0 --analyzer $analyzer  --var mPt 
python plotter_inclusive_signalonly.py --inputFile ePt.root --is_TT_DD 0 --analyzer $analyzer  --var ePt
python plotter_inclusive_signalonly.py --inputFile mPFMET_Mt.root --is_TT_DD 0 --analyzer $analyzer  --var mtMuMet
python plotter_inclusive_signalonly.py --inputFile ePFMET_Mt.root --is_TT_DD 0 --analyzer $analyzer  --var mtEMet
python plotter_inclusive_signalonly.py --inputFile Met.root --is_TT_DD 0 --analyzer $analyzer  --var met
python plotter_inclusive_signalonly.py --inputFile ePFMET_DeltaPhi.root --is_TT_DD 0 --analyzer $analyzer  --var dphiEMet
python plotter_inclusive_signalonly.py --inputFile mPFMET_DeltaPhi.root --is_TT_DD 0 --analyzer $analyzer  --var dphiMuMet
python plotter_inclusive_signalonly.py --inputFile h_collmass_pfmet.root --is_TT_DD 0 --analyzer $analyzer   --var colmass
python plotter_inclusive_signalonly.py --inputFile h_vismass.root --is_TT_DD 0 --analyzer $analyzer   --var vismass
python plotter_inclusive_signalonly.py --inputFile em_DeltaPhi.root --is_TT_DD 0 --analyzer $analyzer  --var dphiemu
python plotter_inclusive_signalonly.py --inputFile mEta.root --is_TT_DD 0 --analyzer $analyzer  --var meta
python plotter_inclusive_signalonly.py --inputFile eEta.root --is_TT_DD 0 --analyzer $analyzer  --var eeta
#python plotter_inclusive.py --inputFile preprocessed_inputs/inclusive/$analyzer//BDT_value.root --is_TT_DD 0 --analyzer ztautau_CR --isLog --var BDT

