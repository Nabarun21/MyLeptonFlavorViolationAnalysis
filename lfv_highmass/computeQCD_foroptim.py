import array
import os 
from sys import argv, stdout, stderr
import ROOT
import sys
import math
import copy
import argparse
import optimizer as optimizer
ROOT.gROOT.SetStyle("Plain")
ROOT.gErrorIgnoreLevel=ROOT.kError

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
    "--inputFile",
    action="store",
    dest="inputFile",
    help="Provide the relative path to the target input file")
parser.add_argument(
    "--numCategories",
    type=int,
    action="store",
    dest="numCategories",
    default=2,
    help="category nameis in analyzer")
args = parser.parse_args()


cuts={}
cuts[0]=optimizer.compute_regions_0jet(100000,100000,100000,-1000000,100000,10000,-10000)
cuts[1]=optimizer.compute_regions_0jet(100000,100000,100000,-1000000,100000,10000,-10000)


categories=[str(cat) for cat in range(args.numCategories)]   #category names in analyzer                                                                                    


syst_names=[]      #sysfolder names in analyzer                                             
if args.doSyst:                                                                                                                                              
	syst_names=['jetup','jetdown','uup','udown','mesup','mesdown','eesup','eesdown']      #sysfolder names in analyzer                                             

variables = [
	('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', 1),
	]




regions=['ss']
regions_common=['ss']

Analyzer="Optimizer_MuE_"+args.analyzer_name


class GetQCD(object):
	def __init__(self):
		self.histos={}
                self.histomc=None
	        self.histodata=None
	        self.histoQCD=None
	        for var in variables:
	        	for sign in regions:#,'antiIsolatedweightedmuonelectron/ss','antiIsolatedweightedelectron/ss','antiIsolatedweightedmuon/ss']:
				for i in range(len(categories)):
					for cut in cuts[i]:
	        				x=0
	        				y=0
						hist_path= sign+"/"+str(i)+"/selected/nosys/"+cut+"/"+var[0]
						
						self.histomc=None
						self.histodata=None
						self.histoQCD=None
	        				for filename in os.listdir(Analyzer+str(args.Lumi)):
							if "FAKES" in filename or "QCD" in filename: continue
	        					file=ROOT.TFile(Analyzer+str(args.Lumi)+"/"+filename)
							histo=file.Get(hist_path)
							if not histo:
								continue
#							print hist_path,"   ",filename,"   ",var[0],"  ",histo.Integral()
	        					if "data"  not in filename and "FAKES" not in filename and "LFV" not in filename and "QCD" not in filename:
								if x==0:
	        							self.histomc=histo.Clone()
									self.histomc.SetDirectory(0)
	        							x+=1
								else:
	        							self.histomc.Add(histo)
								
	        					elif "data" in filename:      		
	        						if y==0:
	        							y+=1
	        							self.histodata=histo.Clone()
									self.histodata.SetDirectory(0)
	        						else:
	        							self.histodata.Add(histo)
						if not self.histomc:
							print "Couldn't find variable ",var[0]
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


		self.outputfile=ROOT.TFile("QCD"+args.analyzer_name+"_foroptim.root","recreate")
		self.outputfile.cd()
		for key in self.histos.keys():
			print key

#			self.outputfile.cd()
			self.dir0 = self.outputfile.mkdir(key[0])
#			print self.dir0
			self.dir0.Cd("QCD"+args.analyzer_name+"_foroptim.root:/"+key[0])
#    print dir0
#			print histos[key]
			self.histos[key].SetDirectory(self.dir0)
			self.histos[key].Write()
		self.outputfile.Close()




QCD=GetQCD()
