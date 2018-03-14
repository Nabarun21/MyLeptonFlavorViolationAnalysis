# check in https://twiki.cern.ch/twiki/bin/view/CMS/HiggsToTauTauWorking2015#MET when the mva met receipe is available.
from EMTree import EMTree
import os
import ROOT
import math
import glob
import array
#import mcCorrections
import baseSelections_mu50 as selections
import FinalStateAnalysis.PlotTools.pytree as pytree
from FinalStateAnalysis.PlotTools.decorators import  memo_last
from FinalStateAnalysis.PlotTools.MegaBase import MegaBase
from cutflowtracker import cut_flow_tracker
from math import sqrt, pi, cos
#from fakerate_functions import fakerate_central_histogram, fakerate_p1s_histogram, fakerate_m1s_histogram
import FinalStateAnalysis.TagAndProbe.PileupWeight as PileupWeight
import FinalStateAnalysis.TagAndProbe.MuonPOGCorrections as MuonPOGCorrections
import FinalStateAnalysis.TagAndProbe.MuonPOGCorrections_efficiencies as MuonPOGCorrections_efficiencies
import FinalStateAnalysis.TagAndProbe.EGammaPOGCorrections as EGammaPOGCorrections
import FinalStateAnalysis.TagAndProbe.HetauCorrection as HetauCorrection
#import FinalStateAnalysis.TagAndProbe.FakeRate2D as FakeRate2D
import bTagSF as bTagSF
from inspect import currentframe




cut_flow_step=['allEvents','HLTIsoPasstrg','DR_e_mu','surplus_mu_veto','surplus_e_veto','surplus_tau_veto','musel','mulooseiso','esel','elooseiso','ecalgap','bjetveto','muiso','eiso','jet0sel','jet1sel','jet2loosesel','jet2tightsel']


def deltaPhi(phi1, phi2):
    PHI = abs(phi1-phi2)
    if PHI<=pi:
        return PHI
    else:
        return 2*pi-PHI


def transMass(myparticle1,myparticle2):
    dphi12=deltaPhi(myparticle2.Phi(),myparticle1.Phi())
    return sqrt(2*myparticle1.Pt()*myparticle2.Pt()*(1-cos(dphi12)))

def collmass(row, met, metPhi,my_elec,my_muon):
    ptnu =abs(met*cos(deltaPhi(metPhi,my_elec.Phi())))
    visfrac = my_elec.Pt()/(my_elec.Pt()+ptnu)
    #print met, cos(deltaPhi(metPhi, row.tPhi)), ptnu, visfrac
    return ((my_elec+my_muon).M()) / (sqrt(visfrac))


def deltaR(phi1, phi2, eta1, eta2):
    deta = eta1 - eta2
    dphi = abs(phi1-phi2)
    if (dphi>pi) : dphi = 2*pi-dphi
    return sqrt(deta*deta + dphi*dphi);

def topPtreweight(pt1,pt2):
    #pt1=pt of top quark
    #pt2=pt of antitop quark
    #13 Tev parameters: a=0.0615,b=-0.0005
    #for toPt >400, apply SF at 400

    if pt1>400:pt1=400
    if pt2>400:pt2=400
    a=0.0615
    b=-0.0005 

    wt1=math.exp(a+b*pt1)
    wt2=math.exp(a+b*pt2)

    wt=sqrt(wt1*wt2)

    return wt

pu_distributions = glob.glob(os.path.join('inputs', os.environ['jobid'], 'data_SingleMu*pu.root'))
pu_distributions_down = glob.glob(os.path.join('inputs', os.environ['jobid'], 'data_SingleMu*pu_down.root'))
pu_distributions_up = glob.glob(os.path.join('inputs', os.environ['jobid'], 'data_SingleMu*pu_up.root'))

pu_corrector = PileupWeight.PileupWeight('MC_Moriond17', *pu_distributions)
pu_corrector_up = PileupWeight.PileupWeight('MC_Moriond17', *pu_distributions_up)
pu_corrector_down = PileupWeight.PileupWeight('MC_Moriond17', *pu_distributions_down)
mid_corrector  = MuonPOGCorrections.make_muon_pog_PFMedium_2016ReReco()
miso_corrector = MuonPOGCorrections.make_muon_pog_TightIso_2016ReReco("Medium")
trg_corrector  = MuonPOGCorrections.make_muon_pog_Mu50oTkMu50_2016ReReco()
trg_eff_corrector=MuonPOGCorrections_efficiencies.make_muon_pog_IsoMu24oIsoTkMu24_2016ReReco()
mtrk_corrector = MuonPOGCorrections.mu_trackingEta_MORIOND2017
#trk_corrector =  MuonPOGCorrections.make_muonptabove10_pog_tracking_corrections_2016()
#eId_corrector = EGammaPOGCorrections.make_egamma_pog_electronID_ICHEP2016( 'nontrigWP80')
eId_corrector = EGammaPOGCorrections.make_egamma_pog_electronID_MORIOND2017( 'nontrigWP80')
erecon_corrector=EGammaPOGCorrections.make_egamma_pog_recon_MORIOND17()


