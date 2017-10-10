B1;95;0c#!/bin/bash                                                                                                                                   

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
      -num_cat) shift;num_cat=$2;shift;;
    esac
done

echo Preprocessing results for Optimizer: $analyzer
echo Current luminosity is :$luminosity

echo Current Jobid is: $jobid
echo Type of Optimizer: $analtype

#remove earlier preprocessed files with analyzer of same name
rm -r Optimizer_MuE_$analyzer$luminosity*


#copy results into current directory in the form wanted
cp -r results/$jobid/Optimizer_MuE_$analyzer Optimizer_MuE_$analyzer$luminosity

#combine relevant backgrounds
cp combine_backgrounds.sh Optimizer_MuE_$analyzer$luminosity
cd Optimizer_MuE_$analyzer$luminosity
source combine_backgrounds.sh
rm combine_backgrounds.sh
cd -


#get QCD (data-MC) in ss *2.30(SF)
python computeQCD_foroptim.py --aName $analyzer --lumi $luminosity --jobid $jobid --aType $analtype  --numCategories $num_cat


#folder for plotting
 mv QCD${analyzer}_foroptim.root Optimizer_MuE_$analyzer$luminosity/QCD.root



#final preprocessing : weight lumi, fill empty bins etc, create separate root file for each variable for plotting . FINAL_SEL_CATEGORY_WISE
python do_lumiweight_sel_optim.py --aName $analyzer --lumi $luminosity --jobid $jobid --aType $analtype  --numCategories $num_cat
