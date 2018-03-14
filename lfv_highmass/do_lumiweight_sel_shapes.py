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
parser.add_argument(
    "--numCategories",
    type=int,
    action="store",
    dest="numCategories",
    default=3,
    help="category nameis in analyzer")
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

syst_names_analyzer=['nosys','mesup','mesdown','eesup','eesdown','eresrhoup','eresrhodown','nosys','eresphidown','puup','pudown',
                'chargeduesdown','chargeduesup','ecaluesdown','ecaluesup','hcaluesdown','hcaluesup','hfuesdown','hfuesup',
                'jes_JetAbsoluteFlavMapDown',
                'jes_JetAbsoluteMPFBiasDown',
                'jes_JetAbsoluteScaleDown',
                'jes_JetAbsoluteStatDown',
                'jes_JetFlavorQCDDown',
                'jes_JetFragmentationDown',
                'jes_JetPileUpDataMCDown',
                'jes_JetPileUpPtBBDown',
                'jes_JetPileUpPtEC1Down',
                'jes_JetPileUpPtEC2Down',
                'jes_JetPileUpPtHFDown',
                'jes_JetPileUpPtRefDown',
                'jes_JetRelativeBalDown',
                'jes_JetRelativeFSRDown',
                'jes_JetRelativeJEREC1Down',
                'jes_JetRelativeJEREC2Down',
                'jes_JetRelativeJERHFDown',
                'jes_JetRelativePtBBDown',
                'jes_JetRelativePtEC1Down',
                'jes_JetRelativePtEC2Down',
                'jes_JetRelativePtHFDown',
                'jes_JetRelativeStatECDown',
                'jes_JetRelativeStatFSRDown',
                'jes_JetRelativeStatHFDown',
                'jes_JetSinglePionECALDown',
                'jes_JetSinglePionHCALDown',
                'jes_JetTimePtEtaDown',
                'jes_JetAbsoluteFlavMapUp',
                'jes_JetAbsoluteMPFBiasUp',
                'jes_JetAbsoluteScaleUp',
                'jes_JetAbsoluteStatUp',
                'jes_JetFlavorQCDUp',
                'jes_JetFragmentationUp',
                'jes_JetPileUpDataMCUp',
                'jes_JetPileUpPtBBUp',
                'jes_JetPileUpPtEC1Up',
                'jes_JetPileUpPtEC2Up',
                'jes_JetPileUpPtHFUp',
                'jes_JetPileUpPtRefUp',
                'jes_JetRelativeBalUp',
                'jes_JetRelativeFSRUp',
                'jes_JetRelativeJEREC1Up',
                'jes_JetRelativeJEREC2Up',
                'jes_JetRelativeJERHFUp',
                'jes_JetRelativePtBBUp',
                'jes_JetRelativePtEC1Up',
                'jes_JetRelativePtEC2Up',
                'jes_JetRelativePtHFUp',
                'jes_JetRelativeStatECUp',
                'jes_JetRelativeStatFSRUp',
                'jes_JetRelativeStatHFUp',
                'jes_JetSinglePionECALUp',
                'jes_JetSinglePionHCALUp',
                'jes_JetTimePtEtaUp']      #sysfolder names in analyzer



