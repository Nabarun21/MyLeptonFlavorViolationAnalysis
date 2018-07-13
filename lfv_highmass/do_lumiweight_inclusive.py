import binning
import os
from sys import argv, stdout, stderr
import ROOT
import binning
import sys
import copy
import argparse
ROOT.gROOT.SetStyle("Plain")
#ROOT.gROOT.SetBatch(True)
#ROOT.gStyle.SetOptStat(0)

parser = argparse.ArgumentParser(
    "Compute QCD from same sign shape and using a OS/SS SF ")
parser.add_argument(
    "--doSyst",
    action="store_true",
    help="if set , will calculate QCD histograms for all shape systematics")
parser.add_argument(
    "--aType",
    type=str,
    action="store",
    dest="analyzer_type",
    default="cut_based",
    help="type of analyzer: cut_based, BDT, neural_net")
parser.add_argument(
    "--region",
    type=str,
    action="store",
    dest="region",
    default="os",
    help="region of space: oppositesign-os,samesign-ss,anti-isolated os/ss etc")
parser.add_argument(
    "--aName",
    type=str,
    action="store",
    dest="analyzer_name",
    default="highmass",
    help="Which channel to run over? (et, mt, em, me)")
parser.add_argument(
    "--lumi",
    action="store",
    type=int,
    dest="Lumi",
    default=35862, #full 2016 dataset luminosity 
    help="luminosity in picobarns")
parser.add_argument(
    "--jobid",
    type=str,
    action="store",
    dest="jobid",
    default="LFV_Mar15_mc", #last production of 2016 ntuples
    help="Current condor jobid")
parser.add_argument(
    "--oDir",
    action="store",
    dest="outputdir",
    default="preprocessed_inputs",
    help="Provide the relative path to the target input file")

args = parser.parse_args()

 
lumidict2={}
lumidict={}

lumidict['data_obs']=args.Lumi

lumidict['Diboson']=1.0
lumidict['WG']=1.0
lumidict['W']=1.0
lumidict['T']=1.0
lumidict['TT']=1.0
lumidict['TT_DD']=1.0
lumidict['WJETSMC']=1.0
lumidict['DY']=1.0
lumidict['Zothers']=1.0
lumidict['ZTauTau']=1.0
lumidict['ggH_htt']=1.0
lumidict['qqH_htt']=1.0
lumidict['ggH_hww']=1.0
lumidict['qqH_hww']=1.0
lumidict['LFV200']=1.0
lumidict['LFV300']=1.0
lumidict['LFV450']=1.0
lumidict['LFV600']=1.0
lumidict['LFV750']=1.0
lumidict['LFV900']=1.0
lumidict['QCD_mc']=1.0


lumidict['QCD']=args.Lumi


lumidict2['data_obs']=args.Lumi
lumidict2['Diboson']=1.49334492783e-05
lumidict2['TT']=1.08709111195e-05
lumidict2['TT_DD']=1.08709111195e-05
lumidict2['WJETSMC']=3e-04
lumidict2['DY']=2.1e-05
lumidict2['Zothers']=2.1e-05
lumidict2['ZTauTau']=2.1e-05
lumidict2['ggH_htt']=2.07e-06
lumidict2['qqH_htt']=4.2e-08
lumidict2['ggH_hww']=2.07e-06
lumidict2['qqH_hww']=4.2e-08
lumidict2['LFV200']=1.694e-06
lumidict2['LFV300']=1.33345743863e-07 
lumidict2['LFV450']=4.65541809702e-08
lumidict2['LFV600']=2.04664734848e-08 
lumidict2['LFV750']=9.93800000005e-09
lumidict2['LFV900']=5.37000000001e-09 
lumidict2['WG']=1.56725042226e-06
lumidict2['W']=1.56725042226e-06
lumidict2['T']=5.23465826064e-06
lumidict2['QCD']=float(1.0)/float(args.Lumi)
lumidict2['QCD_mc']=0.013699241892



#col_vis_mass_binning=array.array('d',(range(0,190,20)+range(200,480,30)+range(500,990,50)+range(1000,1520,100)))
col_vis_mass_binning=binning.binning('colmass')
met_vars_binning=binning.binning('met')
pt_vars_binning=binning.binning('pt')

