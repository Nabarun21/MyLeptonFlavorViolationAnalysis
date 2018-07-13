#!/usr/bin/env python
import ROOT
import re
from array import array
from collections import OrderedDict
import varCfgPlotter
import argparse
import os

import ROOT as rt
import CMS_lumi, tdrstyle
import array

#set the tdr style
tdrstyle.setTDRStyle()

parser = argparse.ArgumentParser(
    "Create pre/post-fit plots for LFV H analysis")
parser.add_argument(
    "--isLog",
    type=int,
    action="store",
    dest="isLog",
    default=0,
    help="Plot Log Y? (Integers 0, false, 1 true)")
parser.add_argument(
    "--is_TT_DD",
    type=int,
    action="store",
    dest="is_TT_DD",
    default=0,
    help="if TTbar is data driven")
parser.add_argument(
    "--lumi",
    type=int,
    action="store",
    dest="Lumi",
    default=35847,
    help="Which channel to run over? (et, mt, em, me)")
parser.add_argument(
    "--analyzer",
    type=str,
    action="store",
    dest="analyzer",
    default="highmass",
    help="name of subfolder in plots directory to save plots")
parser.add_argument(
    "--channel",
    action="store",
    dest="channel",
    default="et",
    help="Which channel to run over? (et, mt, em, me)")
parser.add_argument(
    "--suffix",
    action="store",
    dest="suffix",
    default="presel",
    help="slection region")
parser.add_argument(
    "--region",
    type=str,
    action="store",
    dest="region",
    default="os",
    help="region of space: oppositesign-os,samesign-ss,anti-isolated os/ss etc")
parser.add_argument(
    "--var",
    type=str,
    action="store",
    dest="variable",
    default="colmass",
    help="Which variable")
parser.add_argument(
    "--signals",
    type=str,
    action="store",
    dest="signals",
    default="200,300,450,600,750,900",
    help="List of signal mass points to be plotted")
parser.add_argument(
    "--higgsSF",
    type=int,
    action="store",
    dest="higgsSF",
    default=5,
    help="Provide the Scale Factor for the SM-Higgs signals.  5x is default for linear")
parser.add_argument(
    "--higgsSFSM",
    type=int,
    action="store",
    dest="higgsSFSM",
    default=1,
    help="Provide the Scale Factor for the SM-Higgs signals.  10x is default")
parser.add_argument(
    "--inputFile",
    action="store",
    dest="inputFile",
    help="Provide the relative path to the target input file")
parser.add_argument(
    "--blind",
    type=int,
    action="store",
    dest="blind",
    default=1,
    help="Do you want to force blinding?")
parser.add_argument(
    "--numCategories",
    type=int,
    action="store",
    dest="numCategories",
    default=3,
    help="How many categories?")
args = parser.parse_args()



varnames={}
varnames['ePt']='e p_{T} [GeV]'
varnames['mPt']='#mu p_{T} [GeV]'
varnames['colmass']='M_{col} [GeV]'
varnames['vismass']='Visible Mass [GeV]'
varnames['mtMuMet']='M_{T}[#mu, MET] [GeV]'
varnames['mtEMet']='M_{T}[e, MET] [GeV]'
varnames['dphiEMet']='#Delta#phi[e, MET] '
varnames['dphiMuMet']='#Delta#phi[#mu, MET] '
varnames['BDT']='BDT Discriminator'
varnames['dphiemu']='#Delta#phi [e, #mu]'
varnames['met']='MET [GeV]'
varnames['meta']='#mu #eta'
varnames['eeta']='e #eta'

 
Lumi_uncert=0.026
e_eff_uncert=0.02
mu_eff_uncert=0.02
squared_sum_others=Lumi_uncert*Lumi_uncert+e_eff_uncert*e_eff_uncert+mu_eff_uncert*mu_eff_uncert

Lumi=args.Lumi
analyzer=args.analyzer
variable=args.variable
channel = args.channel
higgsSF = args.higgsSF if "CR" not in args.analyzer and args.region!='ss' else 1
isLog = args.isLog
suffix = args.suffix
categories = varCfgPlotter.getCategories( channel, suffix ,args.numCategories)

forceBlinding=args.blind
if suffix=='presel':
    selection_region='preselection'
else:
    selection_region='selection'

fileName = "preprocessed_inputs/"+args.analyzer+str(args.Lumi)+"/"+selection_region+"/"+args.region+"/"+args.inputFile

if fileName == None :
    fileName = varCfgPlotter.getFile( channel )
assert (fileName != None), "Please provide a file name"

