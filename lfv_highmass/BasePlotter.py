import copy
import fnmatch
import re
import os
import math
import rootpy.plotting.views as views
from pdb import set_trace
from rootpy.plotting.hist import HistStack
import rootpy.plotting as plotting
from FinalStateAnalysis.MetaData.data_views import data_views
from FinalStateAnalysis.PlotTools.RebinView import RebinView
from FinalStateAnalysis.PlotTools.BlindView import BlindView,  blind_in_range
from FinalStateAnalysis.Utilities.struct import struct
import FinalStateAnalysis.Utilities.prettyjson as prettyjson
from FinalStateAnalysis.MetaData.data_styles import data_styles
from FinalStateAnalysis.PlotTools.Plotter  import Plotter
from FinalStateAnalysis.PlotTools.SubtractionView      import SubtractionView, PositiveView
from FinalStateAnalysis.PlotTools.MedianView     import MedianView
from FinalStateAnalysis.PlotTools.SystematicsView     import SystematicsView
from FinalStateAnalysis.StatTools.quad     import quad
import ROOT
import glob
from pdb import set_trace
from FinalStateAnalysis.PlotTools.THBin import zipBins

def create_mapper(mapping):
    def _f(path):
        for key, out in mapping.iteritems():
            if key == path:
                path = path.replace(key,out)
                print 'path', path
        return path
    return _f

def remove_name_entry(dictionary):
    return dict( [ i for i in dictionary.iteritems() if i[0] != 'name'] )

def histo_diff_quad(mc_err, *systematics):
    nbins = mc_err.GetNbinsX()
    clone = mc_err.Clone()
    sys_up = [i for i, _ in systematics]
    sys_dw = [i for _, i in systematics]
    #bin loop
    for ibin in range(nbins+2): #from uflow to oflow
        content = clone.GetBinContent(ibin)
        error   = clone.GetBinError(ibin)

        shifts_up = [abs(i.GetBinContent(ibin) - content) for i in sys_up]
        shifts_dw = [abs(i.GetBinContent(ibin) - content) for i in sys_dw]
        max_shift = [max(i, j) for i, j in zip(shifts_up, shifts_dw)]
        #print shifts_up, shifts_dw, max_shift, error, content
        
        new_err = quad(error, *max_shift)
        #print clone.GetTitle(), ibin, new_err, clone.GetBinContent(ibin)
        clone.SetBinError(ibin, new_err)

    return clone

def mean(histo):
    '''compute histogram mean because root is not able to'''
    nbins = histo.GetNbinsX()
    wsum = sum( histo.GetBinCenter(i)*histo.GetBinContent(i) for i in xrange(1, nbins+1))
    entries = sum(histo.GetBinContent(i) for i in xrange(1, nbins+1))
    #print histo.GetTitle(), wsum, entries, nbins, histo.GetEntries(), histo.Integral()
    return float(wsum)/entries

def name_systematic(name):
    '''makes functor that makes a name systematic (with postfix)'''
    return lambda x: x+name

def dir_systematic(name):
    '''makes functor that makes a directory systematic'''
    return lambda x: os.path.join(name,x)

def parse_cgs_groups(file_path):
    if not os.path.isfile(file_path):
        raise NameError('%s is not a file!' % file_path)
    
    groups = {}
    regex = re.compile('$ GROUP (?P<groupname>\w+) (?P<includes>[a-zA-Z\_\, ]+)')
    with open(file_path) as infile:
        for line in infile:
            match = regex.match(line)
            if match:
                groups[match.group('groupname')] = [ i.strip() for i in match.group('includes').split(',') ]
    return groups

def remove_empty_bins(histogram, weight, first = 0, last = 0):
    ret  = histogram.Clone()
    last = last if last else ret.GetNbinsX() + 1
    for i in range(first, last+1):
        if ret.GetBinContent(i) <= 0:
            ret.SetBinContent(i, 0.9200*weight) #MEAN WEIGHT
            ret.SetBinError(i, 1.8*weight)
    return ret     
           
def change_histo_nbins(histogram, first = 0, last = 0):
    nbins = int((last - first)/histogram.GetBinWidth(2))
    if nbins == histogram.GetNbinsX(): 
        return histogram
    else:
        name = "" 
        title =""
        name = histogram.GetName()
        title = histogram.GetTitle()
        newH = ROOT.TH1F(name, title, nbins , first, last)
        for i in range (1, nbins+1):
            newH.SetBinContent(i, histogram.GetBinContent(i))
            newH.SetBinError(i, histogram.GetBinError(i))
        return newH

def find_fill_range(histo):
    first, last = (0, 0)
    for i in range(histo.GetNbinsX() + 1):
        if histo.GetBinContent(i) > 0:
            if first:
                last = i
            else:
                first = i
    return first, last

class BasePlotter(Plotter):
    def __init__ (self,  files, outputdir, blind_region=None, forceLumi=-1, use_embedded=False,noData=False,blind_path="os/.*ass*"): 
        cwd = os.getcwd()
        self.period = '13TeV'
        self.sqrts  = 13
        jobid = os.environ['jobid13']
        self.use_embedded = use_embedded
        print "\nPlotting e mu for %s\n" % jobid
        files=files
        outputdir = outputdir
        #self.files     = glob.glob('results/%s/%s/*.root' % (jobid, self.files))
        lumifiles = glob.glob('inputs/%s/*.lumicalc.sum' % jobid)

        
        samples = [os.path.basename(i).split('.')[0] for i in files]
        self.blind_region=blind_region
        blinder=None
        if self.blind_region:
            # Don't look at the SS all pass region
#            blinder = lambda x: BlindView(x, "allfakes/os/.*ass*",blind_in_range(*self.blind_region))
            blinder = lambda x: BlindView(x, blind_path,blind_in_range(*self.blind_region))
        print files
        super(BasePlotter, self).__init__(files, lumifiles, outputdir, blinder, forceLumi=forceLumi)



        self.mc_samples = [
            'GluGluHToTauTau*', 
            'VBFHToTauTau*',
            'TT*',
            #'T*_t*',
            'WW*',
            'ZZ*',
            'WZ*',
            'DYJets*',
            'WJets*',
            'W1Jets*','W2Jets*',  'W3Jets*',  'W4Jets*',
            'DY1Jets*','DY2Jets*','DY3Jets*','DY4Jets*'
        ]
        
        if use_embedded:            
            self.mc_samples.pop()
            embedded_view, weight = self.make_embedded('os/h_collmass_pfmet')
            self.views['ZetauEmbedded'] = {
                'view' : embedded_view,
                'weight' : weight
                }
