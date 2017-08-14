### File to store all of the configurations for the
### LFV H prefit/prefit plotter
###
###
import ROOT
from collections import OrderedDict

# Provide the category names (folder names)
# where we should look for histograms
#def getCategories( channel="tt", prefix="" ) :
#    preCategories=["_0jet","_boosted","_VBF"] 
#    if channel == "em" or channel == "et" or channel == "mt": # FIXME vbf --> VBF when ready
#        preCategories=["_0jet","_boosted","_vbf"] 
#    categories=[prefix+channel+cat for cat in preCategories]
#    return categories

def getCategories( channel="et", prefix="" ) :
    preCategories=["_1_","_2_","_3_"]
    categories=["ch1_lfv_"+channel+cat+"_prefit" for cat in preCategories]
    if channel=="et":
        categories[0]="ch2_ch1_"+prefix
        categories[1]="ch2_ch2_"+prefix
        categories[2]="ch2_ch3_"+prefix
        categories[3]="ch2_ch4_"+prefix
    if channel=="em":
        categories[0]="ch1_ch1_"+prefix
        categories[1]="ch1_ch2_"+prefix
        categories[2]="ch1_ch3_"+prefix
        categories[3]="ch1_ch4_"+prefix
    if channel=="mt":
        categories[0]="mutau_HMuTau_mutauhad_1_2016_"+prefix  
        categories[1]="mutau_HMuTau_mutauhad_2_2016_"+prefix
        categories[2]="mutau_HMuTau_mutauhad_3_2016_"+prefix
        categories[3]="mutau_HMuTau_mutauhad_4_2016_"+prefix
    if channel=="me":
        categories[0]="mutaue_0jet_"+prefix
        categories[1]="mutaue_1jet_"+prefix
        categories[2]="mutaue_2jet_"+prefix
    return categories


# Provide standard mapping to our files
# this can be overridden with --inputFile
def getFile( channel ) :
    fileMap = {
        "et" : "etauh.root", 
        "mt" : "mutauh.root", 
        "em" : "etaumu.root", 
        "me" : "mutaue.root", 
    }
    return fileMap[ channel ]

def getInfoMap( higgsSF, channel, shift="" ) :
    if channel == "mt" : sub = ("h", "#mu") 
    if channel == "et" : sub = ("h", "e")
    if channel == "em" : sub = ("e", "#mu")
    if channel == "me" : sub = ("#mu", "e")
    
    infoMap = OrderedDict()
    # Name : Add these shapes [...], legend name, leg type, fill color,norm uncertainty on x-sec,line-style(only for signals)
    infoMap["data_obs"] = [["data_obs",],"Observed","elp",1]
    infoMap["ZTT"] = [["ZTauTau"+shift],"Z#rightarrow#tau#tau","f","#ffcc66",0.10]
    infoMap["ZJ"] = [["Zothers"+shift],"Z#rightarrowee/#mu#mu","f","#4496c8",0.10]
    infoMap["TT"] = [["TT"+shift,"T"+shift],"t#bar{t},t+jets","f","#9999cc",0.12]
    infoMap["Diboson"] = [["Diboson"+shift],"Diboson","f","#12cadd",0.05]
    if channel=="et" or channel=="mt":
       infoMap["QCD"] = [["Fakes",],"Reducible","f","#ffccff"]
    if channel == "me" or channel=="em":
       infoMap["QCD"] = [["QCD","W"+shift],"Reducible","f","#ffccff",0.30]
    if channel=="em" or channel=="et":
       infoMap["H125"] = [["LFVGG125"+shift,"LFVVBF125"+shift,],"H#rightarrowe#tau (B=%i%%)"%higgsSF,"l","#111bbb"]
    elif channel=="me" or channel=="mt":
       infoMap["LFV200"] = [["LFV200"],"LFV200","l",ROOT.kRed,0,1]
       infoMap["LFV300"] = [["LFV300"],"LFV300","l",ROOT.kBlack,0,1]
       infoMap["LFV450"] = [["LFV450"],"LFV450","l",ROOT.kBlue,0,1]
       infoMap["LFV600"] = [["LFV600"],"LFV600","l",ROOT.kRed,0,2]
       infoMap["LFV750"] = [["LFV750"],"LFV750","l",ROOT.kBlack,0,2]
       infoMap["LFV900"] = [["LFV900"],"LFV900","l",ROOT.kBlue,0,2]

    return infoMap


def getBackgrounds(channel) :
    if channel=="em" or channel=="me":    
       bkgs=["QCD", "Diboson", "TT", "ZTT", "ZJ"]
       return bkgs
    if channel=="et" or channel=="mt":
       bkgs=["QCD", "Diboson", "TT", "ZJ", "ZTT"]
       return bkgs

def getSignals() :
    signals=["LFV200","LFV300","LFV450","LFV600","LFV750","LFV900"]
    return signals

