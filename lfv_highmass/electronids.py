#This module provides additional electron ID's starting from MVA's raw values
from FinalStateAnalysis.PlotTools.decorators import memo
@memo
def getVar(name, var):
    return name+var

def h2etau_looseId(row, name):
    return bool(getattr(row, getVar(name, 'CBID_LOOSE')))
def h2etau_tightId(row, name):
    return bool(getattr(row, getVar(name, 'CBID_TIGHT')))

def zh_loose_2012eid(row, name):
    value    = getattr(row, getVar(name, 'MVANonTrig'))
    pt       = getattr(row, getVar(name, 'Pt'))
    fabseta  = getattr(row, getVar(name, 'AbsEta'))
    if pt > 10. and fabseta < 0.8:
        return (value > 0.5)
    elif pt > 10. and fabseta >=0.8 and fabseta < 1.479:
        return (value > 0.12)
    elif pt > 10. and fabseta >= 1.479:
        return (value > 0.6)
    return False

def h2tau_2012_LooseId(row, name):
     return bool( getattr(row, getVar(name, 'MVAIDH2TauWP')))


def h2tau_2012_tightId(row, name):
    mva_output = getattr(row, getVar(name, 'MVANonTrig'))
    pT         = getattr(row, getVar(name, 'Pt'))
    abseta     = getattr(row, getVar(name, 'AbsEta'))
    if pT > 20  and abseta < 0.8:
        return ( mva_output > 0.925 )
    elif pT > 20  and 0.8 < abseta < 1.479:
        return ( mva_output > 0.975 )
    elif pT > 20  and abseta > 1.479:
        return ( mva_output > 0.985 )
    return False
    

#LEPTON ID-ISO
def summer_2013_eid(row, name):
    mva_output = getattr(row, getVar(name, 'MVANonTrig')) #was eMVATrigNoIP
    pT    = getattr(row, getVar(name, 'Pt'))
    abseta= getattr(row, getVar(name, 'AbsEta'))
    if pT < 20    and abseta < 0.8:
        return ( mva_output > 0.925 )
    elif pT < 20  and 0.8 < abseta < 1.479:
        return ( mva_output > 0.915 )
    elif pT < 20  and abseta > 1.479:
        return ( mva_output > 0.965 )
    elif pT > 20  and abseta < 0.8:
        return ( mva_output > 0.905 )
    elif pT > 20  and 0.8 < abseta < 1.479:
        return ( mva_output > 0.955 )
    elif pT > 20  and abseta > 1.479:
        return ( mva_output > 0.975 )
    return False

def summer_2013_eid_tight(row, name):
    mva_output = getattr(row, getVar(name, 'MVANonTrig'))
    pT    = getattr(row, getVar(name, 'Pt'))
    abseta= getattr(row, getVar(name, 'AbsEta'))
    if pT > 20 and abseta < 0.8:
        return ( mva_output > 0.925)
    elif pT > 20 and 0.8 < abseta < 1.479:
        return ( mva_output > 0.975 )
    elif pT > 20 and abseta > 1.479:
        return ( mva_output > 0.985 )
    return False
def summer_2015_eid(row, name,wp):
    if wp=='WP80':
        mva_output = getattr(row, getVar(name, 'MVANonTrigWP80')) #was eMVATrigNoIP
    if wp=='WP90':
        mva_output = getattr(row, getVar(name, 'MVANonTrigWP90')) #was eMVATrigNoIP
    if wp=='gen':
        mva_output = getattr(row, getVar(name, 'MVANonTrigID')) #was eMVATrigNoIP
    if mva_output:
        return True
    return False
def summer_2015_eid_tight(row, name):
    mva_output = getattr(row, getVar(name, 'MVANonTrigID'))
    pT    = getattr(row, getVar(name, 'Pt'))
    abseta= getattr(row, getVar(name, 'AbsEta'))
    if pT > 20 and abseta < 0.8:
        return ( mva_output > 0.925)
    elif pT > 20 and 0.8 < abseta < 1.479:
        return ( mva_output > 0.975 )
    elif pT > 20 and abseta > 1.479:
        return ( mva_output > 0.985 )
    return False

#add electron id from AN 2012_463
def hWW_eid_tight(row, name):
    mva_output = getattr(row, getVar(name,'MVATrig')) #check if it is correct
    pT    = getattr(row, getVar(name, 'Pt'))
    abseta= getattr(row, getVar(name, 'AbsEta'))
    if pT>20:
        if abseta <0.8:
            if mva_output >= 0.914 : return True
        if abseta <1.479 and abseta > 0.8 :
            if mva_output >=0.964 : return True
        if abseta <2.5 and abseta > 1.479:
            if mva_output >=0.899 : return True
        
    return False

def hWW_eid_loose(row, name):
    mva_output = getattr(row, getVar(name,'MVATrig')) #check if correct
    pT    = getattr(row, getVar(name, 'Pt'))
    abseta= getattr(row, getVar(name, 'AbsEta'))
    if pT>20:
        if abseta <0.8:
            if mva_output >= 0.877 : return True
        if abseta <1.479 and abseta > 0.8 :
            if mva_output >=0.811 : return True
        if abseta <2.5 and abseta > 1.479:
            if mva_output >=0.707 : return True
        
    return False

    
            
#ID MVA cut value (tight lepton) 0.913 0.964 0.899
#Isolation cut value (tight lepton) 0.105 0.178 0.150
#ID MVA cut value (loose lepton) 0.877 0.811 0.707
#Isolation cut value (loose lepton) 0.426 0.481 0.390

electronIds = {
    'eidCBLoose' : h2etau_looseId,
    'eidCBTight' : h2etau_tightId,
    'eid12Loose' : zh_loose_2012eid,
    'eid12Medium': h2tau_2012_LooseId,
    'eid12Tight' : h2tau_2012_tightId,
    'eid14Loose' : hWW_eid_loose,
    'eid14Tight' : hWW_eid_tight,
    'eid13Loose' : summer_2013_eid,
    'eid13Tight' : summer_2013_eid_tight,
    'eid15Loose' : summer_2015_eid,
    'eid15Tight' : summer_2015_eid_tight,
}
