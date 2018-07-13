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
hist_TT.Scale(0.855636610815)
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

hist_VV=file.Get("mutaue_inclus").Get("Diboson")
hist_data=file.Get("mutaue_inclus").Get("data_obs")
hist_ZL=file.Get("mutaue_inclus").Get("Zothers")
hist_SM=file.Get("mutaue_inclus").Get("ggH_htt")
#hist_SM.Add(file.Get("mutaue_inclus").Get("qqH_htt"))
#hist_SM.Add(file.Get("mutaue_inclus").Get("ggH_hww"))
#hist_SM.Add(file.Get("mutaue_inclus").Get("qqH_hww"))
 
Lumi_uncert=0.026
e_eff_uncert=0.02
mu_eff_uncert=0.02

squared_sum_others=Lumi_uncert*Lumi_uncert+e_eff_uncert*e_eff_uncert+mu_eff_uncert*mu_eff_uncert
for k in range(1,hist_ZTT.GetSize()-1):
   hist_TT.SetBinError(k,(squared_sum_others*hist_TT.GetBinContent(k)*hist_TT.GetBinContent(k)+0.10*hist_TT.GetBinContent(k)*0.10*hist_TT.GetBinContent(k)+hist_TT.GetBinError(k)*hist_TT.GetBinError(k))**0.5)
   hist_ZTT.SetBinError(k,(squared_sum_others*hist_ZTT.GetBinContent(k)*hist_ZTT.GetBinContent(k)+0.10*hist_ZTT.GetBinContent(k)*0.10*hist_ZTT.GetBinContent(k)+hist_ZTT.GetBinError(k)*hist_ZTT.GetBinError(k))**0.5)
   hist_ZL.SetBinError(k,(squared_sum_others*hist_ZL.GetBinContent(k)*hist_ZL.GetBinContent(k)+0.12*hist_ZL.GetBinContent(k)*0.12*hist_ZL.GetBinContent(k)+hist_ZL.GetBinError(k)*hist_ZL.GetBinError(k))**0.5)
   hist_VV.SetBinError(k,(squared_sum_others*hist_VV.GetBinContent(k)*hist_VV.GetBinContent(k)+0.05*hist_VV.GetBinContent(k)*0.05*hist_VV.GetBinContent(k)+hist_VV.GetBinError(k)*hist_VV.GetBinError(k))**0.5)
   if args.region!='ss':
       hist_Fakes.SetBinError(k,(squared_sum_others*hist_Fakes.GetBinContent(k)*hist_Fakes.GetBinContent(k)+0.30*hist_Fakes.GetBinContent(k)*0.30*hist_Fakes.GetBinContent(k)+hist_Fakes.GetBinError(k)*hist_Fakes.GetBinError(k))**0.5)
   hist_W.SetBinError(k,(squared_sum_others*hist_W.GetBinContent(k)*hist_W.GetBinContent(k)+0.1*hist_W.GetBinContent(k)*0.1*hist_W.GetBinContent(k)+hist_W.GetBinError(k)*hist_W.GetBinError(k))**0.5)
   hist_SM.SetBinError(k,(squared_sum_others*hist_SM.GetBinContent(k)*hist_SM.GetBinContent(k)+0.10*hist_SM.GetBinContent(k)*0.10*hist_SM.GetBinContent(k)+hist_SM.GetBinError(k)*hist_SM.GetBinError(k))**0.5)
if args.region!='ss':
    hist_Fakes.SetFillColor(ROOT.TColor.GetColor("#ffccff"))
    hist_Fakes.SetLineColor(1)
hist_VV.SetFillColor(ROOT.TColor.GetColor("#12cadd"))
hist_VV.SetLineColor(1)
hist_W.SetFillColor(ROOT.TColor.GetColor("#32CD32"))
hist_W.SetLineColor(1)
hist_ZTT.SetFillColor(ROOT.TColor.GetColor("#ffcc66"))
hist_ZTT.SetLineColor(1)
hist_ZL.SetFillColor(ROOT.TColor.GetColor("#4496c8"))
hist_ZL.SetLineColor(1)
hist_TT.SetFillColor(ROOT.TColor.GetColor("#9999cc"))
hist_TT.SetLineColor(1)
hist_SM.SetFillColor(ROOT.TColor.GetColor("#c243cd"))
hist_SM.SetLineColor(1)
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

hist_data.SetLineColor(1)

mystack=ROOT.THStack("mystack","")

mystack.Add(hist_W)
mystack.Add(hist_SM)
mystack.Add(hist_VV)
if args.region!='ss':
    mystack.Add(hist_Fakes)
