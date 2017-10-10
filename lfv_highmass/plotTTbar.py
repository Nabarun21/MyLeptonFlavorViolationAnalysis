#!/usr/bin/env python
import copy
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
    "--lumi",
    type=int,
    action="store",
    dest="Lumi",
    default=35847,
    help="Which channel to run over? (et, mt, em, me)")
parser.add_argument(
    "--mc_v_mc",
    action="store_true",
    help="comparing mc to CR mc? otherwise compare mc to DD estimate")
parser.add_argument(
    "--analyzer",
    type=str,
    action="store",
    dest="analyzer",
    default="highmass",
    help="which analyzer's TTbar shapes do you wanna compare?")
parser.add_argument(
    "--channel",
    action="store",
    dest="channel",
    default="et",
    help="Which channel to run over? (et, mt, em, me)")
parser.add_argument(
    "--var",
    type=str,
    action="store",
    dest="variable",
    default="colmass",
    help="Which variable")
parser.add_argument(
    "--suffix",
    type=str,
    action="store",
    dest="suffix",
    default="presel",
    help="Which variable")
parser.add_argument(
    "--inputFile",
    action="store",
    dest="inputFile",
    help="Provide the relative path to the target input file")

args = parser.parse_args()

variables = [
	('BDT_value', 'BDT_value', 1),
	('h_collmass_pfmet', 'M_{coll}(e#mu) (GeV)', 1),
	('mPt', 'p_{T}(mu) (GeV)', 4),
	('mEta', 'eta(mu)', 1),
	('mPhi', 'phi(mu)', 2),
	('ePt', 'p_{T}(e) (GeV)', 4),
	('eEta', 'eta(e)', 1),
	('ePhi', 'phi(e)', 2),
	('em_DeltaPhi', 'emu Deltaphi', 1),
	('em_DeltaR', 'emu Delta R', 1),
	('h_vismass', 'M_{vis} (GeV)', 1),
	('Met', 'MET (GeV)', 1),
	('ePFMET_Mt', 'MT-e-MET (GeV)', 4),
	('mPFMET_Mt', 'MT-mu-MET (GeV)', 4),
	('ePFMET_DeltaPhi', 'Deltaphi-e-MET (GeV)', 1),
	('mPFMET_DeltaPhi', 'Deltaphi-mu-MET (GeV)', 1),
	('jetN_30', 'number of jets (p_{T} > 30 GeV)', 1),
	]


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

Lumi=args.Lumi
analyzer=args.analyzer
variable=args.variable
channel = args.channel
isLog = args.isLog
filename=args.inputFile
suffix=args.suffix
if suffix=='presel':
    selection_region='preselection'
else:
    selection_region='selection'


file1=ROOT.TFile("preprocessed_inputs/"+args.analyzer+str(args.Lumi)+"/"+selection_region+"/"+args.inputFile)
#file2=ROOT.TFile("preprocessed_inputs/ttbarCR_1bjet"+str(args.Lumi)+"/"+selection_region+"/"+args.inputFile)
file2=ROOT.TFile("preprocessed_inputs/ttbarCR_1or2bjet"+str(args.Lumi)+"/"+selection_region+"/"+args.inputFile)


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

def make_legend():
	if 'dphi' in variable and 'Met' in variable:
	   output = ROOT.TLegend(0.30, 0.6, 0.92, 0.88, "", "brNDC")
           output.SetNColumns(5)
	else:
           #output = ROOT.TLegend(0.65, 0.3, 0.92, 0.85, "", "brNDC")
	   output = ROOT.TLegend(0.42, 0.5, 0.92, 0.85, "", "brNDC")
           output.SetNColumns(2)
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


hist_SR1=file1.Get("mutaue_01jet_"+suffix).Get("TT")
#hist_SR2=file1.Get("mutaue_1jet_"+suffix).Get("TT")
#hist_SR3=file1.Get("mutaue_2jet_"+suffix).Get("TT")


#hist_SR=hist_SR1.Clone()
#hist_SR.Add(hist_SR2)

hist_SR_DD1=file1.Get("mutaue_01jet_"+suffix).Get("TT_DD")
#hist_SR_DD2=file1.Get("mutaue_1jet_"+suffix).Get("TT_DD")
#hist_SR_DD3=file1.Get("mutaue_2jet_"+suffix).Get("TT_DD")

#hist_SR_DD=hist_SR_DD1.Clone()
#hist_SR_DD.Add(hist_SR_DD2)



all_SRs={}
all_SRs["01-jet"]=hist_SR1
#all_SRs["1-jet"]=hist_SR2
#all_SRs["0_1-jet"]=hist_SR