syst_names_datacard=['nominal_no_name','CMS_MES_13TeVUp','CMS_MES_13TeVDown','CMS_EES_13TeVUp','CMS_EES_13TeVDown','CMS_Eresrho_13TeVUp','CMS_Eresrho_13TeVDown','CMS_Eresphi_13TeVUp','CMS_Eresphi_13TeVDown','CMS_Pileup_13TeVUp','CMS_Pileup_13TeVDown','CMS_MET_chargedUes_13TeVDown','CMS_MET_chargedUes_13TeVUp','CMS_MET_ecalUes_13TeVDown','CMS_MET_ecalUes_13TeVUp','CMS_MET_hcalUes_13TeVDown','CMS_MET_hcalUes_13TeVUp','CMS_MET_hfUes_13TeVDown','CMS_MET_hfUes_13TeVUp',
             'CMS_Jes_JetAbsoluteFlavMap_13TeVDown',
             'CMS_Jes_JetAbsoluteMPFBias_13TeVDown',
             'CMS_Jes_JetAbsoluteScale_13TeVDown',
             'CMS_Jes_JetAbsoluteStat_13TeVDown',
             'CMS_Jes_JetFlavorQCD_13TeVDown',
             'CMS_Jes_JetFragmentation_13TeVDown',
             'CMS_Jes_JetPileUpDataMC_13TeVDown',
             'CMS_Jes_JetPileUpPtBB_13TeVDown',
             'CMS_Jes_JetPileUpPtEC1_13TeVDown',
             'CMS_Jes_JetPileUpPtEC2_13TeVDown',
             'CMS_Jes_JetPileUpPtHF_13TeVDown',
             'CMS_Jes_JetPileUpPtRef_13TeVDown',
             'CMS_Jes_JetRelativeBal_13TeVDown',
             'CMS_Jes_JetRelativeFSR_13TeVDown',
             'CMS_Jes_JetRelativeJEREC1_13TeVDown',
             'CMS_Jes_JetRelativeJEREC2_13TeVDown',
             'CMS_Jes_JetRelativeJERHF_13TeVDown',
             'CMS_Jes_JetRelativePtBB_13TeVDown',
             'CMS_Jes_JetRelativePtEC1_13TeVDown',
             'CMS_Jes_JetRelativePtEC2_13TeVDown',
             'CMS_Jes_JetRelativePtHF_13TeVDown',
             'CMS_Jes_JetRelativeStatEC_13TeVDown',
             'CMS_Jes_JetRelativeStatFSR_13TeVDown',
             'CMS_Jes_JetRelativeStatHF_13TeVDown',
             'CMS_Jes_JetSinglePionECAL_13TeVDown',
             'CMS_Jes_JetSinglePionHCAL_13TeVDown',
             'CMS_Jes_JetTimePtEta_13TeVDown',
             'CMS_Jes_JetAbsoluteFlavMap_13TeVUp',
             'CMS_Jes_JetAbsoluteMPFBias_13TeVUp',
             'CMS_Jes_JetAbsoluteScale_13TeVUp',
             'CMS_Jes_JetAbsoluteStat_13TeVUp',
             'CMS_Jes_JetFlavorQCD_13TeVUp',
             'CMS_Jes_JetFragmentation_13TeVUp',
             'CMS_Jes_JetPileUpDataMC_13TeVUp',
             'CMS_Jes_JetPileUpPtBB_13TeVUp',
             'CMS_Jes_JetPileUpPtEC1_13TeVUp',
             'CMS_Jes_JetPileUpPtEC2_13TeVUp',
             'CMS_Jes_JetPileUpPtHF_13TeVUp',
             'CMS_Jes_JetPileUpPtRef_13TeVUp',
             'CMS_Jes_JetRelativeBal_13TeVUp',
             'CMS_Jes_JetRelativeFSR_13TeVUp',
             'CMS_Jes_JetRelativeJEREC1_13TeVUp',
             'CMS_Jes_JetRelativeJEREC2_13TeVUp',
             'CMS_Jes_JetRelativeJERHF_13TeVUp',
             'CMS_Jes_JetRelativePtBB_13TeVUp',
             'CMS_Jes_JetRelativePtEC1_13TeVUp',
             'CMS_Jes_JetRelativePtEC2_13TeVUp',
             'CMS_Jes_JetRelativePtHF_13TeVUp',
             'CMS_Jes_JetRelativeStatEC_13TeVUp',
             'CMS_Jes_JetRelativeStatFSR_13TeVUp',
             'CMS_Jes_JetRelativeStatHF_13TeVUp',
             'CMS_Jes_JetSinglePionECAL_13TeVUp',
             'CMS_Jes_JetSinglePionHCAL_13TeVUp',
             'CMS_Jes_JetTimePtEta_13TeVUp']      #sysfolder names in analyzer

print len(syst_names_datacard)
print len(syst_names_analyzer)

col_vis_mass_binning=array.array('d',(range(0,190,20)+range(200,480,30)+range(500,990,50)+range(1000,1520,100)))
#met_vars_binning=array.array('d',(range(0,190,20)+range(200,580,40)+range(600,1010,100)))
#pt_vars_binning=array.array('d',(range(0,190,20)+range(200,500,40)))



variable_list=[
#   ('BDT_value', 'BDT_value', 1),
   ('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', col_vis_mass_binning),
#   ('h_vismass', 'M_{vis} (GeV)', col_vis_mass_binning),
   ]


if args.numCategories==3:
   category_names=["mutaue_0jet_selected","mutaue_1jet_selected","mutaue_2jet_selected"]
elif args.numCategories==2:
   category_names=["mutaue_01jet_selected","mutaue_rest_selected"]
else:
   print "number of categories must be 1 or 2"
   exit


try:
   os.makedirs(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/selected_with_shapes")
except Exception as ex:
   print ex


for var in variable_list:
   histos={}
   for i_cat in range(len(category_names)):
      histos[category_names[i_cat]]=[]
      for filename in os.listdir('Analyzer_MuE_'+args.analyzer_name+str(args.Lumi)):
         if "FAKES" in filename or "ETau" in filename or filename=='QCD.root':continue
         file=ROOT.TFile('Analyzer_MuE_'+args.analyzer_name+str(args.Lumi)+'/'+filename)
         title=filename.split('.')[0].replace("_with_shapes","")
         for k in range(len(syst_names_analyzer)):
            hist_path="os/"+str(i_cat)+"/selected/"+syst_names_analyzer[k]+"/"+var[0]
            histo=file.Get(hist_path)

      # print histo.GetNbinsX()

            binning=var[2]

            if not histo:
               print "Couldn't find histo: ",title+" "+syst_names_analyzer[k]
               continue


            try:
               histo.Rebin(binning*2)
            except TypeError:
               histo=histo.Rebin(len(binning)-1,"",binning)
            except:
               print "Please fix your binning"


            if 'data' not in filename and 'QCD' not in filename and 'TT_DD' not in filename and "_with_shapes" not in filename:
               histo.Scale(lumidict['data_obs']/lumidict[title])      
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
                   histo.SetBinContent(j,0.001*float((lumidict['data_obs'])*float(lumidict2[title])))
                   histo.SetBinError(j,1.8*float((lumidict['data_obs'])*float(lumidict2[title])))
             #            print "found neg bin  ",j
            if 'nominal' not in syst_names_datacard[k]:
               new_title=title+"_"+syst_names_datacard[k]
            else:
               new_title=title
            histo.SetTitle(new_title)
            histo.SetName(new_title)
            new_histo=copy.copy(histo)
            histos[category_names[i_cat]].append(new_histo)


      if not histo:
         print "couldn't find histo for ",var[0]
         continue

   
   outputfile=ROOT.TFile(args.outputdir+"/"+args.analyzer_name+str(args.Lumi)+"/selected_with_shapes/"+var[0]+".root","recreate")

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



