import ROOT
import argparse
import math

parser=argparse.ArgumentParser("extract data/mc normalization scale factors from TTbar control region")

parser.add_argument(
    "--analyzer",
    type=str,
    dest="analyzer",
    default='highmass_lowrange_TTCR',
    help='analyzer name',
    )
parser.add_argument(
    "--region",
    type=str,
    dest="region",
    default='selection',
    help='preselection or selection',
    )
parser.add_argument(
    "--lumi",
    type=int,
    dest="lumi",
    default=35858,
    help='luminosity',
    )


args=parser.parse_args()

region_name="selected"
if args.region=='preselection':
    region_name='presel'

tt_file=ROOT.TFile("preprocessed_inputs/"+args.analyzer+str(args.lumi)+"/"+args.region+"/os/h_collmass_pfmet.root","r")#.Get("mutaue_1jet_"+region_name)
print tt_file
#get data hist
data_hist=tt_file.Get("mutaue_1jet_"+region_name).Get("data_obs")

error=ROOT.Double(0.0)
data_yield=data_hist.IntegralAndError(1,data_hist.GetNbinsX(),error)


print "data_yield= ",data_yield," +/- ",error

#subtract backGs other than ttbar


data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("ggH_htt"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("ggH_hww"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("qqH_htt"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("qqH_hww"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("QCD"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("Diboson"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("Zothers"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("ZTauTau"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("W"),-1)
data_hist.Add(tt_file.Get("mutaue_1jet_"+region_name).Get("T"),-1)

error_num=ROOT.Double(0.0)
data_yield=data_hist.IntegralAndError(1,data_hist.GetNbinsX(),error_num)
print "data_yield-other_mc_yield= ",data_yield," +/- ",error_num

error_deno=ROOT.Double(0.0)
tt_hist=tt_file.Get("mutaue_1jet_"+region_name).Get("TT")
tt_yield=tt_hist.IntegralAndError(1,tt_hist.GetNbinsX(),error_deno)

print "tt_yield= ",tt_yield," +/- ",error_deno

print "SF = (data-othermc)_yield/ttbar_yield = ",data_yield/tt_yield," +/- ",(math.sqrt((error_num/data_yield)**2+(error_deno/tt_yield)**2))*(data_yield/tt_yield)