print "\nPlotting for:"
print " -- Channel:",channel
print " -- Plot", "Log" if isLog else "Linear"
print " -- Plotting for categories:"

for cat in categories :
    print "     -- ",cat
print " -- Using Higgs Scale Factor:",higgsSF
print " -- Target file:",fileName,"\n"



file = ROOT.TFile( fileName, "r" )
#print file

# Category map for the LaTeX naming of histograms
catMap = {
    "em" : "e#tau_{#mu}",
    "et" : "e#tau_{h}",
    "mt" : "#mu#tau_{h}",
    "me" : "#mu#tau_{e}",
}



def add_lumi():
    lowX=0.67
    lowY=0.83
    lumi  = ROOT.TPaveText(lowX,lowY, lowX+0.30, lowY+0.2, "NDC")
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.SetTextSize(0.06)
    lumi.SetTextFont (   42 )
    lumi.AddText(str(round(float(Lumi)/1000,1)) +"fb^{-1} (13 TeV)")
    return lumi

#   TLatex *   tex = new TLatex(0.96,0.936,"20.1 fb^{-1} (13 TeV)");
#tex->SetNDC();
#   tex->SetTextAlign(31);
#   tex->SetTextFont(42);
#   tex->SetTextSize(0.048);
#   tex->SetLineWidth(2);
#   tex->Draw();



def add_CMS():
    lowX=0.17
    lowY=0.705
    lumi  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.15, lowY+0.16, "NDC")
    lumi.SetTextFont(61)
    lumi.SetTextSize(0.08)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("CMS")
    return lumi

def add_Preliminary():
    lowX=0.17
    lowY=0.645
    lumi  = ROOT.TPaveText(lowX, lowY+0.05, lowX+0.15, lowY+0.15, "NDC")
    lumi.SetTextFont(52)
    lumi.SetTextSize(0.08*0.8*0.7)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("Preliminary")
    return lumi

def make_legend(x1=0.42,y1=0.5,x2=0.92,y2=0.85):
	if 'dphi' in variable:# and 'Met' in variable:
            x1=x1-0.03
            x2=x2-0.03
            y1=0.56
           #output = ROOT.TLegend(0.65, 0.3, 0.92, 0.85, "", "brNDC")
        output = ROOT.TLegend(x1, y1,x2,y2, "", "brNDC")
#           output.SetNColumns(2)
        output.SetNColumns(1)
        #output = ROOT.TLegend(0.2, 0.1, 0.47, 0.65, "", "brNDC")
        output.SetLineWidth(0)
        output.SetLineStyle(0)
        output.SetFillStyle(0)
        #output.SetFillColor(0)
        output.SetBorderSize(0)
        output.SetTextFont(62)
        return output

# Can use to return all hists in a dir
def get_Keys_Of_Class( file_, dir_, class_ ) :
    keys = []
    d = file_.Get( dir_ )
    allKeys = d.GetListOfKeys()

    #print "keys of class"
    for k in allKeys :
        if k.GetClassName() == class_ :
            if( "LFV" in k.GetName() ) :
		continue 
	 #   print k.GetName()	
            keys.append( k )

    dir2=dir_.replace("postfit","prefit")
#    print dir2
    d2 = file_.Get(dir2)
    signalKeys = d2.GetListOfKeys()
    for k in signalKeys :
        if k.GetClassName() == class_ :
            if( "LFV" not in k.GetName() ) :
                continue
#            print k.GetName()		
            keys.append( k )

    return keys

ROOT.gStyle.SetFrameLineWidth(3)
ROOT.gStyle.SetLineWidth(3)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
ROOT.TGaxis.SetMaxDigits(4)

c=ROOT.TCanvas("canvas","",0,0,800,800)
c.cd()


adapt=ROOT.gROOT.GetColor(12)
new_idx=ROOT.gROOT.GetListOfColors().GetSize() + 1
trans=ROOT.TColor(new_idx, adapt.GetRed(), adapt.GetGreen(),adapt.GetBlue(), "",0.5)

infoMap = varCfgPlotter.getInfoMap( higgsSF, channel,"" )
print "infomap ",infoMap
bkgs = varCfgPlotter.getBackgrounds(channel,args.is_TT_DD,args.region)
print "bg  ",bkgs
signals = varCfgPlotter.getSignals(args.signals)
print "sig    ",signals
higgsSFSM=1
for cat in categories:
    print "Plotting for:",cat
    
    # Get list of the keys to hists in our category analyzertory
    histKeys = get_Keys_Of_Class( file, cat, "TH1F" )
 
    # Get nominal shapes for all processes
    initHists = {}
    for key in histKeys :
