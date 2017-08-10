from FinalStateAnalysis.PlotTools.decorators import memo
from FinalStateAnalysis.Utilities.struct import struct
from electronids import electronIds

@memo
def getVar(name, var):
    return name+var

@memo
def splitEid(label):
    return label.split('_')[-1], label.split('_')[0] 

#OBJECT SELECTION
def muSelection(row, my_muon,name):
    if my_muon.Pt() < 26:       return False
    if abs(my_muon.Eta()) > 2.4:  return False
    if not getattr( row, getVar(name,'PixHits')):   return False
  #  if getattr( row, getVar(name,'JetPFCISVBtag')) > 0.8: return False
    if abs(getattr( row, getVar(name,'PVDZ'))) > 0.2: return False
    return True

def eSelection(row, my_electron,name):
    if my_electron.Pt() < 10:           
        #print "1"
        return False #was 20
    if abs(my_electron.Eta()) > 2.4:      #as in H->tau_etau_h # was 2.3
        #print "2"
        return False #was 20
    if getattr( row, getVar(name,'MissingHits'))>1:       
        #print "3"
        return False #was 20
    if not getattr( row, getVar(name,'PassesConversionVeto')):     
        #print "4"
        return False #was 20
    if not getattr( row, getVar(name,'ChargeIdTight')): 
#    if not getattr( row, getVar(name,'ChargeIdLoose')): 
        #print "5"
        return False #was 20
#    if getattr( row, getVar(name,'JetPFCISVBtag')) > 0.8:  
        #print "6"
 #       return False #was 20
    ###if getattr( row, getVar(name,'JetBtag')) > 3.3:     
    if abs(getattr( row, getVar(name,'PVDZ'))) > 0.2:     
        #print "7"
        return False #was 20
    return True
    
def tauSelection(row, name):
    if getattr( row, getVar(name,'Pt')) < 30:          return False
    if getattr( row, getVar(name,'AbsEta')) > 2.3:     return False
    if abs(getattr( row, getVar(name,'PVDZ'))) > 0.2:    return False
    return True

def muTSelection(row, name):
#    if getattr( row, getVar(name,'Pt')) < 20:       return False
    if getattr(row, getVar(name, 'RelPFIsoDBDefault'))>0.15: return False 
    return True
#VETOS
def vetos(row):
    if row.muVetoPt5IsoIdVtx: return False
    if row.eVetoMVAIsoVtx:    return False
    ##if row.eVetoCicTightIso:   return False # change it to loose
    ##if row.tauVetoPt20:        return False
    if tauVetoPt20Loose3HitsNewDMVtx: return False
    return True

def lepton_id_iso(row, name, label,eIDwp='WP80',dataperiod=None): #label in the format eidtype_isotype
    'One function to rule them all'
    LEPTON_ID = False
    isolabel, eidlabel = splitEid(label) #memoizes to be faster!
#    print isolabel
    if name[0] == 'e':
        LEPTON_ID = electronIds[eidlabel](row, name,eIDwp)
    else:
#        LEPTON_ID = getattr(row, getVar(name, 'PFIDTight'))
        if dataperiod=="BCDEF":
            goodglob=(row.mIsGlobal) and (row.mNormalizedChi2 < 3) and (row.mChi2LocalPosition < 12) and (row.mTrkKink < 20)
            LEPTON_ID = row.mPFIDLoose and (row.mValidFraction> 0.49) and (row.mSegmentCompatibility > (0.303 if goodglob else  0.451)) #ichepmedium
        elif dataperiod=="GH":
            LEPTON_ID=row.mPFIDMedium
    if not LEPTON_ID:
        return False
    if name[0]=='e':
     #   RelPFIsoDB   = getattr(row, getVar(name, 'RelPFIsoDB'))
        RelPFIsoDB   = getattr(row, getVar(name, 'IsoDB03'))
    else:
        RelPFIsoDB   = getattr(row, getVar(name, 'RelPFIsoDBDefaultR04'))
    

    AbsEta       = getattr(row, getVar(name, 'AbsEta'))
    if isolabel == 'h2taucuts':
        return bool( RelPFIsoDB < 0.1 or (RelPFIsoDB < 0.15 and AbsEta < 1.479))
    if isolabel == 'h2taucuts020':
        return bool( RelPFIsoDB < 0.15 or (RelPFIsoDB < 0.20 and AbsEta < 1.479))
    if isolabel == 'idiso0p5':
        print "taking isolation"
        return bool( RelPFIsoDB < 0.5 ) 
    if isolabel == 'idiso0p25':
        return bool( RelPFIsoDB < 0.25 ) 
    if isolabel == 'etauiso1':
        return bool( RelPFIsoDB < 1.0 ) 
    if isolabel == 'etauiso1000':
        return bool( RelPFIsoDB < 1000.0 ) 
    if isolabel == 'etauiso0p12' or isolabel == 'mutauiso0p12': 
        return bool( RelPFIsoDB < 0.12 ) 
    if isolabel == 'etauiso0p1' or isolabel == 'mutauiso0p1': 
        return bool( RelPFIsoDB < 0.1 ) 
    if isolabel == 'etauiso0p5' or isolabel == 'mutauiso0p5': 
        return bool( RelPFIsoDB < 0.5 ) 
    if isolabel == 'etauiso0p15' or isolabel == 'mutauiso0p15': 
        return bool( RelPFIsoDB < 0.15 ) 


    ##put the new iso
    if isolabel == 'mvaLoose' :
        if AbsEta < 0.8:
            return bool( RelPFIsoDB < 0.426 ) 
        if AbsEta > 0.8 and AbsEta < 1.479 :
            return bool(RelPFIsoDB < 0.481)
        if AbsEta > 1.479 and AbsEta < 2.5:
            return bool(RelPFIsoDB < 0.390)
        return False
    if isolabel == 'mvaTight':
        if AbsEta < 0.8:
            return bool( RelPFIsoDB < 0.105 ) 
        if AbsEta > 0.8 and AbsEta < 1.479 :
            return bool(RelPFIsoDB < 0.178)
        if AbsEta > 1.479 and AbsEta < 2.5:
            return bool(RelPFIsoDB < 0.150)
        return False
        
        

def control_region_ee(row):
    '''Figure out what control region we are in. Shared among two codes, to avoid mismatching copied here'''
    if  row.e1_e2_SS and lepton_id_iso(row, 'e1', 'eid12Medium_h2taucuts') and row.e1MtToMET > 30: 
        return 'wjets'
    elif row.e1_e2_SS and row.e1RelPFIsoDB > 0.3 and row.type1_pfMetEt < 25: #and row.metSignificance < 3: #
        return 'qcd'
    elif lepton_id_iso(row,'e1', 'eid12Medium_h2taucuts') and lepton_id_iso(row,'e2', 'eid12Medium_h2taucuts') \
        and not any([ row.muVetoPt5IsoIdVtx,
                      row.tauVetoPt20Loose3HitsVtx,
                      row.eVetoMVAIsoVtx,
                      ]):
        return 'zee'
    else:
        return None