class Analyzer_MuE_highmass_200optimized_Mu50_pt65(MegaBase):
    tree = 'em/final/Ntuple'
    def __init__(self, tree, outfile, **kwargs):
        self.channel='EMu'
        super(Analyzer_MuE_highmass_200optimized_Mu50_pt65, self).__init__(tree, outfile, **kwargs)
        target = os.path.basename(os.environ['megatarget'])
        self.target=target

        self.generator=ROOT.TRandom3(0)
        self.is_WJet=('WJetsToLNu' in target or 'W1JetsToLNu' in target or 'W2JetsToLNu' in target or 'W3JetsToLNu' in target or 'W4JetsToLNu' in target)
        self.is_DYJet= ('DYJetsToLL_M-50' in target or  'DY1JetsToLL_M-50' in target or 'DY2JetsToLL_M-50' in target or 'DY3JetsToLL_M-50' in target or 'DY4JetsToLL_M-50' in target) 

        self.is_DYlowmass= ('DYJetsToLL_M-10to50' in target or  'DY1JetsToLL_M-10to50' in target or 'DY2JetsToLL_M-10to50' in target or 'DY3JetsToLL_M-10to50' in target or 'DY4JetsToLL_M-10to50' in target) 

        self.is_ZTauTau= ('ZTauTauJets_M-50' in target or  'ZTauTau1Jets_M-50' in target or 'ZTauTau2Jets_M-50' in target or 'ZTauTau3Jets_M-50' in target or 'ZTauTau4Jets_M-50' in target) 
        
        self.data_period="BCDEF" if ("Run2016B" in target or "Run2016C" in target or  "Run2016D" in target or  "Run2016E" in target or  "Run2016F" in target) else "GH"

        self.isData=('data' in target)

        #set systematics flag to true if you want shape syustematic histos
        self.syscalc=True
        
        self.isWGToLNuG=( 'WGToLNuG' in target)
        self.isWGstarToLNuEE=('WGstarToLNuEE' in target)
        self.isWGstarToLNuMuMu=('WGstarToLNuMuMu' in target)

        self.isST_tW_antitop=('ST_tW_antitop' in target)
        self.isST_tW_top=('ST_tW_top' in target)
        self.isST_t_antitop=('ST_t-channel_antitop' in target)
        self.isST_t_top=('ST_t-channel_top' in target)
        self.isTT=('TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_v6-v1' in target)
        self.isTTevtgen=('TT_TuneCUETP8M2T4_13TeV-powheg-pythia8-evtgen_v6-v1' in target)


        self.isGluGlu_LFV_HToMuTau_M200=('GluGlu_LFV_HToMuTau_M200' in target )
        self.isGluGlu_LFV_HToMuTau_M300=('GluGlu_LFV_HToMuTau_M300' in target )
        self.isGluGlu_LFV_HToMuTau_M450=('GluGlu_LFV_HToMuTau_M450' in target )
        self.isGluGlu_LFV_HToMuTau_M600=('GluGlu_LFV_HToMuTau_M600' in target )
        self.isGluGlu_LFV_HToMuTau_M750=('GluGlu_LFV_HToMuTau_M750' in target )
        self.isGluGlu_LFV_HToMuTau_M900=('GluGlu_LFV_HToMuTau_M900' in target )


        self.isWZTo2L2Q=('WZTo2L2Q' in target)
        self.isVVTo2L2Nu=('VVTo2L2Nu' in target)
        self.isWWTo1L1Nu2Q=('WWTo1L1Nu2Q' in target)
        self.isWZJToLLLNu=('WZJToLLLNu' in target)
        self.isWZTo1L1Nu2Q=('WZTo1L1Nu2Q' in target)
        self.isWZTo1L3Nu=('WZTo1L3Nu' in target)
        self.isZZTo2L2Q=('ZZTo2L2Q' in target)
        self.isZZTo4L=('ZZTo4L' in target)

        self.WZTo2L2Q_weight=2.39150954356e-08 
        self.VVTo2L2Nu_weight=5.53447020181e-08
        self.WWTo1L1Nu2Q_weight=1.14858944695e-07
        self.WZJToLLLNu_weight=3.33096092079e-07
        self.WZTo1L1Nu2Q_weight=2.54725706507e-08
        self.WZTo1L3Nu_weight=3.26075777445e-07
        self.ZZTo2L2Q_weight=4.13778925604e-08
        self.ZZTo4L_weight=5.92779186525e-08

 #        self.DYlowmass_weight=1.99619334706e-08

        self.WGToLNuG_weight=1.87611519302e-08  #3.36727421664e-08 #1.02004951008e-07 #1.03976258739e-07
        self.WGstarToLNuEE_weight=1.56725042226e-06 #1.56725042226e-06   #1.56725042226e-06
        self.WGstarToLNuMuMu_weight=1.25890428e-06  #1.25890428e-06    #1.25890428e-06 #1.25890428e-06

        self.ST_tW_antitop_weight=5.1347926337e-06 #5.23465826064e-06
        self.ST_tW_top_weight=5.12021723529e-06   #5.16316171138e-06
        self.ST_t_antitop_weight=6.75839027873e-07  #6.77839939377e-07
        self.ST_t_top_weight=6.55405568597e-07 #6.57612514709e-07
        self.TT_weight=1.09557853135e-05#1.20956576071e-05#1.08602238426e-05#1.07699999667e-05 #1.07699999667e-05  #1.08709111195e-05
        self.TTevtgen_weight=8.41414729168e-05#8.56505206262e-05#8.41414729168e-05 #8.80724961084e-05  #1.08709111195e-05

        self.WW_weight= 1.48725639285e-05  #1.49334492783e-05
        self.WZ_weight= 1.17948019785e-05  #1.17948019785e-05
        self.ZZ_weight= 8.3109585141e-06  #4.14537072254e-06


        self.GluGluHToWW_weight=1.91354271402e-06
        self.VBFHToWW_weight=4.09574479328e-08

        self.GluGluHToTT_weight=2.05507004808e-06  #2.07059122633e-06 
        self.ZHToTauTau_weight=1.28035908968e-07  #1.28035908968e-07
        self.WplusHToTauTau_weight=2.33513589465e-07
        self.WminusHToTauTau_weight=3.59334302781e-07
        self.VBFHToTT_weight=4.23479177085e-08                                   #4.23479177085e-08 
        self.ttHToTT_weight=7.1143619819e-08                                   #4.23479177085e-08 

        self.GluGlu_LFV_HToMuTau_M120_weight=5.22200000001e-06            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M125_weight=1.9432e-06            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M130_weight=4.531e-06            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M150_weight=3.2458506224e-06            #1.9432e-06 

        self.GluGlu_LFV_HToMuTau_M200_weight=1.694e-06            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M300_weight=1.33345743863e-07 #7.32222222221e-07            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M450_weight=4.65541809702e-08 #2.70588235294e-07            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M600_weight=2.04664734848e-08  #1.2625e-07    #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M750_weight=9.93800000005e-09            #1.9432e-06 
        self.GluGlu_LFV_HToMuTau_M900_weight=5.37000000001e-09            #1.9432e-06 


        self.VBF_LFV_HToMuTau_M120_weight=1.01169556062e-07            #1.9432e-06 
        self.VBF_LFV_HToMuTau_M125_weight=4.23479177085e-08            #1.9432e-06 
        self.VBF_LFV_HToMuTau_M130_weight=1.01192215127e-07            #1.9432e-06 
        self.VBF_LFV_HToMuTau_M150_weight=1.05129570004e-07            #1.9432e-06 
        self.VBF_LFV_HToMuTau_M200_weight=1.05303474276e-07          #1.9432e-06 


        self.GluGlu_LFV_HToETau_weight=1.9432e-06    #1.9432e-06 
        self.VBF_LFV_HToETau_weight=4.05239613191e-08  #1.83818883478e-07  


        self.tree = EMTree(tree)
        self.out=outfile
        self.histograms = {}
        self.mym1='m'
        self.mye1='e'
        if self.syscalc and not self.isData:
#            self.sysdir=['nosys','mesup']
            self.sysdir=['nosys','uup','udown','chargeduesdown','chargeduesup','ecaluesdown','ecaluesup','hcaluesdown','hcaluesup','hfuesdown','hfuesup','mesup','mesdown','eesup','eesdown','eresrhoup','eresrhodown','eresphidown','puup','pudown']
            self.jetsysdir=['jes_JetAbsoluteFlavMapDown',
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
                            'jes_JetTimePtEtaUp']
        else:
            self.sysdir=['nosys']
            self.jetsysdir=[]
#        self.sysdir=['nosys']
        if self.is_WJet:
            self.binned_weight=[0.709390278,0.190063899,0.058529964,0.019206445,0.01923548]
#0.709390278,0.190063899,0.058529964,0.019206445,0.01923548]
#0.709521921,0.190073347,0.059034569,0.019318685,0.019344044]

        elif self.is_DYJet:
            self.binned_weight=[0.039542337,0.012748615,0.013012785,0.013380213,0.010969872]
#0.040812575,0.012877836,0.013147445,0.013522627,0.011065415]
#0.117315804,0.016214144,0.016643878,0.017249744,0.01344205]
#0.119211763,0.016249863,0.016824004,0.017799422,0.014957552]
        elif self.is_ZTauTau:
            self.binned_weight=[0.039542337,0.012748615,0.013012785,0.013380213,0.010969872]
#            self.binned_weight=[0.040812575,0.012877836,0.013147445,0.013522627,0.011065415]
#            self.binned_weight=[0.117315804,0.016214144,0.016643878,0.017249744,0.01344205]
#0.119211763,0.016249863,0.016824004,0.017799422,0.014957552]

        elif self.is_DYlowmass:
            self.binned_weight=[0.527321457,0.01037153,0.009311641,0.527321457,0.527321457]