#	print key.GetName()
        if "_CMS_" in key.GetName() : continue
        # skip the higgs mass +/-
        if "120" in key.GetName() or "130" in key.GetName() : continue
        initHists[ key.GetName() ] = key.ReadObj()
    
    # Check for a few fundamental histos
    assert (initHists["data_obs"] != None), "Where's your data hist?!"
    #assert (initHists["ZTT"] != None), "Where's your ZTT hist?!"
    #for sig in signals :
    #    assert (initHists[sig] != None), "Where's your %s?!" % sig

    nBins = initHists["data_obs"].GetXaxis().GetNbins()
    binWidth = initHists["data_obs"].GetBinWidth(1)
#    print nBins,binWidth
    
    # Make the final hists, some initial shapes need to be merged
    hists = {}
    for name, val in infoMap.iteritems() :
 #       print name, val
        #hists[ name ] = ROOT.TH1F( name+cat, val[1], nBins, 0, nBins*binWidth )
	hists[ name ] = initHists["data_obs"].Clone()
	hists[ name ].Scale(0)
        #hists[ name ].Sumw2()
        for toAdd in val[0] :
#	    print toAdd
            if not toAdd in initHists :
                print toAdd," not in your file: %s, analyzertory, %s" % (file, cat)
                continue
            hists[ name ].Add( initHists[ toAdd ] )
    
        if name not in signals  :
            hists[ name ].SetFillColor(ROOT.TColor.GetColor( val[3] ) )
            hists[ name ].SetLineColor(1)
            if 'data' not in name:
                for k in range(1,hists[name].GetSize()-1):
                    hists[name].SetBinError(k,(squared_sum_others*hists[name].GetBinContent(k)*hists[name].GetBinContent(k)+val[4]*hists[name].GetBinContent(k)*val[4]*hists[name].GetBinContent(k)+hists[name].GetBinError(k)*hists[name].GetBinError(k))**0.5)

        
    # Set aesthetics
    hists["data_obs"].GetXaxis().SetTitle("")
    hists["data_obs"].GetXaxis().SetTitleSize(0)
    hists["data_obs"].GetXaxis().SetNdivisions(505)
    hists["data_obs"].GetYaxis().SetLabelFont(42)
    hists["data_obs"].GetYaxis().SetLabelOffset(0.01)
    hists["data_obs"].GetYaxis().SetLabelSize(0.06)
#    hists["data_obs"].GetYaxis().SetTitleSize(0.075)
    hists["data_obs"].GetYaxis().SetTitleSize(0.09)
#    hists["data_obs"].GetYaxis().SetTitleOffset(1.04)#0.96)
    hists["data_obs"].GetYaxis().SetTitleOffset(0.7)
    hists["data_obs"].SetTitle("")
    hists["data_obs"].GetYaxis().SetTitle("Events/bin")
    hists["data_obs"].SetMarkerStyle(20)
    hists["data_obs"].SetMarkerSize(1)
    hists["data_obs"].SetLineWidth(1)

#    print "data",hists["data_obs"].GetXaxis().GetXmax()
    for sig in signals :
#	print sig
        hists[ sig ].SetLineColor(infoMap[ sig ][3] )
        hists[sig].SetLineStyle(infoMap[sig][5])
        hists[ sig ].SetLineWidth(4)
        
        #hists[ sig ].SetLineStyle(2)
 #       print sig,hists[sig].GetXaxis().GetXmax()
    
    errorBand=hists["ZTT"].Clone()
    for bkg in bkgs :
	if bkg == "SMH" : 
            hists[ bkg ].Scale(higgsSFSM)
        
#        if bkg == "TT":
#            if suffix=='presel':
 #           hists[ bkg ].Scale(0.885591123589)            
           # else:
            #    hists[ bkg ].Scale(0.618959690883)            

        if bkg == "ZTT" : continue
        errorBand.Add(hists[bkg])
