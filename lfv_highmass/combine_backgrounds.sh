#mv GluGluHToWWTo2L2Nu_M125_13TeV_powheg_pythia8_v6-v1.root ggH_hww.root
#mv VBFHToWWTo2L2Nu_M125_13TeV_powheg_pythia8_v6-v1.root qqH_hww.root

#mv GluGluHToTauTau_M125_13TeV*.root  ggH_htt.root             

#mv VBFHToTauTau_M125_13TeV_powheg_pythia8_v6-v1.root qqH_htt.root

hadd -f  ggH_htt.root WminusHToTauTau_M125_13TeV_powheg_pythia8_v6-v1.root WplusHToTauTau_M125_13TeV_powheg_pythia8_v6-v1.root ZHToTauTau_M125_13TeV_powheg_pythia8_v6-v1.root GluGluHToWWTo2L2Nu_M125_13TeV_powheg_pythia8_v6-v1.root  GluGluHToTauTau_M125_13TeV*.root #VBFHToTauTau_M125_13TeV_powheg_pythia8_v6-v1.root  #ttHJetToTT_M125_13TeV_amcatnloFXFX_madspin_pythia8_v6_ext4-v1.root




mv TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_v6-v1.root TT.root

#hadd -f LFV125.root GluGlu_LFV_HToMuTau_M125_13TeV*.root VBF_LFV_HToMuTau_M125_13TeV*.root
#hadd -f LFV120.root GluGlu_LFV_HToMuTau_M120_13TeV*.root VBF_LFV_HToMuTau_M120_13TeV*.root
#hadd -f LFV150.root GluGlu_LFV_HToMuTau_M150_13TeV*.root VBF_LFV_HToMuTau_M150_13TeV*.root
#hadd -f LFV130.root GluGlu_LFV_HToMuTau_M130_13TeV*.root VBF_LFV_HToMuTau_M130_13TeV*.root
mv GluGlu_LFV_HToMuTau_M200_13TeV*.root LFV200.root 
mv GluGlu_LFV_HToMuTau_M300_13TeV*.root LFV300.root 
mv GluGlu_LFV_HToMuTau_M450_13TeV*.root LFV450.root 
mv GluGlu_LFV_HToMuTau_M600_13TeV*.root LFV600.root 
mv GluGlu_LFV_HToMuTau_M750_13TeV*.root LFV750.root 
mv GluGlu_LFV_HToMuTau_M900_13TeV*.root LFV900.root 

mv QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8_v6-v1.root QCD_mc.root


#mv GluGlu_LFV_HToMuTau_M125_13TeV*.root LFVGG125.root
#mv VBF_LFV_HToMuTau_M125_13TeV*.root LFVVBF125.root



hadd -f Diboson.root VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8*.root WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8*.root WZJToLLLNu_TuneCUETP8M1_13TeV-amcnlo-pythia8_v6-v1*.root WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_v6-v3.root  WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8_v6-v1.root WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_v6-v1.root ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_v6-v1.root ZZTo4L_13TeV-amcatnloFXFX-pythia8_v6_ext1-v1.root

hadd -f Zothers.root DYJetsToLL_M-50_TuneCUETP8M1_13TeV*.root DY1JetsToLL_M-50_TuneCUETP8M1_13TeV*.root DY2JetsToLL_M-50_TuneCUETP8M1_13TeV*.root DY3JetsToLL_M-50_TuneCUETP8M1_13TeV*.root DY4JetsToLL_M-50_TuneCUETP8M1_13TeV*.root DY*M-10to50*root

hadd -f ZTauTau.root ZTauTauJets_M-50_TuneCUETP8M1_13TeV*.root ZTauTau1Jets_M-50_TuneCUETP8M1_13TeV*.root ZTauTau2Jets_M-50_TuneCUETP8M1_13TeV*.root ZTauTau3Jets_M-50_TuneCUETP8M1_13TeV*.root ZTauTau4Jets_M-50_TuneCUETP8M1_13TeV*.root 


hadd -f W.root WJetsToLNu_TuneCUETP8M1_13TeV*.root W1JetsToLNu_TuneCUETP8M1_13TeV*.root W2JetsToLNu_TuneCUETP8M1_13TeV*.root W3JetsToLNu_TuneCUETP8M1_13TeV*.root W4JetsToLNu_TuneCUETP8M1_13TeV*.root WGstarToLNuEE_012Jets_13TeV-*.root WGToLNuG_TuneCUETP8M1_13TeV-*.root  WGstarToLNuMuMu_012Jets_*.root

hadd -f  data_obs.root   data_SingleMuon_Run2016B*.root  data_SingleMuon_Run2016C*.root  data_SingleMuon_Run2016D*.root  data_SingleMuon_Run2016E*.root data_SingleMuon_Run2016F*.root data_SingleMuon_Run2016G*.root data_SingleMuon_Run2016H*.root

hadd -f T.root ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_*.root ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8*.root ST_t-channel*root


#rm WW_TuneCUETP8M1_13TeV*.root
#rm WZ_TuneCUETP8M1_13TeV*.root
#rm ZZ_TuneCUETP8M1_13TeV*.root
rm *HToTauTau*
rm ttHJetToTT_M125_13TeV_amcatnloFXFX_madspin_pythia8_v6_ext4-v1.root
rm *HToWW*
rm WG*mad*
rm WG*amcat*
rm ST*
rm DY*Jets*
rm W*Jets*
rm data_SingleMuon_*
rm ZTauTau*Jets*
rm *amc*
rm *ETau*
rm *evtgen*
rm *HToMuTau*
rm GluGlu*
rm VBF*
rm QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8_v6-v1.root