#0.527321457,0.011589863,0.009311641,0.527321457,0.527321457]

        else:
            self.binned_weight=[1,1,1,1,1]
        """need to think about this"""




    def mc_corrector_2015(self, row, region,pileup='nominal'):
        pu = pu_corrector(row.nTruePU)
        if pileup=='up':
            pu = pu_corrector_up(row.nTruePU) 
        if pileup=='down':
            pu = pu_corrector_down(row.nTruePU) 
        electron_Pt=self.my_elec.Pt()
        electron_Eta=self.my_elec.Eta()
        muon_Pt=self.my_muon.Pt()
        muon_Eta=self.my_muon.Eta()
#        print electron_Eta," ",muon_Eta
        muidcorr = mid_corrector(muon_Pt, abs(muon_Eta))
        muisocorr = miso_corrector(muon_Pt, abs(muon_Eta))
        mutrcorr = trg_corrector(muon_Pt, abs(muon_Eta))
        
        mutrkcorr=mtrk_corrector(muon_Eta)[0]
        eidcorr = eId_corrector(electron_Eta,electron_Pt)
        ereconcorr=erecon_corrector(electron_Eta,electron_Pt)
#        eidisocorr0p10= eidiso_corr0p10(getattr(row, self.mye1+'Pt'),abs(getattr(row,self.mye1+'Eta')))[0]
#        eidisocorr0p15= eidiso_corr0p15(getattr(row, self.mye1+'Pt'),abs(getattr(row,self.mye1+'Eta')))[0]
#        etrkcorr=etrk_corrector(getattr(row,self.mye1+'Eta'),getattr(row, self.mye1+'Pt'))
#        print "id corr", muidcorr
#        print "iso corr", muisocorr
#        print "pu  ",pu
#        print "trk corr",mutrkcorr
#        print "tr corr", mutrcorr
#        print "eidiso corr", eidcorr
#        print "etack ",ereconcorr
###       mutrcorr=1
     # if pu*muidcorr1*muisocorr1*muidcorr2*muisocorr2*mutrcorr==0: print pu, muidcorr1, muisocorr1, muidcorr2, muisocorr2, mutrcorr
 #       if pu>2:
#            print "pileup--------   =",pu
   #     print pu*muidcorr*muisocorr*mutrcorr
#        print eisocorr

        topptreweight=1

        if self.isTT:
            topptreweight=topPtreweight(row.topQuarkPt1,row.topQuarkPt2)

        return pu*muidcorr*muisocorr*mutrcorr*mutrkcorr*topptreweight*eidcorr*ereconcorr


    def correction(self,row,region,pileup):
	return self.mc_corrector_2015(row,region,pileup)
        
    def event_weight(self, row, region,pileup):
 
        if row.run > 2: #FIXME! add tight ID correction
            return 1.
       # if row.GenWeight*self.correction(row) == 0 : print 'weight==0', row.GenWeight*self.correction(row), row.GenWeight, self.correction(row), row.m1Pt, row.m2Pt, row.m1Eta, row.m2Eta
       # print row.GenWeight, "lkdfh"


        return row.GenWeight*self.correction(row,region,pileup) 
#        return self.correction(row) 






    def begin(self):


        sign=[ 'ss','os']
        jetN = [0,1,2]
        folder=[]

#        alldirs=['','antiIsolatedweighted/','antiIsolated/','antiIsolatedweightedelectron/','antiIsolatedweightedmuon/','antiIsolatedweightedmuonelectron/','fakeRateMethod/']
        alldirs=['']#,'antiIsolatedweighted/','antiIsolated/']#,'qcdshaperegion/']