#        self.views['fakes'] = {'view' : self.make_fakes('t')} # comment in case of optimization study
 #       self.views['efakes'] = {'view' : self.make_fakes('e')}
  #      self.views['etfakes'] = {'view' : self.make_fakes('et')}

        #names must match with what defined in self.mc_samples
        self.datacard_names = {
            'GluGluHToTauTau*' : 'SMGG126'   , 
            'VBFHToTauTau*'     : 'SMVBF126'  ,
            'TT*'                  : 'ttbar'     ,
            'DYJets*'                  : 'DY'     ,
#            'T*_t*'                    : 'singlet'   ,
            '[WZ][WZ]_*'             : 'diboson'   ,
            'GluGlu_LFV_HToETau'  : 'LFVGG',
            'VBF_LFV_HToETau' : 'LFVVBF',
            'fakes' : 'fakes'
        }

        self.sample_groups = {#parse_cgs_groups('card_config/cgs.0.conf')
            'fullsimbkg' : ['SMGG126', 'SMVBF126','LFVGG', 'LFVVBF','ttbar','DY', 
                            'diboson', 'zjetsother'],
            'simbkg' : ['SMGG126', 'SMVBF126', 'LFVGG', 'LFVVBF', 'ttbar','DY',
                        'diboson', 'zjetsother'],
            'realtau' : ['diboson', 'ttbar', 'DY', 'SMGG126', 'SMVBF126','LFVGG', 'LFVVBF'],
            'Zee' : ['zjetsother']
            }

        self.systematics = {
            'PU_Uncertainty' : {
                'type' : 'yield',
                '+' : dir_systematic('p1s'),
                '-' : dir_systematic('m1s'),
                'apply_to' : ['fullsimbkg'],
            },
            ##'E_Trig' : {
            ##    'type' : 'yield',
            ##    '+' : dir_systematic('trp1s'),
            ##    '-' : dir_systematic('trm1s'),
            ##    'apply_to' : ['simbkg'],
            ##},
            ####'E_ID' : { ## to comment in case of optimization study
            ####    'type' : 'yield',
            ####    '+' : dir_systematic('eidp1s'),
            ####    '-' : dir_systematic('eidm1s'),
            ####    'apply_to' : ['simbkg'],
            ####},
            ####'E_Iso' : { ## to comment in case of optimization study
            ####    'type' : 'yield',
            ####    '+' : dir_systematic('eisop1s'),
            ####    '-' : dir_systematic('eisom1s'),
            ####    'apply_to' : ['simbkg'],
            ####},
            ##'JES' : {
            ##    'type' : 'yield',
            ##    '+' : lambda x: os.path.join('jes_plus', x)+'_jes_plus' ,
            ##    '-' : lambda x: os.path.join('jes_minus', x)+'_jes_minus' ,
            ##    'apply_to' : ['fullsimbkg'],
            ##},
            ##'TES' : {
            ##    'type' : 'shape',
            ##    '+' : lambda x: os.path.join('tes_plus', x)+'_tes_plus' ,
            ##    '-' : lambda x: os.path.join('tes_minus', x)+'_tes_minus' ,
            ##    'apply_to' : ['realtau'],
            ##},
            ####'EES' : {
            ####    'type' : 'shape',
            ####    '+' : lambda x: os.path.join('ees_plus', x) +'_ees_plus' ,
            ####    '-' : lambda x: os.path.join('ees_minus', x)+'_ees_minus' ,
            ####    'apply_to' : ['simbkg'],
            ####},
            ##'UES' : { ## to comment in case of optimization study
            ##    'type' : 'yield',
            ##    '+' : name_systematic('_ues_plus'),
            ##    '-' : name_systematic('_ues_minus'),
            ##    'apply_to' : ['fullsimbkg'],
            ##},
            ##'shape_FAKES' : { ## to comment in case of optimization study
            ##    'type' : 'shape',
            ##    '+' : dir_systematic('Up'),
            ##    '-' : dir_systematic('Down'),
            ##    'apply_to' : ['fakes']#,'efakes','etfakes'],
            ##},
            ##'norm_etaufake' : { ## was shape etaufake
            ##    'type' : 'yield',
            ##    '+' : dir_systematic('etaufakep1s'),
            ##    '-' : dir_systematic('etaufakem1s'),
            ##    'apply_to' : ['Zee']#,'efakes','etfakes'],
            ##},
            ##'shape_ZeeMassShift' : { ## to comment in case of optimization study
            ##    'type' : 'shape',
            ##    '+' : name_systematic('_Zee_p1s'),
            ##    '-' : name_systematic('_Zee_m1s'),
            ##    'apply_to' : ['Zee']#,'efakes','etfakes'],
            ##},
            ####'stat' : {
            ####    'type' : 'stat',
            ####    '+' : lambda x: x,
            ####    '-' : lambda x: x,
            ####    'apply_to' : ['fakes','simbkg'],
            ####    #'apply_to' : [ 'simbkg'],#['fakes','simbkg'],  ## no fakes in case of optimization study
            ####}
        }

        
    def make_fakes(self, obj='t'):
        '''Sets up the fakes view'''
        print 'making fakes for %s' %obj
        data_view = self.get_view('data')
        tfakes = views.SubdirectoryView(data_view, 'tLoose')
        efakes = views.SubdirectoryView(data_view, 'eLoose')
        etfakes= views.SubdirectoryView(data_view, 'etLoose')
        central_fakes=SubtractionView(views.SumView(tfakes,efakes),etfakes, restrict_positive=True)
        mc_views = self.mc_views()
        if self.use_embedded:            
            mc_views.append(self.get_view('ZetauEmbedded'))
        mc_sum = views.SumView(*mc_views)
        mc_sum_t = views.SubdirectoryView(mc_sum, 'tLoose')
        mc_sum_e = views.SubdirectoryView(mc_sum, 'eLoose')
        mc_sum_et = views.SubdirectoryView(mc_sum, 'etLoose')
        allmc=SubtractionView(views.SumView(mc_sum_t,mc_sum_e),mc_sum_et, restrict_positive=True)

        fakes_view = SubtractionView(central_fakes, allmc, restrict_positive=True)
        #fakes_view =central_fakes
        style = data_styles['Fakes*']
        return views.TitleView(
            views.StyleView(
                fakes_view,
                **remove_name_entry(style)
            ),
            style['name']
        )
        #MedianView(highv=up_fakes, lowv=dw_fakes, centv=central_fakes, maxdiff=True),
        
    def make_embedded(self, normalization_path):
        '''Configures the embedded view'''
        embedded_view = self.get_view('ZetauEmbedded_Run2012*', 'unweighted_view')
        zjets_view = self.get_view('Z*jets_M50_skimmedTT')

        embedded_histo = embedded_view.Get(normalization_path)
        zjets_histo = zjets_view.Get(normalization_path)

        embed_int = embedded_histo.Integral()
        zjets_int = zjets_histo.Integral()
        

        scale_factor = zjets_int / embed_int
        
        scaled_view = views.TitleView(
            views.StyleView(views.ScaleView(embedded_view, scale_factor),
                **remove_name_entry(data_styles['ZetauEmbedded'])
            ),
            'Z #rightarrow #tau#tau (embedded)'
        )
        return scaled_view, scale_factor

    def simpleplot_mc(self, folder, signal, variable, rebin=1, xaxis='',
                      leftside=True, xrange=None, preprocess=None, sort=True,forceLumi=-1):
        ''' Compare Monte Carlo signal to bkg '''
        #path = os.path.join(folder, variable)
        #is_not_signal = lambda x: x is not signame
        #set_trace()
        
        mc_stack_view = self.make_stack(rebin, preprocess, folder)
        mc_stack=mc_stack_view.Get(variable)
        
        #self.canvas.SetLogy(False)
        mc_stack.SetTitle('')
        mc_stack.Draw()
        
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)

        if xrange:
            mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
            mc_stack.Draw()

        signalview=[]
        mymax=0
        for sig in signal:
                signal_view=self.get_view(sig)
                if preprocess:
                    signal_view=preprocess(signal_view)
                signal_view=self.get_wild_dir(
                    self.rebin_view(signal_view,rebin),folder)
                signal=signal_view.Get(variable)
                signalview.append(signal)
                signal.Draw("SAME")
                if signal.GetBinContent(signal.GetMaximumBin()) > mymax:
                    mymax = signal.GetBinContent(signal.GetMaximumBin())
                    
                self.keep.append(signal)
        if mymax > mc_stack.GetMaximum():
            mc_stack.SetMaximum(mymax*1.2)

        self.keep.append(mc_stack)
        
        all_var=[]
        all_var.extend([mc_stack]) 
        all_var.extend(signalview) 
            
        self.add_legend(all_var, leftside, entries=len(mc_stack)+len(signalview))
 
    def plot_data(self, folder, variable, rebin=1, xaxis='',
                  leftside=True, xrange=None, preprocess=None):
        ''' Compare Monte Carlo signal to bkg '''
        #path = os.path.join(folder, variable)
        #is_not_signal = lambda x: x is not signame
        #set_trace()
        data_view = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.get_wild_dir(
            self.rebin_view(data_view, rebin),
            folder
            )
        data = data_view.Get(variable)
        data.Draw()

         
        data.GetXaxis().SetTitle(xaxis)

        if xrange:
            data.GetXaxis().SetRangeUser(xrange[0], xrange[1])
            data.Draw()
        self.keep.append(data)
        
        
        
    def compare_data(self, folder, variable, folder2, rebin=1, xaxis='',
                     leftside=True, xrange=None, preprocess=None, show_ratio=False, ratio_range=0.2,rescale=1. ):
        ''' Compare Monte Carlo signal to bkg '''
        #path = os.path.join(folder, variable)
        #is_not_signal = lambda x: x is not signame
        #set_trace()
        data_view = self.get_view('data')
        data_view2 = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.get_wild_dir(
            self.rebin_view(data_view, rebin),
            folder
            )
        data_view2 = self.get_wild_dir(
            self.rebin_view(data_view2, rebin),
            folder2
            )
        data = data_view.Get(variable)
        data2 = data_view2.Get(variable)
         
        data.GetXaxis().SetTitle(xaxis)
        #if (data.Integral()!=0 and data2.Integral()!=0) :
        #    data.Scale(1./data.Integral())
        #    data2.Scale(1./data2.Integral())
        data.Draw()
        data.GetYaxis().SetRangeUser(0, data.GetBinContent(data.GetMaximumBin())*1.2)
        if xrange:
            data.GetXaxis().SetRangeUser(xrange[0], xrange[1])
            data.Draw()

        data2.Draw("SAME")
        data2.SetMarkerColor(2)
        data2.Draw("SAME")
       

        if show_ratio:
            self.add_sn_ratio_plot(data2, data, xrange, ratio_range)

        self.keep.append(data)
        self.keep.append(data2)
        
        
    def add_ratio_bandplot(self, data_hist, mc_stack, err_hist,  x_range=None, ratio_range=0.2):
        #resize the canvas and the pad to fit the second pad
        self.canvas.SetCanvasSize( self.canvas.GetWw(), int(self.canvas.GetWh()*1.3) )
        self.canvas.cd()
        self.pad.SetPad(0, 0.33, 1., 1.)
        self.pad.Draw()
        self.canvas.cd()
        #create lower pad
        self.lower_pad = plotting.Pad('low', 'low', 0, 0., 1., 0.33)
        self.lower_pad.Draw()
        self.lower_pad.cd()

        
        mc_hist    = None
        if isinstance(mc_stack, plotting.HistStack):
            mc_hist = sum(mc_stack.GetHists())
        else:
            mc_hist = mc_stack
        data_clone = data_hist.Clone()
        data_clone.Divide(mc_hist)
        
        band = err_hist.Clone()
        
        err = []
        ibin =1 
        while ibin < band.GetXaxis().GetNbins()+1:
            if mc_hist.GetBinContent(ibin) <> 0 : 
                err.append((ibin, band.GetBinError(ibin)/band.GetBinContent(ibin)))
            ibin+=1

        band.Divide(mc_hist.Clone())
        #print err
        for ibin in err:
            band.SetBinError(ibin[0], ibin[1])

        if not x_range:
            nbins = data_clone.GetNbinsX()
            x_range = (data_clone.GetBinLowEdge(1), 
                       data_clone.GetBinLowEdge(nbins)+data_clone.GetBinWidth(nbins))
        else:
            data_clone.GetXaxis().SetRangeUser(*x_range)


        ref_function = ROOT.TF1('f', "1.", *x_range)
        ref_function.SetLineWidth(2)
        ref_function.SetLineStyle(2)
        
        data_clone.Draw()
 
        if ratio_range:
            data_clone.GetYaxis().SetRangeUser(1-ratio_range, 1+ratio_range)
        ref_function.Draw('same')
        band.SetMarkerStyle(0)
        band.SetLineColor(1)
        band.SetFillStyle(3001)
        band.SetFillColor(1)

        band.Draw('samee2')
       
        self.keep.append(data_clone)
        self.keep.append(band)
        self.keep.append(ref_function)
        self.pad.cd()
        return data_clone

 
    def add_ratio_diff(self, data_hist, mc_stack, err_hist,  x_range=None, ratio_range=0.2):
        #resize the canvas and the pad to fit the second pad
        self.canvas.SetCanvasSize( self.canvas.GetWw(), int(self.canvas.GetWh()*1.3) )
        self.canvas.cd()
        self.pad.SetPad(0, 0.33, 1., 1.)
        self.pad.Draw()
        self.canvas.cd()
        #create lower pad
        self.lower_pad = plotting.Pad('low', 'low', 0, 0., 1., 0.33)
        self.lower_pad.Draw()
        self.lower_pad.cd()

        
        mc_hist    = None
        if isinstance(mc_stack, plotting.HistStack):
            mc_hist = sum(mc_stack.GetHists())
        else:
            mc_hist = mc_stack
        data_clone = data_hist.Clone()
        data_clone.Sumw2()
        data_clone.Add(mc_hist, -1)
        data_clone.Divide(mc_hist)
        
        band = err_hist.Clone()
        
        err = []
        ibin =1 
        while ibin < band.GetXaxis().GetNbins()+1:
            if mc_hist.GetBinContent(ibin) <> 0 : 
                err.append((ibin, band.GetBinError(ibin)/band.GetBinContent(ibin)))
                
            ibin+=1

        band.Divide(mc_hist.Clone())
        #print err
        for ibin in err:
            band.SetBinError(ibin[0], ibin[1])

        if self.blind_region:
            for ibin in err:
                if ibin >= band.FindBin(self.blind_region[0]) and ibin <= band.FindBin(self.blind_region[1]):
                    band.SetBinError(ibin, 10)

        if not x_range:
            nbins = data_clone.GetNbinsX()
            x_range = (data_clone.GetBinLowEdge(1), 
                       data_clone.GetBinLowEdge(nbins)+data_clone.GetBinWidth(nbins))
        else:
            data_clone.GetXaxis().SetRangeUser(*x_range)


        ref_function = ROOT.TF1('f', "0.", *x_range)
        ref_function.SetLineWidth(2)
        ref_function.SetLineStyle(2)
        
        data_clone.Draw()
 
        if ratio_range:
            data_clone.GetYaxis().SetRangeUser(-ratio_range, +ratio_range)
        ref_function.Draw('same')
        band.SetMarkerStyle(0)
        band.SetLineColor(1)
        band.SetFillStyle('x')
        band.SetFillColor(1)

        band.Draw('samee2')
       
        self.keep.append(data_clone)
        self.keep.append(band)
        self.keep.append(ref_function)
        self.pad.cd()
        return data_clone

    def add_shape_systematics(self, histo, path, view, folder_systematics = [], name_systematics = []):
        '''Adds shape systematics
        add_shape_systematics(self, histo, path, view, folder_systematics = [], name_systematics = []) --> histo
        histo is the central value 
        path is the path if the central value histo
        view contains all the systematics. 
        folder_systematics is a list of tuples with the folders containing shifts (up, down)
        name_systematics is a list of tuples containing the postfix to obtain the shifts (up, down)
        '''
         
        systematics = []
        for sys_up, sys_dw in folder_systematics:
            h_up = view.Get(os.path.join(sys_up, path))
            h_dw = view.Get(os.path.join(sys_dw, path))
            systematics.append(
                (h_up, h_dw)
                )

        #check if we have to apply met uncertainties
        for sys_up, sys_dw in name_systematics:
            h_up = view.Get(path + sys_up)
            h_dw = view.Get(path + sys_dw)
            systematics.append(
                (h_up, h_dw)
            )
        

        #ADD systematics
        return histo_diff_quad(histo, *systematics)
        



    def add_histo_error(self, histo, histoerr):
        clone = histo.GetStack().Last().Clone('errhist')
        for bin in range(1,clone.GetXaxis().GetNbins()):
            error = histoerr.GetBinError(bin)*clone.GetBinContent(bin)/histoerr.GetBinContent(bin) if histoerr.GetBinContent(bin) <>0 else histoerr.GetBinError(bin)
            clone.SetBinError(bin, error )
       
        return clone


    def plot_with_bkg_uncert (self, folder, variable, rebin=1, xaxis='',
                              leftside=True, xrange=None, preprocess=None,
                              show_ratio=False, ratio_range=0.2, sort=True, obj=['e1', 'e2'], plot_data=False):


        #xsection uncertainties
        #names must match with what defined in self.mc_samples
        xsec_unc_mapper = {
            'TTJets*' : 0.026,
            'T*_t*' : 0.041,
            '[WZ][WZ]Jets' : 0.056, #diboson
            'W*Jets*' : 0.035, #WJets
            'Z*jets_M50_skimmedLL' : 0.300, # theoretical 0.032
            'Z*jets_M50_skimmedTT' : 0.032,
        }


        path = os.path.join(folder,variable)

        #make MC views with xsec error
        mc_views_nosys = self.mc_views(rebin, preprocess)
        mc_views = []
        for view, name in zip(mc_views_nosys, self.mc_samples):
            new = SystematicsView(
                view,
                xsec_unc_mapper.get(name, 0.) #default to 0
            )
            mc_views.append(new)

        #make MC stack
        mc_stack_view = views.StackView(*mc_views, sorted=sort) 
        mc_stack = mc_stack_view.Get( path )

        #make histo clone for err computation
        mc_sum_view = views.SumView(*mc_views)
        mc_err = mc_sum_view.Get( path )
        
        #Add MC-only systematics
        folder_systematics = [
            ('p1s', 'm1s'), #PU correction
        ]

        met_systematics = [ #it was without plus
           ## ('_jes_plus', '_jes_minus'), 
           ## ('_mes_plus', '_mes_minus'), 
           ## #('_ees_plus', '_ees_minus'), 
           ## ('_tes_plus', '_tes_minus'), 
           ## ('_ues_plus', '_ues_minus'), 
        ]

        name_systematics = [] #which are not MET
        #add MET sys if necessary
        if 'collmass' in variable.lower() or \
           'met' in variable.lower():
            if not variable.lower().startswith('type1'):
                name_systematics.extend(met_systematics) # TO ADD WHEN RERUN WITH THE NEW BINNING 

        #add them
        
        mc_err = self.add_shape_systematics(
            mc_err, 
            path, 
            mc_sum_view, 
            folder_systematics,
            name_systematics)

        #add jet category uncertainty
        jetcat_unc_mapper = {
            0 : 0.017,
            1 : 0.035,
            2 : 0.05
        }
        #find inn which jet category we are
        regex = re.compile('\/\d\/')
        found = regex.findall(path)
        jet_unc = 0.
        if found:
            njet = int(found[0].strip('/'))
            jet_unc = jetcat_unc_mapper.get(njet, 0. )
        mc_err = SystematicsView.add_error(mc_err, jet_unc)

        #check if we are using the embedded sample
        if self.use_embedded:
            embed_view = self.get_view('ZetauEmbedded')
            if preprocess:
                embed_view = preprocess(embed_view)
            embed_view = RebinView( embed_view, rebin)
            embed = embed_view.Get(path)

            #add xsec error
            embed = SystematicsView.add_error( embed, xsec_unc_mapper['Z*jets_M50_skimmedTT'])
 
            #add them to backgrounds
            mc_stack.Add(embed)
            mc_err += embed
            
            mc_sum_view = views.SumView(mc_sum_view, embed_view)

        #Add MC and embed systematics
        folder_systematics = [
         #   ('trp1s', 'trm1s'), #trig scale factor
        ]
        
        #print folder_systematics
        #Add as many eid sys as requested
        for name in obj:
            folder_systematics.extend([
               # ('%sidp1s'  % name, '%sidm1s'  % name), #eID scale factor
               # ('%sisop1s' % name, '%sisom1s' % name), #e Iso scale factor
                
            ])
        
            
        mc_err = self.add_shape_systematics(
            mc_err, 
            path, 
            mc_sum_view, 
            folder_systematics)

        #add lumi uncertainty
        mc_err = SystematicsView.add_error( mc_err, 0.026 )

        mc_err.Sumw2()
        no_fakes=True
        if not no_fakes:
            #get fakes
            fakes_view = self.get_view('fakes')
            if preprocess:
                fakes_view = preprocess(fakes_view)
            fakes_view = RebinView(fakes_view, rebin)
            fakes = fakes_view.Get(path)
                
            fakes = self.add_shape_systematics(
                fakes, 
                path, 
                fakes_view, 
                #[('Up','Down')]
            )
            fakes = SystematicsView.add_error(fakes, 0.30)
            #add them to backgrounds
            mc_stack.Add(fakes)
            
            mc_err.Add(fakes)

        #set_trace()
         
        #####get efakes
        ##efakes_view = self.get_view('efakes')
        ##if preprocess:
        ##    efakes_view = preprocess(efakes_view)
        ##efakes_view = RebinView(efakes_view, rebin)
        ##efakes = efakes_view.Get(path)
        ##
        ##efakes = self.add_shape_systematics(
        ##    efakes, 
        ##    path, 
        ##    efakes_view, 
        ##    [('Up','Down')]
        ##)
        #####add them to backgrounds
        ##mc_stack.Add(efakes)
        ##
        ##mc_err.Sumw2()
        ##mc_err.Add(efakes)
        ###set_trace()
        ##etfakes_view = self.get_view('etfakes')
        ##if preprocess:
        ##    etfakes_view = preprocess(etfakes_view)
        ##etfakes_view = RebinView(etfakes_view, rebin)
        ##etfakes = etfakes_view.Get(path)
        ##
        ##etfakes = self.add_shape_systematics(
        ##    etfakes, 
        ##    path, 
        ##    etfakes_view, 
        ##    [('Up','Down')]
        ##)
        #####add them to backgrounds
        ##mc_stack.Add(etfakes)
        ##
        ##mc_err.Sumw2()
        ##mc_err.Add(etfakes)
        ###set_trace()

        #draw stack
        mc_stack.Draw()
        self.keep.append(mc_stack)
        
        #set cosmetics
        self.canvas.SetLogy(True)
        ##self.canvas.SetGridx(True)
        ##self.canvas.SetGridy(True)
        ##self.pad.SetGridx(True)
        ##self.pad.SetGridy(True)
        
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
        if xrange:
            mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
            mc_stack.Draw()
              
        #set cosmetics 
        mc_err.SetMarkerStyle(0)
        mc_err.SetLineColor(1)
        mc_err.SetFillStyle('x')
        mc_err.SetFillColor(1)
        mc_err.Draw('pe2 same')
        self.keep.append(mc_err)


        
        #Get signal
        signals = [
            'GluGlu_LFV_HToETau_M125_13TeV_powheg_pythia8',
            'VBF_LFV_HToETau_M125_13TeV_powheg_pythia8'
        ]
        sig = []
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = RebinView(sig_view, rebin)
            if not plot_data:
                sig_view = views.ScaleView(sig_view, 100)
            
            histogram = sig_view.Get(path)
            histogram.Draw('same')
            self.keep.append(histogram)
            sig.append(histogram)
        for lfvh in sig:
            if lfvh.GetMaximum() > mc_stack.GetMaximum():
                mc_stack.SetMaximum(1.2*lfvh.GetMaximum()) 

        if plot_data==True:
            # Draw data
            data_view = self.get_view('data')
            if preprocess:
                data_view = preprocess( data_view )
            data_view = self.rebin_view(data_view, rebin)
            data = data_view.Get(path)

            data.Draw('same')
            print 'data', data.Integral()
            self.keep.append(data)

            ## Make sure we can see everything
            if data.GetMaximum() > mc_stack.GetMaximum():
                mc_stack.SetMaximum(1.2*data.GetMaximum()) 
                if lfvh.GetMaximum() > mc_stack.GetMaximum():
                    mc_stack.SetMaximum(1.2*lfvh.GetMaximum()) 
    
        if plot_data:
            self.add_legend([data, mc_stack], leftside, entries=len(mc_stack.GetHists())+1)
            #self.add_legend([data, sig[0], sig[1], mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        else:
            self.add_legend([sig[0], sig[1], mc_stack], leftside, entries=len(mc_stack.GetHists())+1)
        if show_ratio and plot_data:
            self.add_ratio_plot(data, mc_err, xrange, ratio_range, True) # add_ratio_diff(data, mc_stack, mc_err, xrange, ratio_range)
            #self.add_ratio_plot(data, mc_stack, xrange, ratio_range, True) # add_ratio_diff(data, mc_stack, mc_err, xrange, ratio_range)
            
                       