mystack.Add(hist_TT)
mystack.Add(hist_ZL)
mystack.Add(hist_ZTT)

errorBand=hist_VV.Clone()
errorBand.Add(hist_SM)
if args.region!='ss':
    errorBand.Add(hist_Fakes)
errorBand.Add(hist_W)
errorBand.Add(hist_TT)
errorBand.Add(hist_ZL)
errorBand.Add(hist_ZTT)
    
# Set aesthetics
hist_data.GetXaxis().SetTitleSize(0.053)
hist_data.GetXaxis().SetNdivisions(505)
hist_data.GetYaxis().SetLabelFont(42)
hist_data.GetYaxis().SetLabelOffset(0.01)
hist_data.GetXaxis().SetLabelOffset(0.008)
hist_data.GetYaxis().SetLabelSize(0.04)
hist_data.GetXaxis().SetLabelSize(0.039)
hist_data.GetYaxis().SetTitleSize(0.06)
hist_data.GetYaxis().SetTitleOffset(1.0)#0.96)
hist_data.GetXaxis().SetTitleOffset(0.84)#0.96)
hist_data.SetTitle("")
hist_data.GetYaxis().SetTitle("Events/bin")
hist_data.GetXaxis().SetTitle(varnames[variable])
hist_data.SetMarkerStyle(20)
hist_data.SetMarkerSize(1)
hist_data.SetLineWidth(1)

for histo in signal_histos:
    histo[0].SetLineWidth(4)

errorBand.SetMarkerSize(0)
errorBand.SetFillColor(new_idx)
errorBand.SetFillStyle(3001)
errorBand.SetLineWidth(1)

c.cd()
if args.isLog:
    c.SetLogy()
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

for histo in signal_histos:
    for bin in range(histo[0].GetNbinsX()+1):
        bg_count=mystack.GetStack().Last().GetBinContent(bin)
        sig_count=histo[0].GetBinContent(bin)
        if sig_count<=0:
            continue
        if (float(sig_count)/float(sig_count+bg_count)>0.0050):#blind if if s/(s+b)>0.5%
            hist_data.SetBinContent(bin,0)
            hist_data.SetBinError(bin,0)

#always blind discriminating mass histos after a certain value excpet when plotting CRs 
if args.region!='ss':
    start_blinding_at=160 #(GeV)
    if 'mass' in variable and "CR" not in args.analyzer:
        start_bin=hist_data.FindFixBin(start_blinding_at)
        for bin in range(start_bin,hist_data.GetNbinsX()+1):
            hist_data.SetBinContent(bin,0)
            hist_data.SetBinError(bin,0)

#mystack.SetMaximum(1000*mystack.GetMaximum())
if args.isLog:
    hist_data.SetMaximum(100000*hist_data.GetMaximum())
else:
    hist_data.SetMaximum(1.7*hist_data.GetMaximum())
#errorBand.SetMaximum(1000*mystack.GetMaximum())
#hist_data.SetMinimum(0.00000000001)
hist_data.SetMinimum(0.0001)
mystack.SetMinimum(0.00001)
hist_data.Draw("ep")
mystack.Draw("histsame")


errorBand.Draw("e2same")

for histo in signal_histos:
    if args.isLog:
        histo[0].Scale(higgsSF)
    else:
        histo[0].Scale(higgsSF)
    histo[0].Draw("histsame")



hist_data.Draw("esame")
#mystack.Draw("histsame")

legend=make_legend()
legend.AddEntry(hist_data, "Observed","elp")
legend.AddEntry(hist_ZTT, "Z#rightarrow#tau#tau","f")
legend.AddEntry(hist_ZL, "Z#rightarrowee/#mu#mu","f")
legend.AddEntry(hist_TT, "t#bar{t},t+jets","f")
legend.AddEntry(hist_VV, "Diboson","f")
legend.AddEntry(hist_W, "W Bkgs.","f")
if args.region!='ss':
    legend.AddEntry(hist_Fakes, "QCD","f")
legend.AddEntry(hist_SM, "SM Higgs","f")
#if "QCD" in analyzer or "SR" in analyzer:
for histo in signal_histos:
    legend.AddEntry(histo[0],histo[1],"l")
legend.AddEntry(errorBand,"Bkg. unc.","f")
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
categ.AddText("#mu#tau_{e}, inclusive")
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
if not os.path.exists("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/"+args.region):
    os.mkdir("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/"+args.region)


c.SaveAs("plots/"+analyzer+str(args.Lumi)+TTbar_DD+"/inclusive/"+args.region+"/"+variable.replace("#","")+".pdf")
#c.SaveAs("plots/"+ePt.png")
 
