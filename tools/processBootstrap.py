from ROOT import *
from utils import *
from ra2blibs import *
from glob import glob
import numpy as np

nBoot = 5
flist = glob('Vault/*of'+str(nBoot)+'.root')

fnew = TFile('OutputBoostrapRun2017.root','recreate')
loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}
redoBinning = binningAnalysis

files = []
for fname in flist:
    files.append(TFile(fname))
    
keys = files[0].GetListOfKeys()
files[0].ls()
names = []
for key in keys: names.append(key.GetName())

for name in names:
    if not 'RplusS' in name: continue
    hMaster = files[0].Get(name).Clone()
    hMaster.SetDirectory(0)
    hMaster.Reset()
    xax = hMaster.GetXaxis()
    for ibin in range(1, xax.GetNbins()+1):
        vals = []
        for fil in files:
            h = fil.Get(name)
            vals.append(h.GetBinContent(ibin))
        haux = TH1F('','',100,min(vals)-1,max(vals)+1)
        for val in vals: haux.Fill(val)
        hMaster.SetBinContent(ibin, haux.GetMean())
        hMaster.SetBinError(ibin, haux.GetRMS())  

    kinvar = name.replace('GenSmeared','').replace('Rebalanced','').replace('RplusS','')
    selection = kinvar[1:kinvar.find('_')]
    kinvar = kinvar[kinvar.find('_')+1:]
    print 'kinvar', kinvar, name
    if len(redoBinning[kinvar])>3:
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hMaster = hMaster.Rebin(nbins,'',newxs)        
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hMaster = hMaster.Rebin(nbins,'',newxs) 

    if 'SearchBins' in name: 
        xax = hMaster.GetXaxis()
        countByHtMht = {}
        errorByHtMht = {}        
        for ibin in range(1, xax.GetNbins()+1): 
            countkey = SearchBinWindows[ibin][:2]
            print 'countkey', countkey
            if not countkey in countByHtMht.keys(): 
                countByHtMht[countkey] = hMaster.GetBinContent(ibin) 
                errorByHtMht[countkey] = hMaster.GetBinError(ibin) 
            else: 
                countByHtMht[countkey] = max(countByHtMht[countkey], hMaster.GetBinContent(ibin))
                errorByHtMht[countkey] = max(errorByHtMht[countkey], hMaster.GetBinError(ibin))
        for ibin in range(1, xax.GetNbins()+1): 
            countkey = SearchBinWindows[ibin][:2]
            if hMaster.GetBinContent(ibin)==0: 
                hMaster.SetBinContent(ibin, countByHtMht[countkey])
                hMaster.SetBinError(ibin, errorByHtMht[countkey])                
        for ibin in range(1, xax.GetNbins()+1): 
            if hMaster.GetBinContent(ibin)==0: 
                print '*'
            print ibin, hMaster.GetBinContent(ibin), 'pm', hMaster.GetBinError(ibin), SearchBinWindows[ibin]
    fnew.cd()
    hMaster.Scale(nBoot)
    hMaster.Write()

print 'just created', fnew.GetName()