##-----

    def plot_without_uncert (self, folder, variable, rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                              show_ratio=False, ratio_range=0.2, sort=True, obj=['e1', 'e2']):
        
        

        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)

        mc_stack = mc_stack_view.Get(variable)
        mc_stack.Draw()
        
        self.canvas.SetLogy(True)
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
        if xrange:
            mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
            mc_stack.Draw()
        self.keep.append(mc_stack)
        

        finalhisto= mc_stack.GetStack().Last().Clone()
        finalhisto.Sumw2()

        histlist = mc_stack.GetHists();
        bkg_stack = mc_stack_view.Get(variable)
        bkg_stack.GetStack().RemoveLast()## mettere il check se c'e` il fake altirmenti histo=mc_stack.GetStack().Last().Clone()
        histo=bkg_stack.GetStack().Last().Clone()
        histo.Sumw2()
        
        fake_p1s_histo=None
      
        if not folder.startswith('tLoose') and not folder.startswith('eLoose') and not folder.startswith('etLoose') :
            isFakesIn= False
            ##isEFakesIn=False
            isETFakesIn=False
            if 'Fakes' in self.mc_samples:
                self.mc_samples.remove('Fakes')  
                if 'finalDYLL' in self.mc_samples: self.mc_samples.remove('finalDYLL')
                isFakesIn=True
            ##if 'eFakes' in self.mc_samples:
            ##    self.mc_samples.remove('eFakes')  
            ##    if 'finalDYLL' in self.mc_samples:  self.mc_samples.remove('finalDYLL')
            ##    isEFakesIn=True
            ##if 'etFakes' in self.mc_samples:
            ##    self.mc_samples.remove('etFakes')  
            ##    if 'finalDYLL' in self.mc_samples:  self.mc_samples.remove('finalDYLL')
            ##    isETFakesIn=True
                

        ibin =1
            
        if isFakesIn:
            self.mc_samples.append('Fakes')
           # self.mc_samples.append('etFakes')
            self.mc_samples.append('finalDYLL')
       ## if isEFakesIn:
       ##     self.mc_samples.append('eFakes')
       ##     if not 'finalDYLL' in self.mc_samples:  self.mc_samples.append('finalDYLL')
       ## if isETFakesIn:
       ##     self.mc_samples.append('etFakes')
       ##     if not 'finalDYLL' in self.mc_samples:  self.mc_samples.append('finalDYLL')


        finalhisto.Draw('samee2')
        finalhisto.SetMarkerStyle(0)
        finalhisto.SetLineColor(1)
        finalhisto.SetFillStyle(3001)
        finalhisto.SetFillColor(1)

        
        self.keep.append(finalhisto)
        # Draw data
        data_view = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.get_wild_dir(
            self.rebin_view(data_view, rebin),
            folder
            )
        data = data_view.Get(variable)
        data.Draw('same')
        print 'data', data.Integral()
        self.keep.append(data)
        ## Make sure we can see everything
        if data.GetMaximum() > mc_stack.GetMaximum():
            mc_stack.SetMaximum(1.2*data.GetMaximum()) 
            
            # # Add legend
        self.add_legend([data, mc_stack], leftside, entries=len(mc_stack.GetHists())+1)
        if show_ratio:
            self.add_ratio_diff(data, mc_stack, finalhisto, xrange, ratio_range)
            
    def write_shapes(self, folder, variable, output_dir, br_strenght=1,
                     rebin=1, last = 400,  preprocess=None): #, systematics):
        '''Makes shapes for computing the limit and returns a list of systematic effects to be added to unc.vals/conf 
        make_shapes(folder, variable, output_dir, [rebin=1, preprocess=None) --> unc_conf_lines (list), unc_vals_lines (list)
        '''
        output_dir.cd()
        path = os.path.join(folder,variable)

        # Draw data
        data_view = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.rebin_view(data_view, rebin)
        data = data_view.Get(path)
       
        data=change_histo_nbins(data, 0, last)
        first_filled, last_filled = find_fill_range(data)
        data.SetName('data_obs')
        data.Write()

        #make MC views with xsec error
        bkg_views  = dict(
            [(self.datacard_names[i], j) for i, j in zip(self.mc_samples, self.mc_views(rebin, preprocess))]
        )
        bkg_weights = dict(
            [(self.datacard_names[i], self.get_view(i, 'weight')) for i in self.mc_samples]
        )
        #cache histograms, since getting them is time consuming
        bkg_histos = {}
        for name, view in bkg_views.iteritems():
            mc_histo = view.Get(path)
            mc_histo = change_histo_nbins(mc_histo, 0, last)
            first_filled_bkg, last_filled_bkg= find_fill_range(mc_histo)
            print name, first_filled_bkg, last_filled_bkg, mc_histo.GetXaxis().GetNbins()
            bkg_histos[name] = mc_histo.Clone()
            mc_histo = remove_empty_bins(
                mc_histo, bkg_weights[name],
                first_filled_bkg, last_filled_bkg)
            mc_histo.SetName(name)
            mc_histo.Write()

        if self.use_embedded:            
            view = self.get_view('ZetauEmbedded')
            weight = self.get_view('ZetauEmbedded', 'weight')
            if preprocess:
                view = preprocess(view)
            view = self.rebin_view(view, rebin)
            name = self.datacard_names['ZetauEmbedded']
            bkg_weights[name] = weight
            bkg_views[name] = view
            mc_histo = view.Get(path)
            mc_histo = change_histo_nbins(mc_histo, 0, last)
            first_filled_bkg, last_filled_bkg= find_fill_range(mc_histo)
            bkg_histos[name] = mc_histo.Clone()
            mc_histo = remove_empty_bins(
                mc_histo, weight,
                first_filled_bkg, last_filled_bkg)
            mc_histo.SetName(name)
            mc_histo.Write()
          
        fakes_view = self.get_view('fakes') 
        d_view = self.get_view('data')
        weights_view = views.SumView(
            views.SubdirectoryView(d_view, 'tLoose'),
            views.SubdirectoryView(d_view, 'eLoose'),
            views.SubdirectoryView(d_view, 'etLoose')
            )
        if preprocess:
            fakes_view = preprocess(fakes_view)    
            weights_view = preprocess(weights_view)
        weights = weights_view.Get(os.path.join(folder,'weight'))
        #print folder
        fakes_view = self.rebin_view(fakes_view, rebin)
        bkg_views['fakes'] = fakes_view
        bkg_weights['fakes'] = mean(weights)
        fake_shape = bkg_views['fakes'].Get(path)
        fake_shape = change_histo_nbins(fake_shape, 0, last)
        bkg_histos['fakes'] = fake_shape.Clone()
        bkg_histos['fakes'] =change_histo_nbins(bkg_histos['fakes'] , 0, last)
        first_filled_bkg, last_filled_bkg = find_fill_range(bkg_histos['fakes'])
        fake_shape = remove_empty_bins(
            fake_shape, bkg_weights['fakes'],
            first_filled_bkg, last_filled_bkg)
        fake_shape.SetName('fakes')
        fake_shape.Write()

        #Get signal
        signals = [
            'ggHiggsToETau',
            'vbfHiggsToETau',
        ]
        for name in signals:
            sig_view = self.get_view(name)
            card_name = self.datacard_names[name]
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = views.ScaleView(
                RebinView(sig_view, rebin),
                br_strenght
                )
            weights = self.get_view(name, 'weight')
            bkg_views[card_name] = sig_view
            bkg_weights[card_name] = weights
            histogram = sig_view.Get(path)
            histogram = change_histo_nbins(histogram, 0, last)
            bkg_histos[card_name] = histogram.Clone()
            first_filled_bkg, last_filled_bkg = find_fill_range(bkg_histos[card_name])
            histogram = remove_empty_bins(
                histogram, bkg_weights[card_name],
                first_filled_bkg, last_filled_bkg)
            histogram.SetName(card_name)
            histogram.Write()


        unc_conf_lines = []
        unc_vals_lines = []
        category_name  = output_dir.GetName()
        for unc_name, info in self.systematics.iteritems():
            targets = []
            for target in info['apply_to']:
                if target in self.sample_groups:
                    targets.extend(self.sample_groups[target])
                else:
                    targets.append(target)

            unc_conf = 'lnN' if info['type'] == 'yield' or info['type'] == 'stat' else 'shape'            
            #stat shapes are uncorrelated between samples
            if info['type'] <> 'stat':
                unc_conf_lines.append('%s %s' % (unc_name, unc_conf))
            shift = 0.
            path_up = info['+'](path)
            path_dw = info['-'](path)
            for target in targets:
                up      = bkg_views[target].Get(
                    path_up
                )
                down    = bkg_views[target].Get(
                    path_dw
                )
                if info['type'] == 'yield':
                    central = bkg_histos[target]
                    integral = central.Integral()
                    integral_up = up.Integral()
                    integral_down = down.Integral()
                    if integral == 0  and integral_up == 0 and integral_down ==0 :
                        shift=shift
                    else:
                        shift = max(
                            shift,
                            (integral_up - integral) / integral,
                            (integral - integral_down) / integral
                        )
                elif info['type'] == 'shape':
                    #remove empty bins also for shapes 
                    #(but not in general to not spoil the stat uncertainties)
                    first_filled_bkg,last_filled_bkg= find_fill_range( bkg_histos[target])
                    up = remove_empty_bins(
                        up, bkg_weights[target],
                        first_filled_bkg, last_filled_bkg)
                    first_filled_bkg, last_filled_bkg= find_fill_range( bkg_histos[target])
                    down = remove_empty_bins(
                        down, bkg_weights[target],
                        first_filled_bkg, last_filled_bkg)
                    up.SetName('%s_%sUp' % (target, unc_name))
                    down.SetName('%s_%sDown' % (target, unc_name))
                    up.Write()
                    down.Write()
                elif info['type'] == 'stat':
                    nbins = up.GetNbinsX()
                    up.Rebin(nbins)
                    yield_val = up.GetBinContent(1)
                    yield_err = up.GetBinError(1)
                    print target, yield_val, yield_err, 
                    if yield_val==0:
                        unc_value = 0.
                    else:
                        unc_value = 1. + (yield_err / yield_val)
                    stat_unc_name = '%s_%s_%s' % (target, category_name, unc_name)
                    unc_conf_lines.append('%s %s' % (stat_unc_name, unc_conf))
                    unc_vals_lines.append(
                        '%s %s %s %.2f' % (category_name, target, stat_unc_name, unc_value)
                    )
                else:
                    raise ValueError('systematic uncertainty type:"%s" not recognised!' % info['type'])

            if info['type'] <> 'stat':
                shift += 1
                unc_vals_lines.append(
                    '%s %s %s %.2f' % (category_name, ','.join(targets), unc_name, shift)
                )

        return unc_conf_lines, unc_vals_lines
                       
    ##-----

    def write_shapes_for_yields(self, folder, variable, output_dir, br_strenght=1,
                                rebin=1, preprocess=None): #, systematics):
        '''Makes shapes for computing the limit and returns a list of systematic effects to be added to unc.vals/conf 
        make_shapes(folder, variable, output_dir, [rebin=1, preprocess=None) --> unc_conf_lines (list), unc_vals_lines (list)
        '''
        output_dir.cd()
        path = os.path.join(folder,variable)

        # Draw data
        data_view = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.rebin_view(data_view, rebin)
        data = data_view.Get(path)
        first_filled, last_filled = find_fill_range(data)
        data.SetName('data_obs')
        data.Write()

        #make MC views with xsec error
        bkg_views  = dict(
            [(self.datacard_names[i], j) for i, j in zip(self.mc_samples, self.mc_views(rebin, preprocess))]
        )
        bkg_weights = dict(
            [(self.datacard_names[i], self.get_view(i, 'weight')) for i in self.mc_samples]
        )
        #cache histograms, since getting them is time consuming
        bkg_histos = {}
        for name, view in bkg_views.iteritems():
            mc_histo = view.Get(path)
            first_filled_bkg, last_filled_bkg= find_fill_range(mc_histo)
            print name, first_filled_bkg, last_filled_bkg, mc_histo.GetXaxis().GetNbins()
            bkg_histos[name] = mc_histo.Clone()
            #mc_histo = remove_empty_bins(
            #    mc_histo, bkg_weights[name],
            #    first_filled_bkg, last_filled_bkg)
            mc_histo.SetName(name)
            mc_histo.Write()

        if self.use_embedded:            
            view = self.get_view('ZetauEmbedded')
            weight = self.get_view('ZetauEmbedded', 'weight')
            if preprocess:
                view = preprocess(view)
            view = self.rebin_view(view, rebin)
            name = self.datacard_names['ZetauEmbedded']
            bkg_weights[name] = weight
            bkg_views[name] = view
            mc_histo = view.Get(path)
            first_filled_bkg, last_filled_bkg= find_fill_range(mc_histo)
            bkg_histos[name] = mc_histo.Clone()
            #mc_histo = remove_empty_bins(
            #    mc_histo, weight,
            #    first_filled_bkg, last_filled_bkg)
            mc_histo.SetName(name)
            mc_histo.Write()
          
        fakes_view = self.get_view('fakes') 
        d_view = self.get_view('data')
        weights_view = views.SumView(
            views.SubdirectoryView(d_view, 'tLoose'),
            views.SubdirectoryView(d_view, 'eLoose'),
            views.SubdirectoryView(d_view, 'etLoose')
            )
        if preprocess:
            fakes_view = preprocess(fakes_view)    
            weights_view = preprocess(weights_view)
        weights = weights_view.Get(os.path.join(folder,'weight'))
        #print folder
        fakes_view = self.rebin_view(fakes_view, rebin)
        bkg_views['fakes'] = fakes_view
        bkg_weights['fakes'] = mean(weights)
        fake_shape = bkg_views['fakes'].Get(path)
        bkg_histos['fakes'] = fake_shape.Clone()
        first_filled_bkg, last_filled_bkg = find_fill_range(bkg_histos['fakes'])
        #fake_shape = remove_empty_bins(
        #    fake_shape, bkg_weights['fakes'],
        #    first_filled_bkg, last_filled_bkg)
        fake_shape.SetName('fakes')
        fake_shape.Write()

        #Get signal
        signals = [
            'ggHiggsToETau',
            'vbfHiggsToETau',
        ]
        for name in signals:
            sig_view = self.get_view(name)
            card_name = self.datacard_names[name]
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = views.ScaleView(
                RebinView(sig_view, rebin),
                br_strenght
                )
            weights = self.get_view(name, 'weight')
            bkg_views[card_name] = sig_view
            bkg_weights[card_name] = weights
            histogram = sig_view.Get(path)
            bkg_histos[card_name] = histogram.Clone()
            first_filled_bkg, last_filled_bkg = find_fill_range(bkg_histos[card_name])
            #histogram = remove_empty_bins(
            #    histogram, bkg_weights[card_name],
            #    first_filled_bkg, last_filled_bkg)
            histogram.SetName(card_name)
            histogram.Write()


        unc_conf_lines = []
        unc_vals_lines = []
        category_name  = output_dir.GetName()
        for unc_name, info in self.systematics.iteritems():
            targets = []
            for target in info['apply_to']:
                if target in self.sample_groups:
                    targets.extend(self.sample_groups[target])
                else:
                    targets.append(target)

            unc_conf = 'lnN' if info['type'] == 'yield' or info['type'] == 'stat' else 'shape'            
            #stat shapes are uncorrelated between samples
            if info['type'] <> 'stat':
                unc_conf_lines.append('%s %s' % (unc_name, unc_conf))
            shift = 0.
            path_up = info['+'](path)
            path_dw = info['-'](path)
            for target in targets:
                up      = bkg_views[target].Get(
                    path_up
                )
                down    = bkg_views[target].Get(
                    path_dw
                )
                if info['type'] == 'yield':
                    central = bkg_histos[target]
                    integral = central.Integral()
                    integral_up = up.Integral()
                    integral_down = down.Integral()
                    if integral == 0  and integral_up == 0 and integral_down ==0 :
                        shift=shift
                    else:
                        shift = max(
                            shift,
                            (integral_up - integral) / integral,
                            (integral - integral_down) / integral
                        )
                elif info['type'] == 'shape':
                    #remove empty bins also for shapes 
                    #(but not in general to not spoil the stat uncertainties)
                    first_filled_bkg,last_filled_bkg= find_fill_range( bkg_histos[target])
                    ##up = remove_empty_bins(
                    ##    up, bkg_weights[target],
                    ##    first_filled_bkg, last_filled_bkg)
                    first_filled_bkg, last_filled_bkg= find_fill_range( bkg_histos[target])
                    ##down = remove_empty_bins(
                    ##    down, bkg_weights[target],
                    ##    first_filled_bkg, last_filled_bkg)
                    up.SetName('%s_%sUp' % (target, unc_name))
                    down.SetName('%s_%sDown' % (target, unc_name))
                    up.Write()
                    down.Write()
                elif info['type'] == 'stat':
                    nbins = up.GetNbinsX()
                    up.Rebin(nbins)
                    yield_val = up.GetBinContent(1)
                    yield_err = up.GetBinError(1)
                    print target, yield_val, yield_err, 
                    if yield_val==0:
                        unc_value = 0.
                    else:
                        unc_value = 1. + (yield_err / yield_val)
                    stat_unc_name = '%s_%s_%s' % (target, category_name, unc_name)
                    unc_conf_lines.append('%s %s' % (stat_unc_name, unc_conf))
                    unc_vals_lines.append(
                        '%s %s %s %.2f' % (category_name, target, stat_unc_name, unc_value)
                    )
                else:
                    raise ValueError('systematic uncertainty type:"%s" not recognised!' % info['type'])

            if info['type'] <> 'stat':
                shift += 1
                unc_vals_lines.append(
                    '%s %s %s %.2f' % (category_name, ','.join(targets), unc_name, shift)
                )

        return unc_conf_lines, unc_vals_lines
