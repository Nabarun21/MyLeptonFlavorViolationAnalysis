import FinalStateAnalysis.Utilities.prettyjson as prettyjson
import os
import glob
from pdb import set_trace

def dump_xsec(jobid):
    json_files = [i for i in glob.glob('inputs/%s/*.json' % jobid) if 'data_' not in i]
    lumi_files = [i for i in glob.glob('inputs/%s/*.sum'  % jobid)  if 'data_' not in i]
    
    datasets = {}
    for json_file in json_files:
        dname = json_file.split('/')[-1].split('.')[0]
        datasets[dname] = {}
        datasets[dname]['numevts'] = prettyjson.loads(open(json_file).read())['n_evts']

    for lumi_file in lumi_files:
        dname = lumi_file.split('/')[-1].split('.')[0]
        datasets[dname]['lumi'] = float( open(lumi_file).read().strip() )

    out_format = '%60s'+'%15s'*3
    print out_format % ('dataset', '# evts', 'lumi [/pb]', 'xsec [pb]')
    for dataset, info in datasets.iteritems():
        print out_format % (dataset, '%.3f' % info['numevts'], '%.3f' % info['lumi'], '%.5f' % (info['numevts']/info['lumi']) )

#print '\n\n%s\n' % os.environ['jobid7']
#dump_xsec(os.environ['jobid7'])

print '\n\n%s\n' % os.environ['jobid']
dump_xsec(os.environ['jobid8'])