#        alldirs=['']
        for d  in alldirs :
            for i in sign:
                for jn in jetN: 
                    folder.append(d+i+'/'+str(jn))
                    for s in self.sysdir:
                        folder.append(d+i+'/'+str(jn)+'/selected/'+s)
                    for jes in self.jetsysdir:
                        folder.append(d+i+'/'+str(jn)+'/selected/'+jes)
   
                            

        for k in range(len(folder)):
            f=folder[k]
            if 'selected' not in f:
                self.book(f,"mPt", "mu p_{T}", 100, 0, 500)
                self.book(f,"mPhi", "mu phi", 100, -3.2, 3.2)
                self.book(f,"mEta", "mu eta",  50, -2.5, 2.5)
            
                self.book(f,"ePt", "e p_{T}", 100, 0, 500)
                self.book(f,"ePhi", "e phi",  100, -3.2, 3.2)
                self.book(f,"eEta", "e eta", 50, -2.5, 2.5)
            
                self.book(f, "em_DeltaPhi", "e-mu DeltaPhi" , 50, 0, 3.2)
                self.book(f, "em_DeltaR", "e-mu DeltaR" , 100, -7, 7)

                self.book(f, "h_vismass",  "h_vismass",  300,0,1500)
                self.book(f, "h_collmass_pfmet",  "h_collmass_pfmet",  300,0,1500)

                self.book(f, "Met",  "Met",  100, 0, 500)
                self.book(f, "mPFMET_Mt", "mu-PFMET M_{T}" , 200, 0, 1000)
                self.book(f, "ePFMET_Mt", "e-PFMET M_{T}" , 200, 0, 1000)           
                self.book(f, "mPFMET_DeltaPhi", "mu-PFMET DeltaPhi" , 50, 0, 3.2)
                self.book(f, "ePFMET_DeltaPhi", "e-PFMET DeltaPhi" , 50, 0, 3.2)

                self.book(f, "vbfMass","vbf dijet mass",500,0,5000)
                self.book(f, "vbfDeta","vbf Delta Eta",50,0,5)

                self.book(f, "jetN_30", "Number of jets, p_{T}>30", 10, -0.5, 9.5) 
            else:
                self.book(f, "h_collmass_pfmet",  "h_collmass_pfmet",  300,0,1500)
                self.book(f, "h_vismass",  "h_vismass",  300, 0, 1500)

        for s in sign:
            self.book(s+'/tNoCuts', "CUT_FLOW", "Cut Flow", len(cut_flow_step), 0, len(cut_flow_step))

            self.book(s, "jetN_30", "Number of jets, p_{T}>30", 10, -0.5, 9.5) 
            self.book(s, "NUP", "Number of Partons", 12, -0.5, 11.5) 
            self.book(s, "numGenJets", "Number of Gen Level Jets", 12, -0.5, 11.5) 
            self.book(s, "numVertices", "Number of Vertices", 60, 0, 60) 
            self.book(s, "h_collmass_pfmet", "h_collmass_pfmet", 300,0,1500) 
            self.book(s, "h_vismass",  "h_vismass",  300,0,1500)


            self.book(s, "Met",  "Met",  100, 0, 500) 
            self.book(s, "mPFMET_Mt", "mu-PFMET M_{T}" , 200, 0, 1000)
            self.book(s, "ePFMET_Mt", "e-PFMET M_{T}" , 200, 0, 1000)           
            self.book(s, "mPFMET_DeltaPhi", "mu-PFMET DeltaPhi" , 50, 0, 3.2)
            self.book(s, "ePFMET_DeltaPhi", "e-PFMET DeltaPhi" , 50, 0, 3.2)

            self.book(s,"mPt", "mu p_{T}", 100, 0, 500)
            self.book(s,"mPhi", "mu phi", 100, -3.2, 3.2)
            self.book(s,"mEta", "mu eta",  50, -2.5, 2.5)
            
            self.book(s,"ePt", "e p_{T}", 100, 0, 500)
            self.book(s,"ePhi", "e phi",  100, -3.2, 3.2)
            self.book(s,"eEta", "e eta", 50, -2.5, 2.5)
            
            self.book(s, "em_DeltaPhi", "e-mu DeltaPhi" , 50, 0, 3.2)
            self.book(s, "em_DeltaR", "e-mu DeltaR" , 100, -7, 7)

            xaxis = self.histograms[s+'/tNoCuts/CUT_FLOW'].GetXaxis()
            self.cut_flow_histo = self.histograms[s+'/tNoCuts/CUT_FLOW']
            self.cut_flow_map   = {}
            for i, name in enumerate(cut_flow_step):
                xaxis.SetBinLabel(i+1, name)
                self.cut_flow_map[name] = i+0.5


    def fill_jet_histos(self,row,sign,region,btagweight):

        if self.is_WJet or self.is_DYJet:
            weight1 = self.event_weight(row,region)*self.binned_weight[int(row.numGenJets)]
        else:
            weight1 = self.event_weight(row,region)

        weight1=btagweight*weight1
        self.histograms[sign+'/jetN_30'].Fill(row.jetVeto30,weight1)
        self.histograms[sign+'/NUP'].Fill(row.NUP,weight1)
        self.histograms[sign+'/numGenJets'].Fill(row.numGenJets,weight1)


    def get_fakerate(self,row):
        if row.ePt<10:
            raise ValueError("electron Pt less than 10")
        elecPt=row.ePt if row.ePt<200 else 200
        if abs(row.eEta)<1.479: #par[0]+par[1]*TMath::Erf(par[2]*x - par[3])  Barrel
            fakerateFactor=0.449+0.289*ROOT.TMath.Erf(0.043*elecPt-2.686)
        else:#endcap par[0]+par[1]*x
            fakerateFactor=0.268+0.001*elecPt

        return fakerateFactor/(1-fakerateFactor)
            
            

    def fill_histos(self, row,sign,f=None,fillCommonOnly=False,region=None,btagweight=1,sys='',qcdshape=None,pileup='nominal'):


        if self.is_WJet or self.is_DYJet or self.is_DYlowmass or self.is_ZTauTau:
            weight = self.event_weight(row,region,pileup) *self.binned_weight[int(row.numGenJets)]*0.001
        
        elif self.isWGToLNuG:
            weight=self.WGToLNuG_weight*self.event_weight(row,region,pileup) 
        elif self.isWGstarToLNuEE:
            weight=self.WGstarToLNuEE_weight*self.event_weight(row,region,pileup) 
        elif self.isWGstarToLNuMuMu:
            weight=self.WGstarToLNuMuMu_weight*self.event_weight(row,region,pileup) 
        
        elif self.isST_tW_top:
            weight=self.ST_tW_top_weight*self.event_weight(row,region,pileup) 
        elif self.isST_tW_antitop:
            weight=self.ST_tW_antitop_weight*self.event_weight(row,region,pileup) 
        elif self.isST_t_top:
            weight=self.ST_t_top_weight*self.event_weight(row,region,pileup) 
        elif self.isST_t_antitop:
            weight=self.ST_t_antitop_weight*self.event_weight(row,region,pileup) 
        
        
        elif self.isWZTo2L2Q:
            weight=self.WZTo2L2Q_weight*self.event_weight(row,region,pileup) 
        elif self.isVVTo2L2Nu:
            weight=self.VVTo2L2Nu_weight*self.event_weight(row,region,pileup) 
        elif self.isWWTo1L1Nu2Q:
            weight=self.WWTo1L1Nu2Q_weight*self.event_weight(row,region,pileup) 
        elif self.isWZJToLLLNu:
            weight=self.WZJToLLLNu_weight*self.event_weight(row,region,pileup) 
        elif self.isWZTo1L1Nu2Q:
            weight=self.WZTo1L1Nu2Q_weight*self.event_weight(row,region,pileup) 
        elif self.isWZTo1L3Nu:
            weight=self.WZTo1L3Nu_weight*self.event_weight(row,region,pileup) 
        elif self.isZZTo2L2Q:
            weight=self.ZZTo2L2Q_weight*self.event_weight(row,region,pileup) 
        elif self.isZZTo4L:
            weight=self.ZZTo4L_weight*self.event_weight(row,region,pileup) 
        
        elif self.isTT:
            weight=self.TT_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M200:
            weight=self.GluGlu_LFV_HToMuTau_M200_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M300:
            weight=self.GluGlu_LFV_HToMuTau_M300_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M450:
            weight=self.GluGlu_LFV_HToMuTau_M450_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M600:
            weight=self.GluGlu_LFV_HToMuTau_M600_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M750:
            weight=self.GluGlu_LFV_HToMuTau_M750_weight*self.event_weight(row,region,pileup) 
        elif self.isGluGlu_LFV_HToMuTau_M900:
            weight=self.GluGlu_LFV_HToMuTau_M900_weight*self.event_weight(row,region,pileup) 
        else:
            weight = self.event_weight(row,region,pileup) 
            
        weight=btagweight*weight
        #fill some histograms before dividing into categories (looking at some variables before dividing into njet categories makes more sense)
        if fillCommonOnly==True:
            if region=='signal':
                if sys=='presel':
                    self.histograms[sign+'/jetN_30'].Fill(row.jetVeto30,weight)
                    self.histograms[sign+'/NUP'].Fill(row.NUP,weight)
                    self.histograms[sign+'/numGenJets'].Fill(row.numGenJets,weight)
                    self.histograms[sign+'/numVertices'].Fill(row.nvtx,weight)
                    self.histograms[sign+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt,row.type1_pfMetPhi,self.my_elec,self.my_muon),weight)
                    self.histograms[sign+'/h_vismass'].Fill(row.e_m_Mass,weight)
                    self.histograms[sign+'/mPt'].Fill(row.mPt, weight)
                    self.histograms[sign+'/Met'].Fill(row.type1_pfMetEt, weight)
                    self.histograms[sign+'/mEta'].Fill(row.mEta, weight)
                    self.histograms[sign+'/mPhi'].Fill(row.mPhi, weight) 
                    self.histograms[sign+'/ePt'].Fill(row.ePt, weight)
                    self.histograms[sign+'/eEta'].Fill(row.eEta, weight)
                    self.histograms[sign+'/ePhi'].Fill(row.ePhi, weight)
                    self.histograms[sign+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), weight)
                    self.histograms[sign+'/em_DeltaR'].Fill(row.e_m_DR, weight)
                    self.histograms[sign+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, weight)
                    self.histograms[sign+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, weight)
                    self.histograms[sign+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), weight)
                    self.histograms[sign+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), weight)
                else:
                    self.histograms[sign+'/'+sys+'/BDT_value'].Fill(MVAvalue,weight)
                    self.histograms[sign+'/'+sys+'/h_collmass_pfmet'].Fill(collmass(row,self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),weight)                     
                    self.histograms[sign+'/'+sys+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), weight)
                return 1
            else:
                return 0

        histos = self.histograms
        pudir=['']
        #pudir =['','fakeRateMethod/'] need to uncomment if using old method for fake rate
        elooseList = ['antiIsolatedweightedelectron/']
        mlooseList = ['antiIsolatedweightedmuon/']
        emlooseList= ['antiIsolatedweightedmuonelectron/']
        alllooselist=['antiIsolatedweighted/','antiIsolated/']
        
        qcdshapelist=['qcdshaperegion/']
        
        """

        if region=='eLoosemTight':
            frarray=self.get_fakerate(row) 
            fakerateWeight=frarray
            antiIsolatedWeightList=[fakerateWeight,1]
            for n, l in enumerate(elooseList) :
                antiIsolatedWeight= weight*antiIsolatedWeightList[n]
                folder = l+f
                if sys=='presel':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)
                    histos[folder+'/mPt'].Fill(row.mPt, antiIsolatedWeight)
                    histos[folder+'/Met'].Fill(row.type1_pfMetEt, antiIsolatedWeight)
                    histos[folder+'/mEta'].Fill(row.mEta, antiIsolatedWeight)
                    histos[folder+'/mPhi'].Fill(row.mPhi, antiIsolatedWeight) 
                    histos[folder+'/ePt'].Fill(row.ePt, antiIsolatedWeight)
                    histos[folder+'/eEta'].Fill(row.eEta, antiIsolatedWeight)
                    histos[folder+'/ePhi'].Fill(row.ePhi, antiIsolatedWeight)
                    histos[folder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), antiIsolatedWeight)
                    histos[folder+'/em_DeltaR'].Fill(row.e_m_DR, antiIsolatedWeight)
                    histos[folder+'/h_vismass'].Fill(row.e_m_Mass, antiIsolatedWeight)
                    histos[folder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), antiIsolatedWeight)
                    histos[folder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), antiIsolatedWeight)
#                    histos[folder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , antiIsolatedWeight)
                    histos[folder+'/vbfMass'].Fill(row.vbfMass, antiIsolatedWeight)
                    histos[folder+'/vbfDeta'].Fill(row.vbfDeta, antiIsolatedWeight)
                    histos[folder+'/jetN_30'].Fill(row.jetVeto30, antiIsolatedWeight) 
                elif sys=='nosys':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)
        if region=='eTightmLoose':
            fakerateWeight=4
            antiIsolatedWeightList=[fakerateWeight,1]
            for n, l in enumerate(mlooseList) :
                antiIsolatedWeight= weight*antiIsolatedWeightList[n]
                folder = l+f
                if sys=='presel':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)
                    histos[folder+'/mPt'].Fill(row.mPt, antiIsolatedWeight)
                    histos[folder+'/Met'].Fill(row.type1_pfMetEt, antiIsolatedWeight)
                    histos[folder+'/mEta'].Fill(row.mEta, antiIsolatedWeight)
                    histos[folder+'/mPhi'].Fill(row.mPhi, antiIsolatedWeight) 
                    histos[folder+'/ePt'].Fill(row.ePt, antiIsolatedWeight)
                    histos[folder+'/eEta'].Fill(row.eEta, antiIsolatedWeight)
                    histos[folder+'/ePhi'].Fill(row.ePhi, antiIsolatedWeight)
                    histos[folder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), antiIsolatedWeight)
                    histos[folder+'/em_DeltaR'].Fill(row.e_m_DR, antiIsolatedWeight)
                    histos[folder+'/h_vismass'].Fill(row.e_m_Mass, antiIsolatedWeight)
                    histos[folder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), antiIsolatedWeight)
                    histos[folder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), antiIsolatedWeight)
#                    histos[folder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , antiIsolatedWeight)
                    histos[folder+'/vbfMass'].Fill(row.vbfMass, antiIsolatedWeight)
                    histos[folder+'/vbfDeta'].Fill(row.vbfDeta, antiIsolatedWeight)
                    histos[folder+'/jetN_30'].Fill(row.jetVeto30, antiIsolatedWeight) 
                elif sys=='nosys':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)

        if region=='eLoosemLoose':
            efrarray=self.get_fakerate(row)
            efakerateWeight=efrarray
            mfakerateWeight=4
            antiIsolatedWeightList=[mfakerateWeight*efakerateWeight,1]
            for n, l in enumerate(emlooseList) :
                antiIsolatedWeight= weight*antiIsolatedWeightList[n]
                folder = l+f
                if sys=='presel':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)
                    histos[folder+'/mPt'].Fill(row.mPt, antiIsolatedWeight)
                    histos[folder+'/Met'].Fill(row.type1_pfMetEt, antiIsolatedWeight)
                    histos[folder+'/mEta'].Fill(row.mEta, antiIsolatedWeight)
                    histos[folder+'/mPhi'].Fill(row.mPhi, antiIsolatedWeight) 
                    histos[folder+'/ePt'].Fill(row.ePt, antiIsolatedWeight)
                    histos[folder+'/eEta'].Fill(row.eEta, antiIsolatedWeight)
                    histos[folder+'/ePhi'].Fill(row.ePhi, antiIsolatedWeight)
                    histos[folder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), antiIsolatedWeight)
                    histos[folder+'/em_DeltaR'].Fill(row.e_m_DR, antiIsolatedWeight)
                    histos[folder+'/h_vismass'].Fill(row.e_m_Mass, antiIsolatedWeight)
                    histos[folder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), antiIsolatedWeight)
                    histos[folder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), antiIsolatedWeight)
#                    histos[folder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , antiIsolatedWeight)
                    histos[folder+'/vbfMass'].Fill(row.vbfMass, antiIsolatedWeight)
                    histos[folder+'/vbfDeta'].Fill(row.vbfDeta, antiIsolatedWeight)
                    histos[folder+'/jetN_30'].Fill(row.jetVeto30, antiIsolatedWeight) 
                elif sys=='nosys':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),antiIsolatedWeight)
                    """
        if region!='signal':
            if region=='eLoosemTight':
                frarray=self.get_fakerate(row)
                fakerateWeight=frarray
            elif region=='eTightmLoose':
                fakerateWeight=4
            elif region=='eLoosemLoose':
                frarray=self.get_fakerate(row)
                efakerateWeight=frarray
                mfakerateWeight=4
                fakerateWeight=-efakerateWeight*mfakerateWeight
            antiIsolatedWeightList=[fakerateWeight,1]
            for n, l in enumerate(alllooselist):
                antiIsolatedWeight= weight*antiIsolatedWeightList[n]
                folder = l+f
                if sys=='presel':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row, self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),antiIsolatedWeight)
                    histos[folder+'/mPt'].Fill(row.mPt, antiIsolatedWeight)
                    histos[folder+'/Met'].Fill(row.type1_pfMetEt, antiIsolatedWeight)
                    histos[folder+'/mEta'].Fill(row.mEta, antiIsolatedWeight)
                    histos[folder+'/mPhi'].Fill(row.mPhi, antiIsolatedWeight) 
                    histos[folder+'/ePt'].Fill(row.ePt, antiIsolatedWeight)
                    histos[folder+'/eEta'].Fill(row.eEta, antiIsolatedWeight)
                    histos[folder+'/ePhi'].Fill(row.ePhi, antiIsolatedWeight)
                    histos[folder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), antiIsolatedWeight)
                    histos[folder+'/em_DeltaR'].Fill(row.e_m_DR, antiIsolatedWeight)
                    histos[folder+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), antiIsolatedWeight)
                    histos[folder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, antiIsolatedWeight)
                    histos[folder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), antiIsolatedWeight)
                    histos[folder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), antiIsolatedWeight)
