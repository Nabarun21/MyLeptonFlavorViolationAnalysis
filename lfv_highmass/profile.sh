#crei una cartella

mkdir /nfs_scratch/taroni/profile

#setti le variabili ambientali che ti servono

export megaprofile=/nfs_scratch/taroni/profile
export megatarget=tmp.root

#runni l'analizer

mega LFVHETauAnalyzer.py inputs/MCntuples_25March/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6.txt tmp.root --workers=2 --chain=5

#lasci runnare per un po' (ma non piu` di 10' se no ti annoi)

dump_profile_stats.py /nfs_scratch/taroni/profile/LFVHETauAnalyzer/*.prf