#col_vis_mass_binning=2
#met_vars_binning=2
#pt_vars_binning=2

variable_list=[
   ('BDT_value', 'BDT_value', 1),
   ('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', col_vis_mass_binning),
   ('mPt', 'p_{T}(mu) (GeV)', pt_vars_binning),
   ('mEta', 'eta(mu)', 1),
   ('mPhi', 'phi(mu)', 2),
   ('ePt', 'p_{T}(e) (GeV)', pt_vars_binning),
   ('eEta', 'eta(e)', 1),
   ('ePhi', 'phi(e)', 2),
   ('em_DeltaPhi', 'emu Deltaphi', 1),
   ('em_DeltaR', 'emu Delta R', 1),
   ('h_vismass', 'M_{vis} (GeV)', col_vis_mass_binning),
   ('Met', 'MET (GeV)', pt_vars_binning),
   ('ePFMET_Mt', 'MT-e-MET (GeV)', met_vars_binning),
   ('mPFMET_Mt', 'MT-mu-MET (GeV)', met_vars_binning),
   ('ePFMET_DeltaPhi', 'Deltaphi-e-MET (GeV)', 1),
   ('mPFMET_DeltaPhi', 'Deltaphi-mu-MET (GeV)', 1),
   ]

category="mutaue_inclus"

if not os.path.exists(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/inclusive"):
   os.makedirs(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/inclusive")
if not os.path.exists(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/inclusive/"+args.region):
   os.makedirs(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/inclusive/"+args.region)

for var in variable_list:
   histos={}
   histos[category]=[]
   for filename in os.listdir('Analyzer_MuE_'+args.analyzer_name+str(args.Lumi)):
      if "FAKES" in filename or "ETau" in filename or "QCD_with_shapes" in filename:continue
      if args.region=='ss' and 'QCD' in filename:continue
      file=ROOT.TFile('Analyzer_MuE_'+args.analyzer_name+str(args.Lumi)+'/'+filename)
      new_title=filename.split('.')[0]
      hist_path=args.region+"/"+var[0]
      histo=file.Get(hist_path)
        # print histo.GetNbinsX()
      binning=var[2]

      if not histo:
         continue

      if new_title!='QCD':
         try:
            histo.Rebin(binning*2)
         except TypeError:
            histo=histo.Rebin(len(binning)-1,"",binning)
         except:
            print "Please fix your binning"

      if new_title=='TT':histo.Scale(0.885591123589)
         
      if 'data' not in filename and 'QCD'!=filename and 'TT_DD' not in filename:
         histo.Scale(lumidict['data_obs']/lumidict[new_title])      
      if 'data' in filename:
         histo.SetBinErrorOption(ROOT.TH1.kPoisson)

      lowBound=0
      highBound=histo.GetNbinsX()
      for bin in range(1,highBound):
         if histo.GetBinContent(bin) != 0:
#            print histo.GetBinContent(bin),bin
            lowBound = bin
            break
      for bin in range(histo.GetNbinsX(),lowBound,-1):
         if histo.GetBinContent(bin) != 0:
            highBound = bin
            break
      for j in range(lowBound, highBound+1):
         if lowBound==0:continue
         if (histo.GetBinContent(j)<=0) and "data" not in filename and "LFV" not in filename:
            histo.SetBinContent(j,0.001*float((lumidict['data_obs'])*float(lumidict2[new_title])))
            histo.SetBinError(j,1.8*float((lumidict['data_obs'])*float(lumidict2[new_title])))
#            print "found neg bin  ",j

      histo.SetTitle(new_title)
      histo.SetName(new_title)
      new_histo=copy.copy(histo)
      histos[category].append(new_histo)

   if not histo:
      continue

   outputfile=ROOT.TFile(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/inclusive/"+args.region+"/"+var[0]+".root","recreate")

#   print outputfile
   outputfile.cd()
   for key in histos.keys():
      dir0 = outputfile.mkdir(key);
  # print dir
      dir0.cd();
         #   print key
      for histo in histos[key]:
 #     if "_" not in histo.GetName():
  #       print histo.GetName()
   #      print histo.GetBinContent(15)
    #     print histo.GetBinError(15)
         histo.Write()
   outputfile.Close()