#	print bkg,hists[bkg].GetXaxis().GetXmax()
    
    # Build our stack
    stack=ROOT.THStack("stack","stack")
    for bkg in bkgs :
        stack.Add( hists[bkg] )
    
    errorBand.SetMarkerSize(0)
    errorBand.SetFillColor(new_idx)
    errorBand.SetFillStyle(3001)
    errorBand.SetLineWidth(1)
    
    pad1 = ROOT.TPad("pad1","pad1",0,0.35,1,1)
    pad1.Draw()
    pad1.cd()
    pad1.SetFillColor(0)
    pad1.SetBorderMode(0)
    pad1.SetBorderSize(10)
    pad1.SetTickx(1)
    pad1.SetTicky(1)
    pad1.SetLeftMargin(0.14)
    pad1.SetRightMargin(0.05)
    pad1.SetTopMargin(0.122)
    pad1.SetBottomMargin(0.026)
    pad1.SetFrameFillStyle(0)
    pad1.SetFrameLineStyle(0)
    pad1.SetFrameLineWidth(3)
    pad1.SetFrameBorderMode(0)
    pad1.SetFrameBorderSize(10)
    if isLog:
        pad1.SetLogy()
    
    hists["data_obs"].GetXaxis().SetLabelSize(0)
    hists["data_obs"].SetMaximum(1.7*max(stack.GetMaximum(),hists["data_obs"].GetMaximum()))
#    print stack.GetMaximum()
    hists["data_obs"].SetMinimum(0.0)
    if isLog:
        hists["data_obs"].SetMaximum(hists["data_obs"].GetMaximum()*1000)
        hists["data_obs"].SetMinimum(0.01)
    for k in range(1,hists["data_obs"].GetSize()-1):
        s=0.0
        b=0.0
        for bkg in bkgs :
            b += hists[bkg].GetBinContent(k)
        for sig in signals :
            s = hists[sig].GetBinContent(k)

	# commenting this because this should be done before
#        if (b<0):
#            b=0.000001
#        #if (10*s/((b+0.09*b*0.09*b)**0.5) > 0.5):

            if (forceBlinding>0 and s/(0.00000001+s+b) > 0.005):
                hists["data_obs"].SetBinContent(k,0)#100000000)
                hists["data_obs"].SetBinError(k,0)#100000000)


    if args.region!='ss':            
        start_blinding_at=160#gev
#   always blind discriminating mass histos after a certain value except when plotting CRs 
        if 'mass' in variable and 'CR' not in args.analyzer:
            start_bin=hists["data_obs"].FindFixBin(start_blinding_at)
            for bin in range(start_bin,hists["data_obs"].GetNbinsX()+1):
                hists["data_obs"].SetBinContent(bin,0)
                hists["data_obs"].SetBinError(bin,0)

    hists["data_obs"].Draw("ep")
    stack.Draw("histsame")
    errorBand.Draw("e2same")
    for sig in signals :
        if isLog:
            hists[ sig ].Scale(higgsSF)
        else:
            hists[ sig ].Scale(higgsSF)

        hists[ sig ].Draw("histsame")
    hists["data_obs"].Draw("esame")
 
    legend1=make_legend(x2=0.62)
    legend2=make_legend(x1=0.65)
    for name, val in infoMap.iteritems() :
        if name in bkgs:
            legend1.AddEntry(hists[name], val[1], val[2])
    legend1.AddEntry(errorBand,"Bkg. unc.","f")

    legend2.AddEntry(None,"LFV H#rightarrow#mu#tau_{e}","")
    legend2.AddEntry(None,"M_{H}   "+"{:.2f}#timesxs(BSM)".format(0.01*higgsSF),"")

    for name, val in infoMap.iteritems() :
        if name in signals:
            legend2.AddEntry(hists[name], val[1], val[2])



    legend1.Draw()
    legend2.Draw()
    
    l1=add_lumi()
    l1.Draw("same")
    l2=add_CMS()
    l2.Draw("same")
    l3=add_Preliminary()
    l3.Draw("same")
    
    pad1.RedrawAxis()
  
    categ  = ROOT.TPaveText(0.24, 0.92, 0.50, 0.97, "NDC")   
