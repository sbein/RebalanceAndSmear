#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *
import os, sys

loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}

f16 = TFile('QcdPredictionRun2016.root')
f17 = TFile('QcdPredictionRun2017.root')
f18pre = TFile('QcdPredictionRun2018PreHem.root')
f18dur = TFile('QcdPredictionRun2018DuringHem.root')

doAllRun2 = True#set false to get the goodforjer.root file

lumi16 = 35900.
lumi17 = 41500.
lumi18pre = 20919.
lumi18dur = 38628.

lumitot = lumi16+lumi17+lumi18pre+lumi18dur

if doAllRun2: frun2 = TFile('QcdPredictionRun2.root', 'recreate')##funny name should probably be different
else: frun2 = TFile('QcdPredictionRun2_goodforjer.root', 'recreate')#run this to replenish stash for master assemble
keys = f16.GetListOfKeys()
for key in keys:
    
    name = key.GetName()
    print name
    if 'Uncorrelated' in name or 'Stat' in name: continue    
    h16 = f16.Get(name)
    h17 = f17.Get(name)
    h18pre = f18pre.Get(name)
    h18dur = f18dur.Get(name)    
    hnew = h16.Clone()
    if 'CV' in name:
        hnew.Add(h17)
        hnew.Add(h18pre)
        hnew.Add(h18dur)        
    else:
        hnew.Reset()
        h16.Scale(lumi16/lumitot)
        h17.Scale(lumi17/lumitot)
        h18pre.Scale(lumi18pre/lumitot)
        h18dur.Scale(lumi18dur/lumitot)        
        hnew.Add(h16)
        hnew.Add(h17)
        hnew.Add(h18pre)
        hnew.Add(h18dur)        
    frun2.cd()
    hnew.Write()

fbtag = TFile('usefulthings/btagcorrector.root')
fbtag.ls()
hbtagcor = fbtag.Get('hBTagCorrection')

f16.ls()
hbtagsys = f16.Get('PredictionCore').Clone('BTagSys')
hbtagsys.Reset()
xax = hbtagsys.GetXaxis()
for ibin in range(1, xax.GetNbins()+1):
    hbtagsys.GetXaxis().SetBinLabel(ibin, xax.GetBinLabel(ibin).replace('Core', 'BTag'))
    windows = SearchBinWindows[ibin]
    blow = windows[3][0]+1
    jhigh = windows[2][1]
    if jhigh<6:
        correctionweight = hbtagcor.GetBinContent(hbtagcor.GetXaxis().FindBin(blow))
        hbtagsys.SetBinContent(ibin, correctionweight)
    if hbtagsys.GetBinContent(ibin)==0: hbtagsys.SetBinContent(ibin, 1.0)
    
frun2.cd()
if doAllRun2:
    fstat = TFile('QcdPredictionRun2-OnlyUsedForStat.root')# used only for stat
    hstat = fstat.Get('PredictionUncorrelated')
    frun2.cd()
    hstat.Write("PredictionUncorrelated")


hbtagsys.Write('PredictionBTag')
print 'just created', frun2.GetName()
frun2.Close()
