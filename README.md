# MyLeptonFlavorViolationAnalysis
Analysis code for Higgs Lepton Flavor Violating decay search (inhertited from UWHiggs)

```
source environment.sh
cd lfv_highmass
```
To run analyzer, add `analyzer_target` in Rakefile #Analyzer needs to be named Analyzer_{analyzer_name}

```
./run.sh -target analyzer_target

```
After jobs finish running

```
source preprocess.sh -analyzer analyzer_name -lumi luminosity -jobid $job_id -analtype cutBased -num_cat 3 
#use 3 for default (2 categories 0-jet,1-jet plus third where everything else gets dumped)

```
For plotting:


```
source make_plots.sh -analyzer analyzer_name -lumi 35847 -analtype cutBased -num_cat 3 -signals 450,600,750,900

#signals is a string of mass values separated by comma, the signals you want plotted

```


