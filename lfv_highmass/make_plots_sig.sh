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
      -num_cat) shift;numcategories=$2;shift;;
      -signals) shift;my_signals=$2;shift;;
    esac
done

echo Preprocessing results for Analyzer: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
echo Type of Analyzer: $analtype
echo $numcategories categories
echo Signal smaples are : $my_signals
#make inclusive plots

python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile mPt.root --analyzer $analyzer --isLog --signals 200,300,450,600,750,900 --var mPt 
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile ePt.root --analyzer $analyzer --isLog --signals 200,300,450,600,750,900 --var ePt
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile mPFMET_Mt.root --analyzer $analyzer --isLog --signals 200,300,450,600,750,900 --var mtMuMet
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile ePFMET_Mt.root --analyzer $analyzer --isLog --signals 200,300,450,600,750,900 --var mtEMet
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile Met.root --analyzer $analyzer --isLog --signals 200,300,450,600,750,900 --var met
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile ePFMET_DeltaPhi.root --analyzer $analyzer  --signals 200,300,450,600,750,900 --var dphiEMet
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile mPFMET_DeltaPhi.root --analyzer $analyzer  --signals 200,300,450,600,750,900 --var dphiMuMet
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile h_collmass_pfmet.root --analyzer $analyzer --isLog  --signals 200,300,450,600,750,900 --var colmass
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile h_vismass.root --analyzer $analyzer --isLog  --signals 200,300,450,600,750,900 --var vismass
python signal_only_plotter_inclusive.py --lumi $luminosity --inputFile em_DeltaPhi.root --analyzer $analyzer  --signals 200,300,450,600,750,900 --var dphiemu