##-----


    
 
  
    def write_shapes_for_optimization(self, folder, variable, output_dir, br_strenght=1,
                                rebin=1, preprocess=None): #, systematics):
        '''Makes shapes for computing the limit and returns a list of systematic effects to be added to unc.vals/conf 
        make_shapes(folder, variable, output_dir, [rebin=1, preprocess=None) --> unc_conf_lines (list), unc_vals_lines (list)
        '''
        output_dir.cd()
        path = os.path.join(folder,variable)

        #make MC views with xsec error
        bkg_views  = dict(
            [(self.datacard_names[i], j) for i, j in zip(self.mc_samples, self.mc_views(rebin, preprocess))]
        )
        bkg_weights = dict(
            [(self.datacard_names[i], self.get_view(i, 'weight')) for i in self.mc_samples]
        )
        #cache histograms, since getting them is time consuming
        bkg_histos = {}
        for name, view in bkg_views.iteritems():
            mc_histo = view.Get(path)
            bkg_histos[name] = mc_histo.Clone()
            #mc_histo = remove_empty_bins(
            #    mc_histo, bkg_weights[name])
            mc_histo.SetName(name)
            mc_histo.Write()

        if self.use_embedded:            
            view = self.get_view('ZetauEmbedded')
            weight = self.get_view('ZetauEmbedded', 'weight')
            if preprocess:
                view = preprocess(view)
            view = self.rebin_view(view, rebin)
            name = self.datacard_names['ZetauEmbedded']
            bkg_weights[name] = weight
            bkg_views[name] = view
            mc_histo = view.Get(path)
            bkg_histos[name] = mc_histo.Clone()
            #mc_histo = remove_empty_bins(
            #    mc_histo, weight)
            mc_histo.SetName(name)
            mc_histo.Write()
          
 ##       fakes_view = self.get_view('fakes')#to comment for optimization study
        d_view = self.get_view('data')
        weights_view = views.SumView(
            views.SubdirectoryView(d_view, 'tLoose'),
            views.SubdirectoryView(d_view, 'eLoose'),
            views.SubdirectoryView(d_view, 'etLoose')
            )
        if preprocess:
            fakes_view = preprocess(fakes_view)
            weights_view = preprocess(weights_view)
