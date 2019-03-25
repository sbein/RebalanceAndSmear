from ROOT import *
'''
#The 2018 HEM-weighted predictions should be in VaultHem/, and they need to be bundled up
python tools/StitchUpHemPrediction.py


#then pause to carry out commands it suggests (move new files into Vault)

hadd -f Vault/RandS_Run2_1of5.root Vault/RandS_Run2016_1of5.root Vault/RandS_Run2017_1of5.root Vault/RandS_Run2018_1of5.root
hadd -f Vault/RandS_Run2_2of5.root Vault/RandS_Run2016_2of5.root Vault/RandS_Run2017_2of5.root Vault/RandS_Run2018_2of5.root
hadd -f Vault/RandS_Run2_3of5.root Vault/RandS_Run2016_3of5.root Vault/RandS_Run2017_3of5.root Vault/RandS_Run2018_3of5.root
hadd -f Vault/RandS_Run2_4of5.root Vault/RandS_Run2016_4of5.root Vault/RandS_Run2017_4of5.root Vault/RandS_Run2018_4of5.root
hadd -f Vault/RandS_Run2_5of5.root Vault/RandS_Run2016_5of5.root Vault/RandS_Run2017_5of5.root Vault/RandS_Run2018_5of5.root

python tools/processBootstrap.py Run2016
python tools/processBootstrap.py Run2017
python tools/processBootstrap.py Run2018
python tools/processBootstrap.py Run2018PreHem
python tools/processBootstrap.py Run2018DuringHem
python tools/processBootstrap.py Run2

'''

from utils import *
from ra2blibs import *
from glob import glob
import numpy as np
import sys

nBoot = 5

try: year = sys.argv[1]
except: year = 'Run2017'


flist = glob('Vault/*'+year+'_*of'+str(nBoot)+'.root')
print 'flist', flist

fnew = TFile('OutputBootstrap'+year+'.root','recreate')
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
    if not 'RplusS' in name: 
        h = files[0].Get(name)
        fnew.cd()
        h.Write(name)
        continue
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
        #hMaster = hMaster.Rebin(nbins,'',newxs)
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        #hMaster = hMaster.Rebin(nbins,'',newxs) 

    if 'hLowMhtBaseline_SearchBins' in name: 
        hMaster = hMaster.Rebin(nbins,'',newxs)
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
                if hMaster.GetBinContent(ibin)>0 and countByHtMht[countkey]>0:
                    countByHtMht[countkey] = min(countByHtMht[countkey], hMaster.GetBinContent(ibin))
                    errorByHtMht[countkey] = min(errorByHtMht[countkey], hMaster.GetBinError(ibin))                    
                else:
                    countByHtMht[countkey] = max(countByHtMht[countkey], hMaster.GetBinContent(ibin))
                    errorByHtMht[countkey] = max(errorByHtMht[countkey], hMaster.GetBinError(ibin))                    
        for ibin in range(1, xax.GetNbins()+1): 
            countkey = SearchBinWindows[ibin][:2]
            if hMaster.GetBinContent(ibin)==0: 
                print 'fixing this up', ibin, countByHtMht[countkey], errorByHtMht[countkey], 'center', xax.GetBinCenter(ibin)
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
