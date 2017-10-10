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
#      -analtype) shift;analtype=$2;shift;;
#      -isTT_DD) shift;isTT_DD=$2;shift;;
    esac
done

echo Making TTbar estimation comparison plots: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
#echo Type of Analyzer: $analtype
#echo is TTbar data driven: $isTT_DD


#make preselection plots colmass
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var colmass --inputFile h_collmass_pfmet.root --suffix presel --isLog 1
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var colmass --inputFile h_collmass_pfmet.root --suffix presel --isLog 1 --mc_v_mc

#make selection plots
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var colmass --inputFile h_collmass_pfmet.root --suffix selected --isLog 1
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var colmass --inputFile h_collmass_pfmet.root --suffix selected --isLog 1 --mc_v_mc

#make preselection plots vismass
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var vismass --inputFile h_vismass.root --suffix presel --isLog 1
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var vismass --inputFile h_vismass.root --suffix presel --isLog 1 --mc_v_mc

#make preselection plots
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var vismass --inputFile h_vismass.root --suffix selected --isLog 1
python plotTTbar.py --analyzer $analyzer --lumi $luminosity --var vismass --inputFile h_vismass.root --suffix selected --isLog 1 --mc_v_mc

