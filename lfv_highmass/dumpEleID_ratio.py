import ROOT

file1 = ROOT.TFile.Open("EleID_ratio.root", "READ")

h = file1.Get("EleID_SF")

nbinpt = h.GetXaxis().GetNbins()
nbineta = h.GetYaxis().GetNbins()
jeta = 1

while  jeta <= nbineta :

    ydown =  h.GetYaxis().GetBinLowEdge(jeta)
    yup = h.GetYaxis().GetBinUpEdge(jeta)
    print 'if eta > %f and eta <= %f :' %(ydown, yup)
    ipt=1 
    while  ipt <= nbinpt:
        xdown = h.GetXaxis().GetBinLowEdge(ipt)
        xup =  h.GetXaxis().GetBinUpEdge(ipt)

        value = h.GetBinContent(ipt,jeta)
        
        print '\t if pt > %i and pt<= %i :'%(xdown, xup)
        print '\t \t return %f \n' %(value)  
        ipt +=1
    jeta +=1

file1.Close()