##        weights = weights_view.Get(os.path.join(folder,'weight')) #to comment for optimization study
##        fakes_view = self.rebin_view(fakes_view, rebin)
##        bkg_views['fakes'] = fakes_view
##        bkg_weights['fakes'] = mean(weights)
##        fake_shape = bkg_views['fakes'].Get(path)
##        bkg_histos['fakes'] = fake_shape.Clone()
##        #fake_shape = remove_empty_bins(
##        #    fake_shape, bkg_weights['fakes'])
##        fake_shape.SetName('fakes')
##        fake_shape.Write()

        unc_conf_lines = []
        unc_vals_lines = []
        category_name  = output_dir.GetName()
        for unc_name, info in self.systematics.iteritems():
            targets = []
            for target in info['apply_to']:
                if target in self.sample_groups:
                    targets.extend(self.sample_groups[target])
                else:
                    targets.append(target)

            unc_conf = 'lnN' if info['type'] == 'yield' or info['type'] == 'stat' else 'shape'            
            #stat shapes are uncorrelated between samples
            if info['type'] <> 'stat':
                unc_conf_lines.append('%s %s' % (unc_name, unc_conf))
            shift = 0.
            path_up = info['+'](path)
            path_dw = info['-'](path)
            for target in targets:
                up      = bkg_views[target].Get(
                    path_up
                )
                down    = bkg_views[target].Get(
                    path_dw
                )
                if info['type'] == 'yield':
                    central = bkg_histos[target]
                    integral = central.Integral()
                    integral_up = up.Integral()
                    integral_down = down.Integral()
                    if integral == 0  and integral_up == 0 and integral_down ==0 :
                        shift=shift
                    else:
                        shift = max(
                            shift,
                            (integral_up - integral) / integral,
                            (integral - integral_down) / integral
                        )
                elif info['type'] == 'shape':
                    #remove empty bins also for shapes 
                    #(but not in general to not spoil the stat uncertainties)
                    #up = remove_empty_bins(up, bkg_weights[target])
                    #down = remove_empty_bins(down, bkg_weights[target])
                    up.SetName('%s_%sUp' % (target, unc_name))
                    down.SetName('%s_%sDown' % (target, unc_name))
                    up.Write()
                    down.Write()
                elif info['type'] == 'stat':
                    nbins = up.GetNbinsX()
                    up.Rebin(nbins)
                    yield_val = up.GetBinContent(1)
                    yield_err = up.GetBinError(1)
                    #print target, yield_val, yield_err, 
                    if yield_val==0:
                        unc_value = 0.
                    else:
                        unc_value = 1. + (yield_err / yield_val)
                    stat_unc_name = '%s_%s_%s' % (target, category_name, unc_name)
                    unc_conf_lines.append('%s %s' % (stat_unc_name, unc_conf))
                    unc_vals_lines.append(
                        '%s %s %s %.2f' % (category_name, target, stat_unc_name, unc_value)
                    )
                else:
                    raise ValueError('systematic uncertainty type:"%s" not recognised!' % info['type'])

            if info['type'] <> 'stat':
                shift += 1
                unc_vals_lines.append(
                    '%s %s %s %.2f' % (category_name, ','.join(targets), unc_name, shift)
                )

        #Get signal
        signals = [
            'ggHiggsToETau',
            'vbfHiggsToETau',
        ]
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = views.ScaleView(
                RebinView(sig_view, rebin),
                br_strenght
                )
            
            histogram = sig_view.Get(path)
            histogram.SetName(self.datacard_names[name])
            histogram.Write()

        # Draw data
        data_view = self.get_view('data')
        if preprocess:
            data_view = preprocess( data_view )
        data_view = self.rebin_view(data_view, rebin)
        data = data_view.Get(path)
        data.SetName('data_obs')
        data.Write()

        return unc_conf_lines, unc_vals_lines


    def plot_cut_optimizer(self,path,cut_thresholds,cut_type,variable,rebin,saveDir,xaxis='',xrange=None,sort=True,preprocess=None,njet=0):
        '''Plot background outline  different cuts on same canvas'''
        canv=ROOT.TCanvas("optim","optim",800,600)
        canv.cd()
        canv.SetTitle(cut_type)
        color=1
        marker=10
        path2=os.path.join(path+'/'+cut_thresholds[0],variable)
        hist_list=[]
        maxYVal=-2
        signals = [
            'GluGlu_LFV_HToMuTau_M125_13TeV_powheg_pythia8',
            'VBF_LFV_HToMuTau_M125_13TeV_powheg_pythia8'
            ]