all_SR_DDs={}
all_SR_DDs["01-jet"]=hist_SR_DD1
#all_SR_DDs["1-jet"]=hist_SR_DD2
#all_SR_DDs["0_1-jet"]=hist_SR_DD



#print all_SRs

for key in all_SRs.keys():
    if args.mc_v_mc:
        hist_ttbar_CR=file2.Get("mutaue_01jet_"+suffix).Get("TT")
    else:
        hist_ttbar_CR=all_SR_DDs[key].Clone()
    curr_hist_SR=all_SRs[key].Clone()
    # Set aesthetics
    curr_hist_SR.GetXaxis().SetTitle("")
    curr_hist_SR.GetXaxis().SetTitleSize(0)
    curr_hist_SR.GetXaxis().SetNdivisions(505)
    curr_hist_SR.GetYaxis().SetLabelFont(42)
    curr_hist_SR.GetYaxis().SetLabelOffset(0.01)
    curr_hist_SR.GetYaxis().SetLabelSize(0.06)
    curr_hist_SR.GetYaxis().SetTitleSize(0.075)
    curr_hist_SR.GetYaxis().SetTitleSize(0.09)
    curr_hist_SR.GetYaxis().SetTitleOffset(1.04)#0.96)
    curr_hist_SR.GetYaxis().SetTitleOffset(0.7)
    curr_hist_SR.SetTitle("")
    curr_hist_SR.GetYaxis().SetTitle("a.u.")
    curr_hist_SR.SetMarkerStyle(20)
    curr_hist_SR.SetMarkerSize(1)
    curr_hist_SR.SetLineWidth(1)
    
    curr_hist_SR.SetLineColor(ROOT.TColor.GetColor("#32CD32"))

    curr_hist_SR.Scale(1/curr_hist_SR.Integral())               
    hist_ttbar_CR.Scale(1/hist_ttbar_CR.Integral())               

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
        
    curr_hist_SR.SetMaximum(curr_hist_SR.GetMaximum()*100)
    curr_hist_SR.Draw("hist E")
    hist_ttbar_CR.Draw("hist E same")
    
    legend=make_legend()
    
    if args.mc_v_mc:
        legend.AddEntry(curr_hist_SR, "ttBar:no bjets", "l")
        legend.AddEntry(hist_ttbar_CR, "ttBar: 1 bjet","l")
    else:
        legend.AddEntry(curr_hist_SR, "ttBar: MC", "l")
        legend.AddEntry(hist_ttbar_CR, "ttBar: DD","l")

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
    categ.AddText("#mu#tau_{e},"+key+" "+suffix)
    categ.Draw("same")

    pad1.RedrawAxis()


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
    h1=curr_hist_SR.Clone()
    h2=hist_ttbar_CR.Clone()
    h1.Divide(h2)
    
    h1.SetMaximum(2.0)#FIXME(1.5)
    h1.SetMinimum(0.01)#FIXME(0.5)
    h1.SetMarkerStyle(20)
    h1.Sumw2()
    h1.SetStats(0)
    
#h1.GetXaxis().SetTitle("Collinear mass (GeV)")
#h1.GetXaxis().SetTitle("BDT output")
    
    h1.GetXaxis().SetTitle(varnames[variable])
    h1.GetXaxis().SetLabelSize(0.08)
    h1.GetYaxis().SetLabelSize(0.08)
    h1.GetYaxis().SetTitle("[1]/[2]")
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
    
    h1.Draw("hist")
    
    c.cd()
    pad1.Draw()
    
    ROOT.gPad.RedrawAxis()

    c.Modified()
    if not os.path.exists( 'plots' ) : os.makedirs( 'plots' )
    if not os.path.exists("plots/"+args.analyzer+str(args.Lumi)):os.makedirs("plots/"+args.analyzer+str(args.Lumi))
    

    if not os.path.exists("plots/"+args.analyzer+str(args.Lumi)):
        os.mkdir("plots/"+args.analyzer+str(args.Lumi))
    if not os.path.exists("plots/"+args.analyzer+str(args.Lumi)+"/ttbarcomp"):
        os.mkdir("plots/"+args.analyzer+str(args.Lumi)+"/ttbarcomp")


    if args.mc_v_mc:
        c.SaveAs("plots/"+args.analyzer+str(args.Lumi)+"/ttbarcomp/"+key+"_vs_1or2bjetCR_"+suffix+"_"+variable.replace("#","")+".pdf")
    else:
        c.SaveAs("plots/"+args.analyzer+str(args.Lumi)+"/ttbarcomp/"+key+"_vs_DD_"+suffix+"_"+variable.replace("#","")+".pdf")
    
