import argparse
import os
import ROOT

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser(
    "draw nominal, up and down shapes of template varying nuisances ")
parser.add_argument(
    "--lowmass",
    action="store_true",
    help="if set , draw nuisance shapes for lowmass range, else for highmass range")
parser.add_argument(
    "--inp_file_name",
    type=str,
    action="store",
    dest="inp_file_name",
    default="HMuTau_mutaue_2016_input_36fb_bbb_highmass.root",
    help="input file name")


xlabel="Collinear Mass(#mu,e)"
lowmass_hists=["ZTauTau","Zothers","Diboson","TT","T","W","QCD","SMH","LFV200","LFV300","LFV450"]
highmass_hists=["TT","Zothers","Diboson","TT","T","W","QCD","SMH","LFV450","LFV600","LFV750","LFV900","ZTauTau"]

args = parser.parse_args()

inp_file=ROOT.TFile(args.inp_file_name,'r')

#sysfolder names in analyzer
syst_names_datacard=['nominal_no_name','CMS_MES_13TeV','CMS_MES_13TeV','CMS_EES_13TeV','CMS_EES_13TeV','CMS_Eresrho_13TeV','CMS_Eresrho_13TeV','CMS_Eresphi_13TeV','CMS_Eresphi_13TeV','CMS_Pileup_13TeV','CMS_Pileup_13TeV','CMS_MET_chargedUes_13TeV','CMS_MET_chargedUes_13TeV','CMS_MET_ecalUes_13TeV','CMS_MET_ecalUes_13TeV','CMS_MET_hcalUes_13TeV','CMS_MET_hcalUes_13TeV','CMS_MET_hfUes_13TeV','CMS_MET_hfUes_13TeV',
             'CMS_Jes_JetAbsoluteFlavMap_13TeV',
             'CMS_Jes_JetAbsoluteMPFBias_13TeV',
             'CMS_Jes_JetAbsoluteScale_13TeV',
             'CMS_Jes_JetAbsoluteStat_13TeV',
             'CMS_Jes_JetFlavorQCD_13TeV',
             'CMS_Jes_JetFragmentation_13TeV',
             'CMS_Jes_JetPileUpDataMC_13TeV',
             'CMS_Jes_JetPileUpPtBB_13TeV',
             'CMS_Jes_JetPileUpPtEC1_13TeV',
             'CMS_Jes_JetPileUpPtEC2_13TeV',
             'CMS_Jes_JetPileUpPtHF_13TeV',
             'CMS_Jes_JetPileUpPtRef_13TeV',
             'CMS_Jes_JetRelativeBal_13TeV',
             'CMS_Jes_JetRelativeFSR_13TeV',
             'CMS_Jes_JetRelativeJEREC1_13TeV',
             'CMS_Jes_JetRelativeJEREC2_13TeV',
             'CMS_Jes_JetRelativeJERHF_13TeV',
             'CMS_Jes_JetRelativePtBB_13TeV',
             'CMS_Jes_JetRelativePtEC1_13TeV',
             'CMS_Jes_JetRelativePtEC2_13TeV',
             'CMS_Jes_JetRelativePtHF_13TeV',
             'CMS_Jes_JetRelativeStatEC_13TeV',
             'CMS_Jes_JetRelativeStatFSR_13TeV',
             'CMS_Jes_JetRelativeStatHF_13TeV',
             'CMS_Jes_JetSinglePionECAL_13TeV',
             'CMS_Jes_JetSinglePionHCAL_13TeV',
             'CMS_Jes_JetTimePtEta_13TeV',
             'CMS_Jes_JetAbsoluteFlavMap_13TeV',
             'CMS_Jes_JetAbsoluteMPFBias_13TeV',
             'CMS_Jes_JetAbsoluteScale_13TeV',
             'CMS_Jes_JetAbsoluteStat_13TeV',
             'CMS_Jes_JetFlavorQCD_13TeV',
             'CMS_Jes_JetFragmentation_13TeV',
             'CMS_Jes_JetPileUpDataMC_13TeV',
             'CMS_Jes_JetPileUpPtBB_13TeV',
             'CMS_Jes_JetPileUpPtEC1_13TeV',
             'CMS_Jes_JetPileUpPtEC2_13TeV',
             'CMS_Jes_JetPileUpPtHF_13TeV',
             'CMS_Jes_JetPileUpPtRef_13TeV',
             'CMS_Jes_JetRelativeBal_13TeV',
             'CMS_Jes_JetRelativeFSR_13TeV',
             'CMS_Jes_JetRelativeJEREC1_13TeV',
             'CMS_Jes_JetRelativeJEREC2_13TeV',
             'CMS_Jes_JetRelativeJERHF_13TeV',
             'CMS_Jes_JetRelativePtBB_13TeV',
             'CMS_Jes_JetRelativePtEC1_13TeV',
             'CMS_Jes_JetRelativePtEC2_13TeV',
             'CMS_Jes_JetRelativePtHF_13TeV',
             'CMS_Jes_JetRelativeStatEC_13TeV',
             'CMS_Jes_JetRelativeStatFSR_13TeV',
             'CMS_Jes_JetRelativeStatHF_13TeV',
             'CMS_Jes_JetSinglePionECAL_13TeV',
             'CMS_Jes_JetSinglePionHCAL_13TeV',
             'CMS_Jes_JetTimePtEta_13TeV']      #sysfolder names in analyzer                                                                                                                                                                                          


