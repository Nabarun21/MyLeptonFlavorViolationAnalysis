#!/bin/bash                                                                                                                                                                        

for f in results/ntuple9Nov/MuFakeRateAnalyzerMVA_fromeem/*;
  do
    echo $f
    filename=$(echo $f|cut -d'.' -f 1)
    ext=$(echo $f|cut -d'.' -f 2)
#    ext2=$(echo $f|cut -d'.' -f 3)
    echo $filename
    echo $ext
    echo $ext2
    z_to_ee='_zee'
    temp_name=$filename$z_to_ee'.'$ext
    echo $temp_name
    temp_name2=${temp_name/9/6}
    new_name=${temp_name2/_fromeem}
    echo $new_name
    echo
    cp "$f" "$new_name"  
  done;