#                    histos[folder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , antiIsolatedWeight)
                    histos[folder+'/vbfMass'].Fill(row.vbfMass, antiIsolatedWeight)
                    histos[folder+'/vbfDeta'].Fill(row.vbfDeta, antiIsolatedWeight)
                    histos[folder+'/jetN_30'].Fill(row.jetVeto30, antiIsolatedWeight) 
                elif sys=='nosys':
                    histos[folder+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), antiIsolatedWeight)
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row, self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),antiIsolatedWeight)
                else:
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row, self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),antiIsolatedWeight)

                    """            
            if not self.isData and not self.isGluGlu_LFV and not self.isVBF_LFV and not self.isGluGluEtauSig and not self.isVBFEtauSig:
                if region=='eLoosemTight':
                    frarray=self.get_fakerate(row)
                    efakerateWeight=frarray
                elif region=='eTightmLoose':
                    fakerateWeight=4
                elif region=='eLoosemLoose':
                    frarray=self.get_fakerate(row)
                    efakerateWeight=frarray
                    mfakerateWeight=4
                    fakerateweight=-efakerateWeight*mfakerateWeight
                antiIsolatedWeightList=[fakerateWeight,1]
                fakeRateMethodfolder=pudir[1]+f
                fakeRateMethodweight=fakerateWeight*weight*(-1)

                if sys=='presel':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMetEt, row.type1_pfMetPhi),fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/Met'].Fill(row.type1_pfMetEt, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/mPt'].Fill(row.mPt, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/mEta'].Fill(row.mEta, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/mPhi'].Fill(row.mPhi, fakeRateMethodweight) 
                    histos[fakeRateMethodfolder+'/ePt'].Fill(row.ePt, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/eEta'].Fill(row.eEta, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/ePhi'].Fill(row.ePhi, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/em_DeltaR'].Fill(row.e_m_DR, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/h_vismass'].Fill(row.e_m_Mass, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), fakeRateMethodweight)
                #               histos[fakeRateMethodfolder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/vbfMass'].Fill(row.vbfMass, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/vbfDeta'].Fill(row.vbfDeta, fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/jetN_30'].Fill(row.jetVeto30, fakeRateMethodweight) 
                elif sys=='nosys':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row,row.type1_pfMetEt, row.type1_pfMetPhi),fakeRateMethodweight)
                    histos[fakeRateMethodfolder+'/Met'].Fill(row.type1_pfMetEt, fakeRateMethodweight)
                elif sys=='jetup':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_JetEnUp, row.type1_pfMet_shiftedPhi_JetEnUp),fakeRateMethodweight)
                elif sys=='jetdown':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_JetEnDown, row.type1_pfMet_shiftedPhi_JetEnDown),fakeRateMethodweight)
                elif sys=='tup':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_TauEnUp, row.type1_pfMet_shiftedPhi_TauEnUp),fakeRateMethodweight)
                elif sys=='tdown':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_TauEnDown, row.type1_pfMet_shiftedPhi_TauEnDown),fakeRateMethodweight)
                elif sys=='uup':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_UnclusteredEnUp, row.type1_pfMet_shiftedPhi_UnclusteredEnUp),fakeRateMethodweight)
                elif sys=='udown':
                    histos[fakeRateMethodfolder+'/h_collmass_pfmet'].Fill(collmass(row, row.type1_pfMet_shiftedPt_UnclusteredEnDown, row.type1_pfMet_shiftedPhi_UnclusteredEnDown),fakeRateMethodweight)
                    """
        if region=='signal' :
            for n,d  in enumerate(pudir) :
                folder = d+f                
                if sys=='presel':
                    histos[folder+'/mPt'].Fill(row.mPt, weight)
                    histos[folder+'/mEta'].Fill(row.mEta, weight)
                    histos[folder+'/mPhi'].Fill(row.mPhi, weight) 
                    histos[folder+'/ePt'].Fill(row.ePt, weight)
                    histos[folder+'/eEta'].Fill(row.eEta, weight)
                    histos[folder+'/ePhi'].Fill(row.ePhi, weight)
                    histos[folder+'/em_DeltaPhi'].Fill(deltaPhi(row.ePhi, row.mPhi), weight)
                    histos[folder+'/em_DeltaR'].Fill(row.e_m_DR, weight)
                    histos[folder+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), weight)
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),weight)
 #                   histos[folder+'/scaledmPt'].Fill(float(row.mPt)/float(collmass(row, row.type1_pfMetEt, row.type1_pfMetPhi)),weight)
 #                   histos[folder+'/scaledePt'].Fill(float(row.ePt)/float(collmass(row, row.type1_pfMetEt, row.type1_pfMetPhi)),weight)
 #
                    histos[folder+'/Met'].Fill(row.type1_pfMetEt, weight)

                    histos[folder+'/ePFMET_Mt'].Fill(row.eMtToPfMet_type1, weight)
                    histos[folder+'/mPFMET_Mt'].Fill(row.mMtToPfMet_type1, weight)
                    histos[folder+'/ePFMET_DeltaPhi'].Fill(abs(row.eDPhiToPfMet_type1), weight)
                    histos[folder+'/mPFMET_DeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1), weight)
#                    histos[folder+'/mPFMETDeltaPhi_vs_ePFMETDeltaPhi'].Fill(abs(row.mDPhiToPfMet_type1),abs(row.eDPhiToPfMet_type1) , weight)
 
                    histos[folder+'/vbfMass'].Fill(row.vbfMass, weight)
                    histos[folder+'/vbfDeta'].Fill(row.vbfDeta, weight)
                    histos[folder+'/jetN_30'].Fill(row.jetVeto30, weight) 

                elif sys=='nosys':
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),weight)                     
                    histos[folder+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), weight)
                else:
                    histos[folder+'/h_collmass_pfmet'].Fill(collmass(row,self.shifted_type1_pfMetEt,self.shifted_type1_pfMetPhi,self.my_elec,self.my_muon),weight)
                    histos[folder+'/h_vismass'].Fill((self.my_elec+self.my_muon).M(), weight)
                
    def process(self):
        cut_flow_histo = self.cut_flow_histo
        cut_flow_trk   = cut_flow_tracker(cut_flow_histo)
        myevent=()
        frw = []
        curr_event=0
        for row in self.tree:
            sign = 'ss' if row.e_m_SS else 'os'

            cut_flow_trk.new_row(row.run,row.lumi,row.evt)
           
            cut_flow_trk.Fill('allEvents')

            if (self.is_ZTauTau and not row.isZtautau and not self.is_DYlowmass):
                continue
            if (not self.is_ZTauTau and row.isZtautau and not self.is_DYlowmass):
                continue

 #           ptthreshold = [30]
            repeatEvt=True
            if row.evt!=curr_event:
                curr_event=row.evt
                repeatEvt=False
            
            if repeatEvt:continue