hists=lowmass_hists if args.lowmass else highmass_hists
addendum="lowmass" if args.lowmass else "highmass"
canv=ROOT.TCanvas()
for cat in range(2):
    for hist in hists:
        print("HMuTau_mutaue_"+str(cat+1)+"_2016","  ",hist)
        nominal=inp_file.Get("HMuTau_mutaue_"+str(cat+1)+"_2016").Get(hist)
        nom_max=nominal.GetBinContent(nominal.GetMaximumBin())
        for syst in syst_names_datacard:
            print "empty: "+"HMuTau_mutaue_"+str(cat+1)+"_2016"+hist+"_"+syst+"Up"                                            
            up=inp_file.Get("HMuTau_mutaue_"+str(cat+1)+"_2016").Get(hist+"_"+syst+"Up")

            if up==None:
                print "empty: "+"HMuTau_mutaue_"+str(cat+1)+"_2016"+hist+"_"+syst+"Up"
                continue
            nominal.SetLineColor(ROOT.kBlack)
        
            up.SetTitle("Mutaue_"+addendum+"_"+str(cat)+"jet_"+hist+"_"+syst)
            up_max=up.GetBinContent(up.GetMaximumBin())


            
            down=inp_file.Get("HMuTau_mutaue_"+str(cat+1)+"_2016").Get(hist+"_"+syst+"Down")
            down.SetLineColor(ROOT.kRed)
            down_max=down.GetBinContent(down.GetMaximumBin())

            
            ymax=max(nom_max,max(up_max,down_max))*1.3
                  
            if ymax==0:continue


