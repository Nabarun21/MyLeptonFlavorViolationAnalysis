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

python plotter_inclusive.py --lumi $luminosity --inputFile mPt.root --analyzer $analyzer --isLog --signals $my_signals --var mPt 
python plotter_inclusive.py --lumi $luminosity --inputFile ePt.root --analyzer $analyzer --isLog --signals $my_signals --var ePt
python plotter_inclusive.py --lumi $luminosity --inputFile mPFMET_Mt.root --analyzer $analyzer --isLog --signals $my_signals --var mtMuMet
python plotter_inclusive.py --lumi $luminosity --inputFile ePFMET_Mt.root --analyzer $analyzer --isLog --signals $my_signals --var mtEMet
python plotter_inclusive.py --lumi $luminosity --inputFile Met.root --analyzer $analyzer --isLog --signals $my_signals --var met
python plotter_inclusive.py --lumi $luminosity --inputFile ePFMET_DeltaPhi.root --analyzer $analyzer  --signals $my_signals --var dphiEMet
python plotter_inclusive.py --lumi $luminosity --inputFile mPFMET_DeltaPhi.root --analyzer $analyzer  --signals $my_signals --var dphiMuMet
python plotter_inclusive.py --lumi $luminosity --inputFile h_collmass_pfmet.root --analyzer $analyzer --isLog  --signals $my_signals --var colmass
python plotter_inclusive.py --lumi $luminosity --inputFile h_vismass.root --analyzer $analyzer --isLog  --signals $my_signals --var vismass
python plotter_inclusive.py --lumi $luminosity --inputFile em_DeltaPhi.root --analyzer $analyzer  --signals $my_signals --var dphiemu
#python plotter_inclusive.py --lumi $luminosity --inputFile preprocessed_inputs/inclusive/$analyzer//BDT_value.root --analyzer ztautau_CR --isLog --signals $my_signals --var BDT


#make preselection plots
python plotter.py --lumi $luminosity --inputFile h_collmass_pfmet.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals
python plotter.py --lumi $luminosity --inputFile h_vismass.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var vismass
python plotter.py --lumi $luminosity --inputFile mPt.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var mPt
python plotter.py --lumi $luminosity --inputFile ePt.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var ePt
python plotter.py --lumi $luminosity --inputFile mPFMET_Mt.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var mtMuMet
python plotter.py --lumi $luminosity --inputFile ePFMET_Mt.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var mtEMet
python plotter.py --lumi $luminosity --inputFile Met.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1 --isLog 1 --signals $my_signals --var met
python plotter.py --lumi $luminosity --inputFile ePFMET_DeltaPhi.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1  --signals $my_signals --var dphiEMet
python plotter.py --lumi $luminosity --inputFile mPFMET_DeltaPhi.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1  --signals $my_signals --var dphiMuMet
python plotter.py --lumi $luminosity --inputFile em_DeltaPhi.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "presel" --blind 1  --signals $my_signals --var dphiemu


#make preselection plots
python plotter.py --lumi $luminosity --inputFile h_collmass_pfmet.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "selected" --blind 1 --isLog 1 --higgsSF 1 --signals $my_signals
python plotter.py --lumi $luminosity --inputFile h_vismass.root --numCategories $numcategories --analyzer $analyzer --channel "me"  --suffix "selected" --blind 1 --isLog 1 --signals $my_signals --var vismass --higgsSF 1