#            print "non-repeat"
            processtype ='gg'##changed from 20

            
            if (not bool(row.singleMu50Pass or row.singleTkMu50Pass)) : 
                continue 

            cut_flow_trk.Fill('HLTIsoPasstrg')

            #vetoes and cleaning
            
            if row.muVetoPt5IsoIdVtx :continue
            cut_flow_trk.Fill('surplus_mu_veto')

            if row.eVetoMVAIsoVtx :continue
            cut_flow_trk.Fill('surplus_e_veto')

            if row.tauVetoPt20Loose3HitsVtx : continue
            cut_flow_trk.Fill('surplus_tau_veto')

 
            nbtagged=row.bjetCISVVeto30Medium
            if nbtagged>2:
                continue
            btagweight=1
            if (self.isData and nbtagged>0):
                continue
            if nbtagged>0:
                if nbtagged==1:
                    btagweight=bTagSF.bTagEventWeight(nbtagged,row.jb1pt,row.jb1hadronflavor,row.jb2pt,row.jb2hadronflavor,1,0,0) if (row.jb1pt>-990 and row.jb1hadronflavor>-990) else 0
                if nbtagged==2:
                    btagweight=bTagSF.bTagEventWeight(nbtagged,row.jb1pt,row.jb1hadronflavor,row.jb2pt,row.jb2hadronflavor,1,0,0) if (row.jb1pt>-990 and row.jb1hadronflavor>-990 and row.jb2pt>-990 and row.jb2hadronflavor>-990) else 0
