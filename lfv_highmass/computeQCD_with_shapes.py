import array
import os 
from sys import argv, stdout, stderr
import ROOT
import sys
import math
import copy
import argparse
ROOT.gROOT.SetStyle("Plain")
ROOT.gErrorIgnoreLevel=ROOT.kError

parser = argparse.ArgumentParser(
    "Compute QCD from same sign shape and using a OS/SS SF ")

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
    "--inputFile",
    action="store",
    dest="inputFile",
    help="Provide the relative path to the target input file")
parser.add_argument(
    "--numCategories",
    type=int,
    action="store",
    dest="numCategories",
    default=3,
    help="category nameis in analyzer")
args = parser.parse_args()




categories=[str(cat) for cat in range(args.numCategories)]   #category names in analyzer                                                                                    



syst_names_analyzer=['mesup','mesdown','eesup','eesdown','eresrhoup','eresrhodown','nosys','eresphidown','puup','pudown',
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


variables = [
#	('BDT_value', 'BDT_value', 1),
	('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', 1),

	]



commonvars=[
   ('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', 5),
   ]



regions=['ss']
regions_common=['ss']

Analyzer="Analyzer_MuE_"+args.analyzer_name


class GetQCD(object):
	def __init__(self):
		self.histos={}
                self.histomc=None
	        self.histodata=None
	        self.histoQCD=None
		self.datafile=file=ROOT.TFile(Analyzer+str(args.Lumi)+"/data_obs.root")
		print self.datafile
	        for var in variables:
	        	for sign in regions:#,'antiIsolatedweightedmuonelectron/ss','antiIsolatedweightedelectron/ss','antiIsolatedweightedmuon/ss']:
	        		for j in ['fullsel']:
	        			for i in range(len(categories)):
						self.histodata=self.datafile.Get(sign+"/"+str(i )+"/selected/nosys/"+var[0])
						for k in range(len(syst_names_analyzer)):

							hist_path= sign+"/"+str(i)+"/selected/"+syst_names_analyzer[k]+"/"+var[0]
												
							self.histomc=None
							self.histoQCD=None
							for filename in os.listdir(Analyzer+str(args.Lumi)):
								if "data" in filename or "QCD" in filename or "LFV" in filename: continue
								file=ROOT.TFile(Analyzer+str(args.Lumi)+"/"+filename)
								histo=file.Get(hist_path)
								if not histo:
									continue
								try:
									self.histomc.Add(histo)
								except AttributeError:
									self.histomc=histo.Clone()
									self.histomc.SetDirectory(0)
									
								
							
							if not self.histomc:
								print "Couldn't find variable ",var[0]," syst: ",syst_names_analyzer[k]
								continue

							self.histomc.Scale(args.Lumi)				
#						print "data",self.histodata.Integral()
#						print "MC",self.histomc.Integral()
							self.histoQCD=self.histodata.Clone()
							self.histoQCD.Add(self.histomc,-1)
							if i==2 or i==3:
								self.histoQCD.Scale(2.86)
							else:
								self.histoQCD.Scale(2.26)

							new_histo=copy.copy(self.histoQCD) #MAKE DEEP COPY 
						
						#replace ss in pathname by os
							path_name_original=hist_path.split('/')
							path_name_original_redacted='/'.join(path_name_original[0:(len(path_name_original)-1)])
							new_path_name=path_name_original_redacted.replace('ss','os',1)
							self.histos[(new_path_name,var[0])]=new_histo


		self.outputfile=ROOT.TFile("QCD"+args.analyzer_name+"_with_shapes.root","recreate")
		self.outputfile.cd()
		for key in self.histos.keys():
			print key

#			self.outputfile.cd()
			self.dir0 = self.outputfile.mkdir(key[0])
#			print self.dir0
			self.dir0.Cd("QCD"+args.analyzer_name+"_with_shapes.root:/"+key[0])
#    print dir0
#			print histos[key]
			self.histos[key].SetDirectory(self.dir0)
			self.histos[key].Write()
		self.outputfile.Close()




QCD=GetQCD()