#            
        sig = []
        for name in signals:
            sig_view = self.get_view(name)
            sig_view = RebinView(sig_view, rebin)
            sig_view = views.ScaleView(sig_view, 50)
            histogram = sig_view.Get(path2)
            histogram.Scale(1/histogram.Integral())
            if histogram.GetBinContent(histogram.GetMaximumBin())>maxYVal:
                maxYVal=histogram.GetBinContent(histogram.GetMaximumBin())*1.1
                histogram.GetYaxis().SetRangeUser(-0.1, maxYVal)
            histogram.Draw("same")
            histogram.SetTitle(cut_type)
            sig.append(histogram)


        for folder in cut_thresholds:
            mc_stack_view = self.make_stack(rebin, preprocess, path+'/'+folder, sort)

            mc_stack = mc_stack_view.Get(variable)
            mc_err = mc_stack.GetStack().Last().Clone();
            mc_err.GetXaxis().SetRangeUser(xrange[0], xrange[1])
 #           mc_err.GetYaxis().SetRangeUser(-1, 0.5)
            mc_err.SetLineColor(color) 
            mc_err.SetFillColor(0)
            mc_err.SetMarkerColor(color)
            mc_err.SetMarkerStyle(marker)
#            mc_err.SetMarkerSize(3)
            mc_err.Scale(1/mc_err.Integral())
            mc_err.GetXaxis().SetTitle(xaxis)
            mc_err.SetTitle(folder)
            color+=1
            marker+=3
            
            if mc_err.GetBinContent(mc_err.GetMaximumBin())>maxYVal:
                maxYVal=mc_err.GetBinContent(mc_err.GetMaximumBin())*1.1
                mc_err.GetYaxis().SetRangeUser(-0.1, maxYVal)
            hist_list.append(mc_err)
            mc_err.GetYaxis().SetRangeUser(-0.1, maxYVal)
            mc_err.Draw('hp hist same')

        mc_err.GetYaxis().SetRangeUser(-0.1, maxYVal)
