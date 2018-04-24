#!/usr/bin/env python
import ROOT
import re
from array import array
from collections import OrderedDict
import argparse
import os

parser = argparse.ArgumentParser(
    "Create pre/post-fit plots for LFV H analysis")
parser.add_argument(
    "--isLog",
    action="store_true",
    help="Plot Log Y? ")
parser.add_argument(
    "--is_TT_DD",
    type=int,
    action="store",
    dest="is_TT_DD",
    default=0,
    help="is TTbar data driven")
parser.add_argument(
    "--channel",
    action="store",
    dest="channel",
    default="me",
    help="Which channel to run over? (et, mt, em, me)")
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
    default="ePt",
    help="Which channel to run over? (et, mt, em, me)")
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
    "--signals",
    type=str,
    action="store",
    dest="signals",
    default="200,300,450,600,750,900",
    help="name of subfolder in plots directory to save plots")
parser.add_argument(
    "--prefix",
    action="store",
    dest="prefix",
    default="",
    help="Provide prefix for TAnalyzertory holding histograms such as 'prefit_' or postfin_'.  Default is '' and will search in CHANNEL_0jet, CHANNEL_boosted, CHANNEL_VBF")
parser.add_argument(
    "--higgsSF",
    type=int,
    action="store",
    dest="higgsSF",
    default=5,
    help="Provide the Scale Factor for the SM-Higgs signals.  5x is default")
parser.add_argument(
    "--inputFile",
    action="store",
    dest="inputFile",
    help="Provide the relative path to the target input file")
args = parser.parse_args()

varnames={}
varnames['ePt']='e p_{T} [GeV]'
varnames['mPt']='#mu p_{T} [GeV]'
varnames['colmass']='M_{col} [GeV]'
varnames['vismass']='Visible Mass [GeV]'
varnames['mtMuMet']='M_{T}[#mu, MET] [GeV]'
varnames['mtEMet']='M_{T}[e, MET] [GeV]'
varnames['dphiEMet']='|#Delta#phi[e, MET]| '
varnames['dphiMuMet']='|#Delta#phi[#mu, MET]| '
varnames['BDT']='BDT Discriminator'
varnames['dphiemu']='|#Delta#phi [e, #mu]|'
varnames['met']='MET [GeV]'
varnames['meta']='#mu #eta'
varnames['eeta']='e #eta'

analyzer=args.analyzer
variable=args.variable
channel = args.channel
higgsSF = args.higgsSF
fileName = "preprocessed_inputs/"+args.analyzer+str(args.Lumi)+"/inclusive/"+args.region+"/"+args.inputFile
Lumi=args.Lumi



file = ROOT.TFile( fileName, "r" )

# Category map for the LaTeX naming of histograms
catMap = {
    "em" : "e#tau_{#mu}",
    "et" : "e#tau_{h}",
    "mt" : "#mu#tau_{h}",
    "me" : "#mu#tau_{e}",
}

def add_lumi():
    lowX=0.63
    lowY=0.835
    lumi  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.30, lowY+0.16, "NDC")
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.SetTextSize(0.045)
    lumi.SetTextFont (   42 )
    lumi.AddText(str(round(float(Lumi)/1000,1))+"fb^{-1} (13 TeV)")
    return lumi

def add_CMS():
    lowX=0.18
    lowY=0.745
    lumi  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.15, lowY+0.16, "NDC")
    lumi.SetTextFont(61)
    lumi.SetTextSize(0.05)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("CMS")
    return lumi

def add_Preliminary():
    lowX=0.18
    lowY=0.695
    lumi  = ROOT.TPaveText(lowX, lowY+0.06, lowX+0.15, lowY+0.16, "NDC")
    lumi.SetTextFont(52)
    lumi.SetTextSize(0.04)
    lumi.SetBorderSize(   0 )
    lumi.SetFillStyle(    0 )
    lumi.SetTextAlign(   12 )
    lumi.SetTextColor(    1 )
    lumi.AddText("Preliminary")
    return lumi

def make_legend():
	if 'dphi' in variable and 'Met' in variable:
	   output = ROOT.TLegend(0.30, 0.6, 0.92, 0.88, "", "brNDC")
           output.SetNColumns(5)
           output.SetTextSize(0.024)
	else:
           #output = ROOT.TLegend(0.65, 0.3, 0.92, 0.85, "", "brNDC")
	   output = ROOT.TLegend(0.42, 0.5, 0.92, 0.88, "", "brNDC")
           output.SetNColumns(2)
           output.SetTextSize(0.028)
        #output = ROOT.TLegend(0.2, 0.1, 0.47, 0.65, "", "brNDC")
        output.SetLineWidth(0)
        output.SetLineStyle(0)
        output.SetFillStyle(0)
        #output.SetFillColor(0)
        output.SetBorderSize(0)
        output.SetTextFont(62)

        return output

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

hist_ZTT=file.Get("mutaue_inclus").Get("ZTauTau")
if args.region!='ss':
    hist_Fakes=file.Get("mutaue_inclus").Get("QCD")
#hist_Fakes.Add(file.Get("mutaue_inclus").Get("W"))
hist_W=file.Get("mutaue_inclus").Get("W")
if args.is_TT_DD==0:
    hist_TT=file.Get("mutaue_inclus").Get("TT")
else:
    hist_TT=file.Get("mutaue_inclus").Get("TT_DD")