#    categ  = ROOT.TPaveText(0.17, 0.655, 0.45, 0.655+0.155, "NDC")
    categ.SetBorderSize(   0 )
    categ.SetFillStyle(    0 )
    categ.SetTextAlign(   12 )
    categ.SetTextSize ( 0.07 )
    categ.SetTextColor(    1 )
    categ.SetTextFont (   42 )

    if "mutaue" in cat and "01jet" in cat:
        categ.AddText(catMap[channel]+", 0_1 jet "+suffix)
    if "mutaue" in cat and "rest" in cat:
        categ.AddText(catMap[channel]+", 2+ jets "+suffix)
    if "mutaue" in cat and "_0jet" in cat:
        categ.AddText(catMap[channel]+", 0 jet "+suffix)
    if "mutaue" in cat and "_1jet" in cat:
        categ.AddText(catMap[channel]+", 1 jet "+suffix)
    if "mutaue" in cat and "2jet" in cat:
        categ.AddText(catMap[channel]+", 2+ jets "+suffix)
    if "lfv" in cat and "_4_" in cat:
        categ.AddText(catMap[channel]+", 2 jets VBF")
    if "_ch1" in cat:
        categ.AddText(catMap[channel]+", 0 jet")
    if "_ch2" in cat:
        categ.AddText(catMap[channel]+", 1 jet")
    if "_ch3" in cat:
        categ.AddText(catMap[channel]+", 2 jets gg")
    if "_ch4" in cat:
        categ.AddText(catMap[channel]+", 2 jets VBF")
    if "_21_" in cat:
        categ.AddText(catMap[channel]+", 2 jets gg")
    if "_22_" in cat:
        categ.AddText(catMap[channel]+", 2 jets VBF")
    if "HMuTau" in cat and "_1_" in cat:
        categ.AddText(catMap[channel]+", 0 jet")
    if "HMuTau" in cat and "_2_" in cat:
        categ.AddText(catMap[channel]+", 1 jet")
    if "HMuTau" in cat and "_3_" in cat:
        categ.AddText(catMap[channel]+", 2 jets gg")
    if "HMuTau" in cat and "_4_" in cat:
        categ.AddText(catMap[channel]+", 2 jets VBF")
    categ.Draw("same")
    
    c.cd()
    pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.35);
    pad2.SetTopMargin(0.05);
    pad2.SetBottomMargin(0.35);
    pad2.SetLeftMargin(0.14);
    pad2.SetRightMargin(0.05);
    pad2.SetTickx(1)
    pad2.SetTicky(1)
    pad2.SetFrameLineWidth(3)
    #pad2.SetGridx()
    pad2.SetGridy()
    pad2.Draw()
    pad2.cd()
    h1=hists["data_obs"].Clone()
    h1.SetMaximum(1.75)#FIXME(1.5)
    h1.SetMinimum(0.25)#FIXME(0.5)
    h1.SetMarkerStyle(20)
    h3=errorBand.Clone()
    hwoE=errorBand.Clone()
    for iii in range (1,hwoE.GetSize()-2):
      hwoE.SetBinError(iii,0)
    h3.Sumw2()
    h1.Sumw2()
    h1.SetStats(0)
    h1.Divide(hwoE)
    h3.Divide(hwoE)
    #h1.GetXaxis().SetTitle("Collinear mass (GeV)")
    #h1.GetXaxis().SetTitle("BDT output")
    h1.GetXaxis().SetTitle(varnames[variable])
    h1.GetXaxis().SetLabelSize(0.08)
    h1.GetYaxis().SetLabelSize(0.08)
    h1.GetYaxis().SetTitle("Obs./Exp.")
    h1.GetXaxis().SetNdivisions(505)
    h1.GetYaxis().SetNdivisions(5)
    
    h1.GetXaxis().SetTitleSize(0.16)
    h1.GetYaxis().SetTitleSize(0.15)
    h1.GetYaxis().SetTitleOffset(0.40)
    h1.GetXaxis().SetTitleOffset(1.04)
    h1.GetXaxis().SetLabelSize(0.11)
    h1.GetYaxis().SetLabelSize(0.11)
    h1.GetXaxis().SetTitleFont(42)
    h1.GetYaxis().SetTitleFont(42)
    
    h1.Draw("e0p")
    h3.Draw("e2same")
    
    c.cd()
    pad1.Draw()
    
    ROOT.gPad.RedrawAxis()
    
    TTbar_DD=""
    if args.is_TT_DD==1:
        TTbar_DD="_data_drivenTT"

    c.Modified()
    if not os.path.exists( 'plots' ) : os.makedirs( 'plots' )
    if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD):os.makedirs("plots/"+analyzer+str(args.Lumi)+TTbar_DD)
    
    if args.suffix=='presel':
        if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+args.region):os.makedirs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+args.region)

        if isLog:
            c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+args.region+"/log_"+cat+"_"+variable+".pdf")
    #       c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+"log_"+cat+"_"+variable+".pdf")
        else:
            c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+args.region+"/"+cat+"_"+variable+".pdf")
    #       c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/preselection/"+cat+"_"+variable+".pdf")
 
    else:
        if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+args.region):os.makedirs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+args.region)

        if isLog:
            c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+args.region+"/log_"+cat+"_"+variable+".pdf")
    #       c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+"log_"+cat+"_"+variable+".pdf")
        else:
            c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+args.region+"/"+cat+"_"+variable+".pdf")
    #       c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/selection/"+cat+"_"+variable+".pdf")
        
     
    for bkg in bkgs:
	print bkg," : ",hists[bkg].Integral()    

    for sig in signals:
        print sig," : ",hists[sig].Integral()
        
    