#        print "maxi2",maxYVal


        #Draw Signal MC
#        for lfvh in sig:
#            if lfvh.GetMaximum() > mc_stack.GetMaximum():
#                mc_stack.SetMaximum(1.2*lfvh.
#        canv.Update()
        
#        self.add_legend([sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        
        leg=ROOT.TLegend(0.6,0.7,0.9,0.9)
        for histo in hist_list:
            leg.AddEntry(histo,str(histo.GetTitle()),"l")
        leg.AddEntry(sig[0],"MC_GG_Fusion","l")
        leg.AddEntry(sig[1],"MC_VB_Fusion","l")
        leg.Draw()
        canv.SetTitle(cut_type)
        canv.SaveAs(saveDir+"/"+str(njet)+'_'+str(hist_list[0].GetTitle())+'.pdf')
##        self.add_cms_blurb(13)

 
        

    def plot_mc_vs_data_witherrors(self, folder, variable, category,rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                        show_ratio=False, ratio_range=0.2, sort=False,drawData=True,br=1):
        ''' Compare Monte Carlo to data '''
        sel=False
        if 'selected' in folder or 'mass' in variable:
            sel=True
        if 'ss/' in folder:
            sel=False
        path = os.path.join(folder,variable)
        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)
        mc_stack = mc_stack_view.Get(variable)
        mc_stack.SetTitle("")
        mc_stack.Draw()
        mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_stack.Draw()
        mc_err = mc_stack.GetStack().Last().Clone();
        mc_err.Sumw2()
        mc_err.SetMarkerStyle(0)

        mc_err.SetLineColor(0)
        mc_err.SetFillStyle(1001)
        mc_err.SetFillColorAlpha(920+2,0.35)
        mc_err.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_err.Draw('pe2 same')
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
        mc_stack.GetHistogram().GetYaxis().SetTitle("Events /"+str(mc_stack.GetHistogram().GetBinWidth(5))+" GeV")
        mc_stack.GetHistogram().GetXaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetYaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetXaxis().SetTitleSize(0.045)
        mc_stack.GetHistogram().GetYaxis().SetTitleSize(0.05)
        mc_stack.GetHistogram().GetYaxis().SetTitleOffset(0.9)