hist_TT.Add(file.Get("mutaue_inclus").Get("T"))
#hist_sig200=file.Get("mutaue_inclus").Get("LFV200")
#hist_sig300=file.Get("mutaue_inclus").Get("LFV300")
#hist_sig450=file.Get("mutaue_inclus").Get("LFV450")
#hist_sig600=file.Get("mutaue_inclus").Get("LFV600")
#hist_sig750=file.Get("mutaue_inclus").Get("LFV750")
#hist_sig900=file.Get("mutaue_inclus").Get("LFV900")

signals=args.signals.split(",")
signals.sort()
signal_histos=[]
for signal in signals:
#    sig_hist=file.Get("mutaue_inclus").Get("LFV"+signal)
    signal_histos.append((file.Get("mutaue_inclus").Get("LFV"+signal),"LFV"+signal))

#signal_histos=[(hist_sig200,"LFV200"), (hist_sig300,"LFV300"), (hist_sig450,"LFV450"), (hist_sig600,"LFV600"), (hist_sig750,"LFV750"), (hist_sig900,"LFV900")]

if len(signal_histos)>1:
    try:
        signal_histos[0][0].SetLineColor(ROOT.kRed)
        signal_histos[1][0].SetLineColor(ROOT.kBlack)
        signal_histos[2][0].SetLineColor(ROOT.kBlue)
    
        signal_histos[3][0].SetLineColor(ROOT.kRed)
        signal_histos[3][0].SetLineStyle(2)
        signal_histos[4][0].SetLineColor(ROOT.kBlack)
        signal_histos[4][0].SetLineStyle(2)
        signal_histos[5][0].SetLineColor(ROOT.kBlue)
        signal_histos[5][0].SetLineStyle(2)
    except IndexError:
        print "No more signals"


for histo in signal_histos:
    histo[0].SetLineWidth(4)


c.cd()
#if args.isLog:
 #   c.SetLogy()
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetBorderSize(10)
c.SetTickx(1)
c.SetTicky(1)
c.SetLeftMargin(0.16)
c.SetRightMargin(0.05)
c.SetTopMargin(0.10)
c.SetBottomMargin(0.10)
c.SetFrameFillStyle(0)
c.SetFrameLineStyle(0)
c.SetFrameLineWidth(3)
c.SetFrameBorderMode(0)
c.SetFrameBorderSize(10)



#errorBand.Draw("e2same")
integ=signal_histos[0][0].Integral()
max_y=-1
for histo in signal_histos:
    integ=histo[0].Integral()
    print histo[1],"  ",integ
    histo[0].SetTitle("")
    histo[0].Scale(1/integ)
    histo[0].Draw("histsame")
    max_y=max(histo[0].GetMaximum(),max_y)



signal_histos[0][0].GetXaxis().SetTitleSize(0.053)
signal_histos[0][0].GetXaxis().SetNdivisions(505)
signal_histos[0][0].GetYaxis().SetLabelFont(42)
signal_histos[0][0].GetYaxis().SetLabelOffset(0.01)
signal_histos[0][0].GetXaxis().SetLabelOffset(0.008)
signal_histos[0][0].GetYaxis().SetLabelSize(0.04)
signal_histos[0][0].GetXaxis().SetLabelSize(0.039)
signal_histos[0][0].GetYaxis().SetTitleSize(0.06)
signal_histos[0][0].GetYaxis().SetTitleOffset(1.0)#0.96)
signal_histos[0][0].GetXaxis().SetTitleOffset(0.84)#0.96)
signal_histos[0][0].GetYaxis().SetTitle("a.u.")
signal_histos[0][0].GetXaxis().SetTitle(varnames[variable])
signal_histos[0][0].SetMarkerStyle(20)
signal_histos[0][0].SetMarkerSize(1)

signal_histos[0][0].SetMaximum(max_y*1.5)

#hist_data.Draw("esame")
#mystack.Draw("histsame")

legend=make_legend()
#legend.AddEntry(hist_data, "Observed","elp")
#legend.AddEntry(hist_ZTT, "Z#rightarrow#tau#tau","f")
#legend.AddEntry(hist_ZL, "Z#rightarrowee/#mu#mu","f")
#legend.AddEntry(hist_TT, "t#bar{t},t+jets","f")
#legend.AddEntry(hist_VV, "Diboson","f")
#legend.AddEntry(hist_W, "W Bkgs.","f")
#if args.region!='ss':
#    legend.AddEntry(hist_Fakes, "QCD","f")
#legend.AddEntry(hist_SM, "SM Higgs","f")
##if "QCD" in analyzer or "SR" in analyzer:
for histo in signal_histos:
    legend.AddEntry(histo[0],histo[1],"l")
#legend.AddEntry(errorBand,"Bkg. unc.","f")
legend.Draw()

l1=add_lumi()
l1.Draw("same")
l2=add_CMS()
l2.Draw("same")
l3=add_Preliminary()
l3.Draw("same")

categ  = ROOT.TPaveText(0.25, 0.92, 0.50, 0.97, "NDC")
categ.SetBorderSize(   0 )
categ.SetFillStyle(    0 )
categ.SetTextAlign(   12 )
categ.SetTextSize ( 0.04 )
categ.SetTextColor(    1 )
categ.SetTextFont (   42 )
categ.AddText("#mu#tau_{e}")
categ.Draw("same")

c.cd()

ROOT.gPad.RedrawAxis()

c.Modified()
TTbar_DD=""
if args.is_TT_DD:
    TTbar_DD="_data_drivenTT"

if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD):
    os.mkdir("plots/"+analyzer+str(args.Lumi)+TTbar_DD)
if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive"):
    os.mkdir("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive")
if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/sig_only"):
    os.mkdir("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/sig_only")


c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/sig_only/"+variable.replace("#","")+".pdf")
#c.SaveAs("plots/"+ePt.png")
 
