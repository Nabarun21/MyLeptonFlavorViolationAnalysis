from os import listdir
from os.path import isfile, join
import FinalStateAnalysis.MetaData.data13TeV_LFV as datadefs
import os

jobid=os.environ['jobid13']

files = [f for f in listdir(os.getcwd()+'/inputs/'+jobid) if isfile(join(os.getcwd()+'/inputs/'+jobid+'/', f))]
lumifile = [f for f in files if '.lumicalc.sum' in f]

samples = [f[:f.find('.lumicalc')] for f in lumifile if 'data_' not in f ]

for s in samples:
    weightfile= open('inputs/'+jobid+'/'+s+'_weight.log')
    weightstr = weightfile.readline().strip()
    print weightstr
    weight = float(weightstr[weightstr.find(': ')+2:])

    x_sec=datadefs.datadefs[s]['x_sec']

    mylumifile = open(os.getcwd()+'/inputs/'+jobid+'/'+s+'.lumicalc.sum', 'w')
    mylumifile.write(str(weight/x_sec))
    mylumifile.close()
    
    print s, weight, x_sec, weight/x_sec

