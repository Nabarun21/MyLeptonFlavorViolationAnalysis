import array
import os
from sys import argv, stdout, stderr
import ROOT
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


lumidict['QCD']=args.Lumi


lumidict2['data_obs']=args.Lumi
lumidict2['Diboson']=1.49334492783e-05
lumidict2['TT']=1.08709111195e-05
lumidict2['WJETSMC']=3e-04
lumidict2['DY']=2.1e-05
lumidict2['Zothers']=2.1e-05
lumidict2['ZTauTau']=2.1e-05
lumidict2['ggH_htt']=2.07e-06
lumidict2['qqH_htt']=4.2e-08
lumidict2['ggH_hww']=2.07e-06
lumidict2['qqH_hww']=4.2e-08
lumidict2['LFV200']=1.694e-06
lumidict2['LFV300']=7.32222222221e-07
lumidict2['LFV450']=2.70588235294e-07
lumidict2['LFV600']=1.2625e-07
lumidict2['LFV750']=9.93800000005e-08 
lumidict2['LFV900']=4.13076923077e-08 
lumidict2['WG']=1.56725042226e-06
lumidict2['W']=1.56725042226e-06
lumidict2['T']=5.23465826064e-06
lumidict2['QCD']=float(1.0)/float(args.Lumi)




commonvars=[
   ('BDT_value', 'BDT_value', 1),
   ('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', 5),
   ('mPt', 'p_{T}(mu) (GeV)', 5),
   ('mEta', 'eta(mu)', 1),
   ('mPhi', 'phi(mu)', 2),
   ('ePt', 'p_{T}(e) (GeV)', 5),
   ('eEta', 'eta(e)', 1),
   ('ePhi', 'phi(e)', 2),
   ('em_DeltaPhi', 'emu Deltaphi', 1),
   ('em_DeltaR', 'emu Delta R', 1),
   ('h_vismass', 'M_{vis} (GeV)', 5),
   ('Met', 'MET (GeV)', 1),
   ('ePFMET_Mt', 'MT-e-MET (GeV)', 5),
   ('mPFMET_Mt', 'MT-mu-MET (GeV)', 5),
   ('ePFMET_DeltaPhi', 'Deltaphi-e-MET (GeV)', 1),
   ('mPFMET_DeltaPhi', 'Deltaphi-mu-MET (GeV)', 1),
   ]

categories=["mutaue_0jet_presel","mutaue_1jet_presel","mutaue_2jet_presel"]

try:
   os.makedirs(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/preselection")
except Exception as ex:
   print ex


for var in commonvars:
   histos={}
   for i_cat in range(len(categories)):
      histos[categories[i_cat]]=[]
      for filename in os.listdir('AnalyzerMuE'+args.analyzer_name+str(args.Lumi)):
         if "FAKES" in filename or "ETau" in filename :continue
         file=ROOT.TFile('AnalyzerMuE'+args.analyzer_name+str(args.Lumi)+'/'+filename)
         new_title=filename.split('.')[0]
         hist_path="os/"+str(i_cat)+"/"+var[0]
         histo=file.Get(hist_path)
        # print histo.GetNbinsX()
         rebin=var[2]

         if not histo:
            continue

         histo.Rebin(rebin*2)

         if 'data' not in filename and 'QCD' not in filename:
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
         histos[categories[i_cat]].append(new_histo)


   if not histo:
      print "couldn't find histo for ",var[0]
      continue

   
   outputfile=ROOT.TFile(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/preselection/"+var[0]+".root","recreate")

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