#            canv.SetTitle("Mutaue_"+addendum+"_"+str(cat)+"jet_"+hist+"_"+syst)

            
#            canv.DrawFrame(0,1500,0,ymax)
            
            leg=ROOT.TLegend(0.6,0.7,0.9,0.9)
            leg.AddEntry(nominal,"nominal","l")
            leg.AddEntry(up,"Up","l")
            leg.AddEntry(down,"Down","l")

            canv.cd()
            upper_pad=ROOT.TPad("pad1", "pad1", 0, 0.33, 1, 1.0)
            upper_pad.SetBottomMargin(0.05)
            upper_pad.Draw()
            upper_pad.cd()

            up.Draw("Hist")
            down.Draw("Hist same")
            nominal.Draw("Hist same")
            nominal.SetAxisRange(0.,ymax,"Y")
            up.SetAxisRange(0.,ymax,"Y")
            down.SetAxisRange(0.,ymax,"Y")

            leg.Draw("same")

            latex_nom = ROOT.TLatex(0.65,0.50,"nominal yield  = "+str(round(nominal.Integral(),1)))
            latex_nom.SetNDC();
            latex_nom.SetTextSize(0.04);
            latex_nom.SetTextAlign(31);
            latex_nom.SetTextAlign(11);
            latex_up = ROOT.TLatex(0.65,0.45,"up yield  = "+str(round(up.Integral(),1)))
            latex_up.SetNDC();
            latex_up.SetTextSize(0.04);
            latex_up.SetTextAlign(31);
            latex_up.SetTextAlign(11);
            latex_down = ROOT.TLatex(0.65,0.40,"down yield  = "+str(round(down.Integral(),1)))
            latex_down.SetNDC();
            latex_down.SetTextSize(0.04);
            latex_down.SetTextAlign(31);
            latex_down.SetTextAlign(11);
            

            latex_nom.Draw('same')
            latex_up.Draw('same')
            latex_down.Draw('same')

            canv.cd()
            lower_pad=ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.30)
            lower_pad.SetTopMargin(0)
            lower_pad.SetBottomMargin(0.3)
            lower_pad.Draw()
            lower_pad.cd()
            histo_down_clone=down.Clone()
            histo_down_clone.Add(nominal,-1)
            histo_down_clone.Divide(nominal)
            histo_down_clone.SetLineColor(ROOT.kRed)
            histo_down_clone.SetMarkerSize(1.5)
            histo_down_clone.SetMarkerColor(ROOT.kRed)
            histo_down_clone.SetMarkerStyle(33)
            histo_down_clone.SetTitle("")
            histo_down_clone.SetStats(0)
            histo_down_clone.Draw("hist same")
            histo_down_clone.GetYaxis().SetTitle("#frac{shifted-nominal}{nominal} ")
            histo_down_clone.GetYaxis().SetRangeUser(-0.5,0.5)
            histo_down_clone.GetYaxis().SetNdivisions(505)
            histo_down_clone.GetYaxis().SetTitleSize(15)
            histo_down_clone.GetYaxis().SetTitleFont(43)
            histo_down_clone.GetYaxis().SetTitleOffset(1.3)
            histo_down_clone.GetYaxis().SetLabelSize(0.1);
            histo_down_clone.GetXaxis().SetTitle(xlabel);
            histo_down_clone.GetXaxis().SetTitleSize(15);
            histo_down_clone.GetXaxis().SetTitleFont(43);
            histo_down_clone.GetXaxis().SetTitleOffset(4.);
            histo_down_clone.GetXaxis().SetLabelFont(43);

            histo_up_clone=up.Clone()
            histo_up_clone.Add(nominal,-1)
            histo_up_clone.SetStats(0)
            histo_up_clone.Divide(nominal)
            histo_up_clone.SetLineColor(ROOT.kBlue)
            histo_up_clone.SetMarkerSize(1)
            histo_up_clone.SetMarkerColor(ROOT.kBlue)
            histo_up_clone.SetMarkerStyle(34)
            histo_up_clone.SetTitle("")
            histo_up_clone.Draw("hist same")
            histo_up_clone.GetYaxis().SetTitle("#frac{shifted-nominal}{nominal} ")
            histo_up_clone.GetYaxis().SetNdivisions(505)
            histo_up_clone.GetYaxis().SetTitleSize(15)
            histo_up_clone.GetYaxis().SetTitleFont(43)
            histo_up_clone.GetYaxis().SetTitleOffset(1.3)
            histo_up_clone.GetYaxis().SetLabelSize(15);
            histo_up_clone.GetXaxis().SetTitle(xlabel);
            histo_up_clone.GetXaxis().SetTitleSize(15);
            histo_up_clone.GetXaxis().SetTitleFont(43);
            histo_up_clone.GetXaxis().SetTitleOffset(4.);
            histo_up_clone.GetXaxis().SetLabelFont(43);
            x_range=[-300,1500]
            ref_function = ROOT.TF1('f', "0.",*x_range)
	    ref_function.SetLineWidth(1)
            ref_function.SetLineStyle(3)
            ref_function.SetLineColor(ROOT.kBlack)
            ref_function2 = ROOT.TF1('f1', "0.25",*x_range)
            ref_function2.SetLineWidth(1)
            ref_function2.SetLineStyle(6)
            ref_function2.SetLineColor(ROOT.kBlack)
            ref_function3 = ROOT.TF1('f2', "-0.25",*x_range)
            ref_function3.SetLineWidth(1)
            ref_function3.SetLineStyle(6)
            ref_function3.SetLineColor(ROOT.kBlack)
            ref_function.Draw('same')
            ref_function2.Draw('same')
            ref_function3.Draw('same')
            
            canv.SaveAs(addendum+"/Mutaue_"+addendum+"_"+str(cat)+"jet_"+hist+"_"+syst+".pdf")
