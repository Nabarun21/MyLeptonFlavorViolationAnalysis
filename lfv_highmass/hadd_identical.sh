#!/bin/bash                                                                                                                                   
for file in folder1/*;
do
   [ -f $file ] && echo $file
    f=$(echo $file|cut -d'/' -f 2)
    echo $f
    hadd -f output/$f $file folder2/$f
done;