#                print "btagweight,nbtagged,row.jb1pt,row.jb1hadronflavor,row.jb2pt,row.jb2hadronflavor"," ",btagweight," ",nbtagged," ",row.jb1pt," ",row.jb1hadronflavor," ",row.jb2pt," ",row.jb2hadronflavor

#            if btagweight<0:btagweight=0

            if btagweight==0: continue

            cut_flow_trk.Fill('bjetveto')
            ## All preselection passed



            ##do stuff for qcd shape region
            qcdshaperegion=False
 


            for sys in self.sysdir:

                self.my_muon=ROOT.TLorentzVector()
                self.my_muon.SetPtEtaPhiM(row.mPt,row.mEta,row.mPhi,row.mMass)
                
                self.my_elec=ROOT.TLorentzVector()
                self.my_elec.SetPtEtaPhiM(row.ePt,row.eEta,row.ePhi,row.eMass)

                self.my_MET=ROOT.TLorentzVector()
                self.my_MET.SetPtEtaPhiM(row.type1_pfMetEt,0,row.type1_pfMetPhi,0)

                self.shifted_jetVeto30=row.jetVeto30


                self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                self.shifted_type1_pfMetEt=self.my_MET.Pt()
                self.shifted_vbfMass=row.vbfMass
                self.shifted_vbfDeta=row.vbfDeta
                
                self.pileup='nominal'

                if sys =='nosys':
                    self.shifted_jetVeto30=row.jetVeto30
                elif sys =='puup':
                    self.pileup='up'
                elif sys =='pudown':
                    self.pileup='down'
                elif sys =='uup':
                    self.shifted_mDPhiToPfMet=row.mDPhiToPfMet_UnclusteredEnUp
                    self.shifted_mMtToPfMet=row.mMtToPfMet_UnclusteredEnUp
                    self.shifted_eDPhiToPfMet=row.eDPhiToPfMet_UnclusteredEnUp
                    self.shifted_eMtToPfMet=row.eMtToPfMet_UnclusteredEnUp
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_UnclusteredEnUp
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_UnclusteredEnUp
                elif sys =='udown':
                    self.shifted_mDPhiToPfMet=row.mDPhiToPfMet_UnclusteredEnDown
                    self.shifted_mMtToPfMet=row.mMtToPfMet_UnclusteredEnDown
                    self.shifted_eDPhiToPfMet=row.eDPhiToPfMet_UnclusteredEnDown
                    self.shifted_eMtToPfMet=row.eMtToPfMet_UnclusteredEnDown
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_UnclusteredEnDown
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_UnclusteredEnDown
                elif sys =='chargeduesdown':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_CHARGEDUESDown
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_CHARGEDUESDown
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='chargeduesup':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_CHARGEDUESUp
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_CHARGEDUESUp
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='ecaluesdown':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_ECALUESDown
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_ECALUESDown
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='ecaluesup':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_ECALUESUp
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_ECALUESUp
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='hcaluesdown':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_HCALUESDown
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_HCALUESDown
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())


                elif sys =='hcaluesup':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_HCALUESUp
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_HCALUESUp
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                elif sys =='hfuesdown':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_HFUESDown
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_HFUESDown
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                elif sys =='hfuesup':
                    self.shifted_type1_pfMetPhi=row.type1_pfMet_shiftedPhi_HFUESUp
                    self.shifted_type1_pfMetEt=row.type1_pfMet_shiftedPt_HFUESUp
                    self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())

                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='mesup':
                    self.my_METpx=self.my_MET.Px()-0.002*self.my_muon.Px()
                    self.my_METpy=self.my_MET.Py()-0.002*self.my_muon.Py()
                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))

                    self.my_muon*=ROOT.Double(1.002)
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='mesdown':
                    self.my_METpx=self.my_MET.Px()+0.002*self.my_muon.Px()
                    self.my_METpy=self.my_MET.Py()+0.002*self.my_muon.Py()
                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))

                    self.my_muon*=ROOT.Double(0.998)
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='eesup':
                    self.my_METpx=self.my_MET.Px()+self.my_elec.Px()
                    self.my_METpy=self.my_MET.Py()+self.my_elec.Py()
                    self.my_elec.SetPtEtaPhiM(row.ePt_ElectronScaleUp,row.eEta,row.ePhi,row.eMass)
                    self.my_METpx-=self.my_elec.Px()
                    self.my_METpy-=self.my_elec.Py()

                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))
                    
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='eesdown':
                    self.my_METpx=self.my_MET.Px()+self.my_elec.Px()
                    self.my_METpy=self.my_MET.Py()+self.my_elec.Py()

                    self.my_elec.SetPtEtaPhiM(row.ePt_ElectronScaleDown,row.eEta,row.ePhi,row.eMass)

                    self.my_METpx-=self.my_elec.Px()
                    self.my_METpy-=self.my_elec.Py()

                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))

                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='eresrhoup':
                    self.my_METpx=self.my_MET.Px()+self.my_elec.Px()
                    self.my_METpy=self.my_MET.Py()+self.my_elec.Py()
                    self.my_elec.SetPtEtaPhiM(row.ePt_ElectronResRhoUp,row.eEta,row.ePhi,row.eMass)
                    self.my_METpx-=self.my_elec.Px()
                    self.my_METpy-=self.my_elec.Py()

                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='eresrhodown':
                    self.my_METpx=self.my_MET.Px()+self.my_elec.Px()
                    self.my_METpy=self.my_MET.Py()+self.my_elec.Py()
                    self.my_elec.SetPtEtaPhiM(row.ePt_ElectronResRhoDown,row.eEta,row.ePhi,row.eMass)
                    self.my_METpx-=self.my_elec.Px()
                    self.my_METpy-=self.my_elec.Py()
                    self.my_MET.SetPxPyPzE(self.my_METpx,self.my_METpy,0,sqrt(self.my_METpx*self.my_METpx+self.my_METpy*self.my_METpy))
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

                elif sys =='eresphidown':
                    self.my_METpx=self.my_MET.Px()+self.my_elec.Px()
                    self.my_METpy=self.my_MET.Py()+self.my_elec.Py()
                    self.my_elec.SetPtEtaPhiM(row.ePt_ElectronResPhiDown,row.eEta,row.ePhi,row.eMass)
                    self.my_METpx-=self.my_elec.Px()
                    self.my_METpy-=self.my_elec.Py()
                    self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                    self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                    self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                    self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
                    self.shifted_type1_pfMetPhi=self.my_MET.Phi()
                    self.shifted_type1_pfMetEt=self.my_MET.Pt()

 
            #mu preselection
                if not selections.muSelection(row,self.my_muon, 'm'): continue
                cut_flow_trk.Fill('musel')
                if not selections.lepton_id_iso(row, 'm', 'MuIDTight_idiso0p25',dataperiod=self.data_period): continue
                cut_flow_trk.Fill('mulooseiso')


            #E Preselection
                if not selections.eSelection(row,self.my_elec,'e'): continue
                cut_flow_trk.Fill('esel')

                if not selections.lepton_id_iso(row, 'e', 'eid15Loose_etauiso1',eIDwp='WP80'): continue
                cut_flow_trk.Fill('elooseiso')


           #take care of ecal gap
                if abs(self.my_elec.Eta()) > 1.4442 and abs(self.my_elec.Eta()) < 1.566 : continue             
            
                if deltaR(self.my_elec.Phi(),self.my_muon.Phi(),self.my_elec.Eta(),self.my_muon.Eta())<0.3:continue
                cut_flow_trk.Fill('DR_e_mu')


            ## now divide by e-mu isolation regions, looseloose,loosetight,tightloose,tighttight
                isMuonTight=False
                if selections.lepton_id_iso(row, 'm', 'MuIDTight_mutauiso0p15',dataperiod=self.data_period):
                    cut_flow_trk.Fill('muiso')
                    isMuonTight=True

                isElecTight=False
                if selections.lepton_id_iso(row, 'e', 'eid15Loose_etauiso0p1',eIDwp='WP80'): 
                    cut_flow_trk.Fill('eiso')
                    isElecTight=True
 

                if not isMuonTight and not isElecTight: #double fakes, should be tiny
                    region="eLoosemLoose"
                elif not isMuonTight and  isElecTight:   # mu fakes, should be small
                    region="eTightmLoose"
                elif  isMuonTight and not isElecTight: #e fakes, most fakes should come from here
                    region="eLoosemTight"
                elif isMuonTight and isElecTight: #signal region
                    region="signal"
            
                if region!="signal":continue    
                
                jn = self.shifted_jetVeto30
                if jn >= 2:
                    category=2
