##author Mauro Verzetti

import os

class cut_flow_tracker(object):
    def __init__(self, hist):
        self.labels   = [hist.GetXaxis().GetBinLabel(i+1) for i in range(hist.GetNbinsX())]        
        self.cut_flow = dict([ (i, False) for i in self.labels])
        self.hist     = hist
        self.evt_info = [-1, -1, -1]
        os.environ["CutFlow"]="1"
        #os.environ["SYNC"]="1"
       # print "cutflow =",os.environ["CutFlow"]
        self.disabled = 'CutFlow' not in os.environ
        self.sync_mode = 'SYNC' in os.environ
    def fill(self, label):
        self.cut_flow[label] = True

    def Fill(self, *labels):
        if self.disabled:
            return
        for label in labels:
            self.fill(label)

    def flush(self):
        if self.disabled:
            return
        final_i = -1
        for i, label in enumerate(self.labels):
            val = self.cut_flow[label]
            if val:
                self.hist.Fill(i+0.5)
                final_i = i
        if self.sync_mode:
            fails = ''
            try:
                fails = 'fails %s' % (self.labels[final_i+1])
            except IndexError:
                fails = 'passes the selection' #if len(self.labels) == final_i else 'passes the selection'
            print 'Event %i:%i:%i ' % tuple(self.evt_info) + fails
            
    def new_row(self, *args):
        if self.disabled:
            return
        if self.evt_info != list(args):
            self.flush()
            self.evt_info = list(args)
            self.cut_flow = dict([ (i, False) for i in self.labels])