#        if xrange:
 #           mc_stack.Draw()
  #          mc_err.Draw('pe2 same')
        self.keep.append(mc_stack)
        #Draw Signal MC
        signals = [
            'GluGlu_LFV_HToMuTau_M125_13TeV_powheg_pythia8',
            'VBF_LFV_HToMuTau_M125_13TeV_powheg_pythia8'
            ]
        sig = []
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = RebinView(sig_view, rebin)
#            if not plot_data:
            sig_view = views.ScaleView(sig_view, br)

            histogram = sig_view.Get(path)
            histogram.Draw('same')
            self.keep.append(histogram)
            sig.append(histogram)
        for lfvh in sig:
                if lfvh.GetMaximum() > mc_stack.GetMaximum():
                    mc_stack.SetMaximum(1.2*lfvh.GetMaximum())

        # Draw data
        if drawData: 
            data_view = self.get_view('data')
            if preprocess:
                data_view = preprocess( data_view )
            data_view = self.get_wild_dir(
                self.rebin_view(data_view, rebin),
                folder
                )
            data = data_view.Get(variable)
            data.Draw('same')
            self.keep.append(data)
            mc_stack.SetMinimum(0.00001)
            # Make sure we can see everything
            if data.GetMaximum() > mc_stack.GetMaximum():
                mc_stack.SetMaximum(1.2*data.GetMaximum())
        # Add legend
        if drawData:        
            self.add_legend([data, sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        else:
            self.add_legend([sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        self.add_cms_blurb(13)
        if show_ratio and drawData:
            self.add_ratio_plot(data, mc_stack, category,xrange, ratio_range=1.0)




 

    def plot_mc_vs_data_witherrors_2D(self, folder, variable, rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                        show_ratio=False, ratio_range=0.2, sort=False,drawData=True):
        ''' Compare Monte Carlo to data '''
        ROOT.gStyle.SetOptStat(1)
        path = os.path.join(folder,variable)
        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)
        mc_stack = mc_stack_view.Get(variable)
        mc_stack.SetTitle(variable)
        ROOT.gStyle.SetOptStat(1)
        mc_stack.Draw('colz')
        mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
  #      mc_stack.Draw('colz')
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
        ROOT.gStyle.SetOptStat(1)
 #       mc_err = mc_stack.GetStack().Last().Clone();
#        if xrange:
 #           mc_stack.Draw()
  #          mc_err.Draw('pe2 same')
  #      mc_err.Draw('colz')
        self.keep.append(mc_stack)
        #Draw Signal MC
        self.add_cms_blurb(13)
    def plot_mc_vs_data_new(self, folder, variable, category,rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                        show_ratio=False, ratio_range=0.2, sort=False,drawData=True,drawLegend=True,br=5):
        ''' Compare Monte Carlo to data '''
        selec=False
        oppsign=True

        if 'selected' in folder:
            selec=True
        if 'ss/gg' in folder:
            oppsign=False
        path = os.path.join(folder,variable)
        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)
        mc_stack = mc_stack_view.Get(variable)
        mc_stack.SetTitle("")
        mc_stack.Draw()
        mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_stack.Draw()
        mc_err = mc_stack.GetStack().Last().Clone();
        mc_err.Sumw2()
        mc_err.SetMarkerStyle(0)

        mc_err.SetLineColor(0)
        mc_err.SetFillStyle(1001)
        mc_err.SetFillColorAlpha(920+2,0.35)
        mc_err.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_err.Draw('pe2 same')
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
#        mc_stack.GetHistogram().GetYaxis().SetTitle("Events /"+str(mc_stack.GetHistogram().GetBinWidth(5))+" GeV")
        mc_stack.GetHistogram().GetYaxis().SetTitle("Events / bin")
        mc_stack.GetHistogram().GetXaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetYaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetXaxis().SetTitleSize(0.045)
        mc_stack.GetHistogram().GetYaxis().SetTitleSize(0.05)
        mc_stack.GetHistogram().GetYaxis().SetTitleOffset(0.9)

#        if xrange:
 #           mc_stack.Draw()
  #          mc_err.Draw('pe2 same')
        self.keep.append(mc_stack)
        #Draw Signal MC
        signals = [
            'LFVVBF125',
            'LFVGG125'
            ]
        sig = []
        totalsig=None
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = RebinView(sig_view, rebin)
#            if not plot_data:
            sig_view = views.ScaleView(sig_view, br)

            histogram = sig_view.Get(path)
            histogram.Draw('same')
            if not totalsig:
                totalsig=histogram.Clone()
            else:
                totalsig.Add(histogram)
            self.keep.append(histogram)
            sig.append(histogram)

        totalsig.Scale(1/float(br))

        for lfvh in sig:
                if lfvh.GetMaximum() > mc_stack.GetMaximum():
                    mc_stack.SetMaximum(1.2*lfvh.GetMaximum())
                    
        # Draw data
        if drawData: 
            data_view = self.get_view('data')
            if preprocess:
                data_view = preprocess( data_view )
            data_view = self.get_wild_dir(
                self.rebin_view(data_view, rebin),
                folder
                )
            data = data_view.Get(variable)
            data.Draw('same')
            self.keep.append(data)
            mc_stack.SetMinimum(0)
            # Make sure we can see everything
            if data.GetMaximum() > mc_stack.GetMaximum():
                mc_stack.SetMaximum(1.2*data.GetMaximum())

#        for bin in (1,totalsig.GetNbinsX()+1)
        mc_hist = mc_stack.GetStack().Last().Clone();

        for bin in range(1,totalsig.GetNbinsX()+1):
            background=mc_hist.GetBinContent(bin) #B
            signal=totalsig.GetBinContent(bin)
            if signal>0:
                if (float(signal)/float(signal+background)>0.9):
                    data.SetBinContent(bin,0)
                    data.SetBinError(bin,0)
            
        # Add legend
        if drawData:        
            self.add_legend([data, sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        elif drawLegend:
            self.add_legend([sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        self.add_cms_blurb(13,category)
        show_ratio=False
        if show_ratio and drawData:
            self.add_ratio_plot(data, mc_stack, variable,category,xrange, ratio_range=0.50,sel=selec,os=oppsign)

    def plot_mc_vs_data_noData(self, folder, variable, category,rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                        show_ratio=False, ratio_range=0.2, sort=False,drawData=True,drawLegend=True,br=1):
        ''' Compare Monte Carlo to data '''

        path = os.path.join(folder,variable)
        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)
        mc_stack = mc_stack_view.Get(variable)
        ROOT.gStyle.SetTitleX(0.5)
        ROOT.gStyle.SetTitleAlign(23)
        mc_stack.SetTitle("")
        mc_stack.Draw()
#        ROOT.gPad.Update()
#        title=ROOT.gPad.GetPrimitive("title")
#        title.SetBorderSize(0)
#        title.SetLineColor(ROOT.kWhite)
#        ROOT.gPad.Update()
        mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
#        mc_stack.GetHistogram().GetYaxis().SetTitle("Events /"+str(mc_stack.GetHistogram().GetBinWidth(5))+" GeV")
        mc_stack.GetHistogram().GetYaxis().SetTitle("Events / bin")
        mc_stack.GetHistogram().GetXaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetYaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetXaxis().SetTitleSize(0.045)
        mc_stack.GetHistogram().GetYaxis().SetTitleSize(0.05)
        mc_stack.GetHistogram().GetYaxis().SetTitleOffset(1.0) 
        mc_stack.Draw()
        mc_err = mc_stack.GetStack().Last().Clone();
        mc_err.Sumw2()
        mc_err.SetMarkerStyle(0)

        mc_err.SetLineColor(0)
        mc_err.SetFillStyle(1001)
        mc_err.SetFillColorAlpha(920+2,0.35)
        mc_err.GetXaxis().SetRangeUser(xrange[0], xrange[1])
#        mc_err.Draw('pe2 same')
 

#        if xrange:
 #           mc_stack.Draw()
  #          mc_err.Draw('pe2 same')
        self.keep.append(mc_stack)
        #Draw Signal MC
        signals = [
            'LFVVBF125',
            'LFVGG125'
            ]
        sig = []
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = RebinView(sig_view, rebin)
#            if not plot_data:
            sig_view = views.ScaleView(sig_view, br)

            histogram = sig_view.Get(path)
 #           histogram.Draw('same')
            self.keep.append(histogram)
            sig.append(histogram)
        for lfvh in sig:
                if lfvh.GetMaximum() > mc_stack.GetMaximum():
                    mc_stack.SetMaximum(1.2*lfvh.GetMaximum())
        # Add legend
        if drawData:        
            self.add_legend([data, sig[0],sig[1],mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        else:
            self.add_legend([mc_stack], leftside, entries=len(mc_stack.GetHists())+3)
        self.add_cms_blurb(13)
        if show_ratio and drawData:
            self.add_ratio_plot(data, mc_stack, variable,category,xrange, ratio_range=1.0)

    def plot_mc_vs_data_highmass(self, folder, variable, category,rebin=1, xaxis='',
                        leftside=True, xrange=None, preprocess=None,
                        show_ratio=False, ratio_range=0.2, sort=False,drawData=True,drawLegend=True,br=5):
        ''' Compare Monte Carlo to data '''
        selec=False
        oppsign=True

        if 'selected' in folder:
            selec=True
        if 'ss/gg' in folder:
            oppsign=False
        path = os.path.join(folder,variable)
        mc_stack_view = self.make_stack(rebin, preprocess, folder, sort)
        mc_stack = mc_stack_view.Get(variable)
        mc_stack.SetTitle("")
        mc_stack.Draw()
        mc_stack.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_stack.Draw()
        mc_err = mc_stack.GetStack().Last().Clone();
        mc_err.Sumw2()
        mc_err.SetMarkerStyle(0)

        mc_err.SetLineColor(0)
        mc_err.SetFillStyle(1001)
        mc_err.SetFillColorAlpha(920+2,0.35)
        mc_err.GetXaxis().SetRangeUser(xrange[0], xrange[1])
        mc_err.Draw('pe2 same')
        mc_stack.GetHistogram().GetXaxis().SetTitle(xaxis)
#        mc_stack.GetHistogram().GetYaxis().SetTitle("Events /"+str(mc_stack.GetHistogram().GetBinWidth(5))+" GeV")
        mc_stack.GetHistogram().GetYaxis().SetTitle("Events / bin")
        mc_stack.GetHistogram().GetXaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetYaxis().SetTitleFont(22)
        mc_stack.GetHistogram().GetXaxis().SetTitleSize(0.045)
        mc_stack.GetHistogram().GetYaxis().SetTitleSize(0.05)
        mc_stack.GetHistogram().GetYaxis().SetTitleOffset(0.9)

#        if xrange:
 #           mc_stack.Draw()
  #          mc_err.Draw('pe2 same')
        self.keep.append(mc_stack)
        #Draw Signal MC
        signals = [
            'LFV200',
            'LFV300',
            'LFV450',
            'LFV600',
            'LFV750',
            'LFV900',
            
]
        sig = []
        sig_histos=[]
        for name in signals:
            sig_view = self.get_view(name)
            if preprocess:
                sig_view = preprocess(sig_view)
            sig_view = RebinView(sig_view, rebin)
#            if not plot_data:
            sig_view = views.ScaleView(sig_view, br)

            histogram = sig_view.Get(path)
            histogram.Draw('same')
            curr_sig=copy.copy(histogram)
            sig_histos.append(curr_sig)
            self.keep.append(histogram)
            sig.append(histogram)

        for histo in sig_histos:
#            print histo
            histo.Scale(1/float(br))

#        for lfvh in sig:
 #               if lfvh.GetMaximum() > mc_stack.GetMaximum():
  #                  mc_stack.SetMaximum(500*lfvh.GetMaximum())
                    
        # Draw data
        if drawData: 
            data_view = self.get_view('data')
            if preprocess:
                data_view = preprocess( data_view )
            data_view = self.get_wild_dir(
                self.rebin_view(data_view, rebin),
                folder
                )
            data = data_view.Get(variable)
            data.Draw('same')
            self.keep.append(data)
            mc_stack.SetMinimum(0.00001)
            # Make sure we can see everything
            if data.GetMaximum() > mc_stack.GetMaximum():
                mc_stack.SetMaximum(500*data.GetMaximum())
            else:
                mc_stack.SetMaximum(500*mc_stack.GetMaximum())
#        for bin in (1,totalsig.GetNbinsX()+1)
        mc_hist = mc_stack.GetStack().Last().Clone();
        
        for histo in sig_histos:
            for bin in range(1,histo.GetNbinsX()+1):
                background=mc_hist.GetBinContent(bin) #B
                signal=histo.GetBinContent(bin)
                if signal>0:
                    if (float(signal)/float(signal+background)>0.0050):
                        data.SetBinContent(bin,0)
                        data.SetBinError(bin,0)
            
        # Add legend
        if drawData:        
            self.add_legend([data, sig[0],sig[1],sig[2],sig[3],sig[4],sig[5],mc_stack], leftside, entries=len(mc_stack.GetHists())+5)
        elif drawLegend:
            self.add_legend([sig[0],sig[1],sig[2],sig[3],sig[4],sig[5],mc_stack], leftside, entries=len(mc_stack.GetHists())+5)
        self.add_cms_blurb(13,category)
#        show_ratio=False
        if show_ratio and drawData:
            self.add_ratio_plot(data, mc_stack, variable,category,xrange, ratio_range=0.50,sel=selec,os=oppsign)