#                elif jn==2:
 #                   category=2 if self.shifted_vbfMass<550 else 3
                else:
                    category=jn
                
                if sys=='nosys':    
#                    if category!=4:               
                    self.fill_histos(row,sign,None,True,region,btagweight,'presel')
                    folder = sign+'/'+str(int(category))
                    self.fill_histos(row,sign,folder,False,region,btagweight,'presel',qcdshaperegion)

            
                if self.my_muon.Pt() < 65: continue 
                if self.my_elec.Pt() < 10: continue
                if deltaPhi(self.my_elec.Phi(),self.my_muon.Phi()) < 2.2 : continue
                if abs(self.shifted_eDPhiToPfMet) > 0.7 : continue
                cut_flow_trk.Fill('jet0sel')

                folder = sign+'/'+str(int(category))+'/selected/'+sys
                self.fill_histos(row,sign,folder,False,region,btagweight,sys,qcdshaperegion,self.pileup)
            
            self.my_muon=ROOT.TLorentzVector()
            self.my_muon.SetPtEtaPhiM(row.mPt,row.mEta,row.mPhi,row.mMass)
                
            self.my_elec=ROOT.TLorentzVector()
            self.my_elec.SetPtEtaPhiM(row.ePt,row.eEta,row.ePhi,row.eMass)
                
            self.my_MET=ROOT.TLorentzVector()
            self.my_MET.SetPtEtaPhiM(row.type1_pfMetEt,0,row.type1_pfMetPhi,0)

            self.shifted_jetVeto30=row.jetVeto30
            self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
            self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
            self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
            self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
            self.shifted_type1_pfMetPhi=self.my_MET.Phi()
            self.shifted_type1_pfMetEt=self.my_MET.Pt()
            self.shifted_vbfMass=row.vbfMass
            self.shifted_vbfDeta=row.vbfDeta


            self.pileup='nominal'

           # preselection
            if not selections.muSelection(row,self.my_muon, 'm'): continue
            cut_flow_trk.Fill('musel')
            if not selections.lepton_id_iso(row, 'm', 'MuIDTight_idiso0p25',dataperiod=self.data_period): continue
            cut_flow_trk.Fill('mulooseiso')


           #Preselection
            if not selections.eSelection(row,self.my_elec,'e'): continue
            cut_flow_trk.Fill('esel')

            if not selections.lepton_id_iso(row, 'e', 'eid15Loose_etauiso1',eIDwp='WP80'): continue
            cut_flow_trk.Fill('elooseiso')

           




           #take care of ecal gap
            if abs(self.my_elec.Eta()) > 1.4442 and abs(self.my_elec.Eta()) < 1.566 : continue             
           
            if deltaR(self.my_elec.Phi(),self.my_muon.Phi(),self.my_elec.Eta(),self.my_muon.Eta())<0.3:continue
            cut_flow_trk.Fill('DR_e_mu')


           #take now divide by e-mu isolation regions, looseloose,loosetight,tightloose,tighttight
            isMuonTight=False
            if selections.lepton_id_iso(row, 'm', 'MuIDTight_mutauiso0p15',dataperiod=self.data_period):
                cut_flow_trk.Fill('muiso')
                isMuonTight=True

            isElecTight=False
            if selections.lepton_id_iso(row, 'e', 'eid15Loose_etauiso0p1',eIDwp='WP80'): 
                cut_flow_trk.Fill('eiso')
                isElecTight=True
                
                
            if not isMuonTight and not isElecTight: #double fakes, should be tiny
                region="eLoosemLoose"
            elif not isMuonTight and  isElecTight:   # mu fakes, should be small
                region="eTightmLoose"
            elif  isMuonTight and not isElecTight: #e fakes, most fakes should come from here
                region="eLoosemTight"
            elif isMuonTight and isElecTight: #signal region
                region="signal"
                
            if region!="signal":continue    

            for jetsys in self.jetsysdir:
                self.shifted_jetVeto30=getattr(row, jetsys.replace('jes','jetVeto30'))
                jn = self.shifted_jetVeto30
                self.shifted_vbfMass=getattr(row, jetsys.replace('jes','vbfMass'))

                if jn >= 2:
                    category=2
#                elif jn==2:
 #                   category=2 if self.shifted_vbfMass<550 else 3
                else:
                    category=jn

                self.shifted_type1_pfMetEt=getattr(row, jetsys.replace('jes','type1_pfMet_shiftedPt'))
                self.shifted_type1_pfMetPhi=getattr(row, jetsys.replace('jes','type1_pfMet_shiftedPhi'))

                self.my_MET.SetPtEtaPhiM(self.shifted_type1_pfMetEt,0,self.shifted_type1_pfMetPhi,0)

                self.shifted_mDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_muon.Phi())
                self.shifted_eDPhiToPfMet=deltaPhi(self.my_MET.Phi(),self.my_elec.Phi())
                self.shifted_mMtToPfMet=transMass(self.my_muon,self.my_MET)
                self.shifted_eMtToPfMet=transMass(self.my_elec,self.my_MET)
            
                if self.my_muon.Pt() < 65: continue 
                if self.my_elec.Pt() < 10: continue
                if deltaPhi(self.my_elec.Phi(),self.my_muon.Phi()) < 2.2 : continue
                if abs(self.shifted_eDPhiToPfMet) > 0.7 : continue
                cut_flow_trk.Fill('jet0sel')

                folder = sign+'/'+str(int(category))+'/selected/'+jetsys
                self.fill_histos(row,sign,folder,False,region,btagweight,jetsys,qcdshaperegion,self.pileup)

        cut_flow_trk.flush()        
    def finish(self):
        self.write_histos()


