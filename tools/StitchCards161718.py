#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *
import os, sys


f16 = TFile('QcdPredictionRun2016.root')
f17 = TFile('QcdPredictionRun2017.root')
f18 = TFile('QcdPredictionRun2018.root')

lumi16 = 35900.
lumi17 = 41500.
lumi18 = 59200.

lumitot = lumi16+lumi17+lumi18

frun2 = TFile('QcdPredictionRun2_goodforjer.root', 'recreate')
keys = f16.GetListOfKeys()
for key in keys:
    name = key.GetName()
    print name
    h16 = f16.Get(name)
    h17 = f17.Get(name)
    h18 = f18.Get(name)     
    hnew = h16.Clone()
    if 'CV' in name:
        hnew.Add(h17)
        hnew.Add(h18)
    else:
        hnew.Reset()
        h16.Scale(lumi16/lumitot)
        h17.Scale(lumi17/lumitot)
        h18.Scale(lumi18/lumitot)                
        hnew.Add(h16)
        hnew.Add(h17)
        hnew.Add(h18)
    frun2.cd()
    hnew.Write()

print 'just created', frun2.GetName()
frun2.Close()
