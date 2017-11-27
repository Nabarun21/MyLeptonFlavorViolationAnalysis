"Helper module for cut optimization" 

import os

_0jets = {
   'mPt'  : list(range(40,80,5))+[80,90,100]+list(range(125,500,25)),
   'ePt'  : range(10,60,5),
   'dphiEMu' : [0.1*i for i in range(14,32,2)],
   'eDPhiToPfMet':[0.1*i for i in range(1,16,2)],
   'mDPhiToPfMet':[0.1*i for i in range(10,32,2)],
   'mMtToPfMet':range(30,700,30),
   'eMtToPfMet':range(250,100,-20),
}



_0jet_region_templates = ['mPt%i', 'ePt%i', 'dphi%.2f', 'eDPhiToPfMet%.2f','mDPhiToPfMet%.2f','mMtToPfMet%i','eMtToPfMet%i'] 

def _get_0jet_regions(mPt=None, ePt=None, dphiEMu=None, eDPhiToPfMet=None ,mDPhiToPfMet=None,mMtToPfMet=None,eMtToPfMet=None):

   pass_mPt        = [i for i in _0jets['mPt'       ] if mPt        > i] 
   pass_ePt        = [i for i in _0jets['ePt'       ] if ePt        > i] 
   pass_dphi       = [i for i in _0jets['dphiEMu'      ] if dphiEMu       > i] 
   pass_eDPhiToPfMet = [i for i in _0jets['eDPhiToPfMet'] if eDPhiToPfMet < i]
   pass_mDPhiToPfMet = [i for i in _0jets['mDPhiToPfMet'] if mDPhiToPfMet > i]
   pass_mMtToPfMet = [i for i in _0jets['mMtToPfMet'] if mMtToPfMet > i]
   pass_eMtToPfMet = [i for i in _0jets['eMtToPfMet'] if eMtToPfMet < i]

   cuts = [pass_mPt, pass_ePt,pass_dphi,pass_eDPhiToPfMet,pass_mDPhiToPfMet,pass_mMtToPfMet,pass_eMtToPfMet]

   ret = []
   for cut_idx, opts in enumerate(cuts):
      ret.extend([_0jet_region_templates[cut_idx] % i for i in opts])

   return ret



_1jets = {
   'mPt'  : list(range(40,80,5))+[80,90,100]+list(range(125,500,25)),
   'ePt'  : range(10,60,5),
   'dphiEMu' : [0.1*i for i in range(14,32,2)],
   'eDPhiToPfMet':[0.1*i for i in range(1,16,2)],
   'mDPhiToPfMet':[0.1*i for i in range(10,32,2)],
   'mMtToPfMet':range(30,700,30),
   'eMtToPfMet':range(250,100,-20),
}




_1jet_region_templates = ['mPt%i', 'ePt%i', 'dphi%.2f', 'eDPhiToPfMet%.2f','mDPhiToPfMet%.2f','mMtToPfMet%i','eMtToPfMet%i'] 

def _get_1jet_regions(mPt=None, ePt=None, dphiEMu=None, eDPhiToPfMet=None ,mDPhiToPfMet=None,mMtToPfMet=None,eMtToPfMet=None):

   pass_mPt        = [i for i in _1jets['mPt'       ] if mPt        > i] 
   pass_ePt        = [i for i in _1jets['ePt'       ] if ePt        > i] 
   pass_dphi       = [i for i in _1jets['dphiEMu'      ] if dphiEMu       > i] 
   pass_eDPhiToPfMet = [i for i in _1jets['eDPhiToPfMet'] if eDPhiToPfMet < i]
   pass_mDPhiToPfMet = [i for i in _1jets['mDPhiToPfMet'] if mDPhiToPfMet > i]
   pass_mMtToPfMet = [i for i in _0jets['mMtToPfMet'] if mMtToPfMet > i]
   pass_eMtToPfMet = [i for i in _0jets['eMtToPfMet'] if eMtToPfMet < i]


   cuts = [pass_mPt, pass_ePt,pass_dphi,pass_eDPhiToPfMet,pass_mDPhiToPfMet,pass_mMtToPfMet,pass_eMtToPfMet]

   ret = []
   for cut_idx, opts in enumerate(cuts):
      ret.extend([_1jet_region_templates[cut_idx] % i for i in opts])

   return ret

    

compute_regions_0jet = _get_0jet_regions 
compute_regions_1jet = _get_1jet_regions 





