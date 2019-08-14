#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *
import os, sys

try: year = sys.argv[1]
except: year = 'Run2016'

hem_filter = 'Hemv0p5'
        
redoBinning = binningAnalysis
labelfilename = 'Vault/QcdPredictionSUS-16-033.root'
labelfile = TFile(labelfilename)
labeledhist = labelfile.Get('PredictionCV')
labeledhist.Reset()
xax = labeledhist.GetXaxis()

newname = 'QcdPrediction'+year+'.root'
if year=='Run2': newname = newname.replace('.root','-OnlyUsedForStat.root')
fnew = TFile(newname,'recreate')
loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}
redoBinning = binningAnalysis


hCentral = labeledhist.Clone('')
fCentral = TFile('validation_data'+year+'HDP.root')
centralname = 'hLowMhtBaseline_SearchBinsRplusS'
if year=='Run2018DuringHem': centralname = centralname.replace('Baseline','Base').replace('_',hem_filter+'_')
hCentral_ = fCentral.Get(centralname).Clone('hLowMhtBaseline_SearchBinsRplusS_aux')
for ibin in range(1,xax.GetNbins()+1):
    hCentral.SetBinContent(ibin, hCentral_.GetBinContent(ibin))
    hCentral.SetBinError(ibin, hCentral_.GetBinError(ibin))   
    print ibin, 'setting bin error', hCentral_.GetBinError(ibin)

hStat = hCentral.Clone('hStat')
xax = hStat.GetXaxis()
for ibin in range(1,xax.GetNbins()+1):
    bc = hCentral_.GetBinContent(ibin)
    if bc>0:
        hStat.SetBinContent(ibin, 1+hCentral_.GetBinError(ibin)/bc)
    else:
        hStat.SetBinContent(ibin, 2)
    hCentral.GetXaxis().SetBinLabel(ibin, labeledhist.GetXaxis().GetBinLabel(ibin))
fnew.cd()
hCentral.Write('PredictionCV')


for ibin in range(1, xax.GetNbins()+1): 
    bxwindow = SearchBinWindows[ibin][3]
    if bxwindow[0]+1>=3: 
        origerror = hStat.GetBinContent(ibin)-1
        newerrr = 0.2
        hStat.SetBinContent(ibin, 1+TMath.Sqrt(pow(origerror,2)+pow(newerrr,2)))
    print 'stat', ibin, hStat.GetBinContent(ibin)

hStat.Write('PredictionUncorrelated')
#fCentral.Close()


'''
fnjetsyst = TFile('Vault/data-validation-njetsyst.root')
hSyst_njet = fnjetsyst.Get('hRatio_LdpLmhtSideband_RplusSAndTruth_NJets')

PredictionNJet = hCentral.Clone('PredictionNJet')
PredictionNJet.Reset()
xax_jet = hSyst_njet.GetXaxis()
for ibin in range(1, xax.GetNbins()+1): 
    jetmult = SearchBinWindows[ibin][2][0]+1
    jetbin = xax_jet.FindBin(jetmult)
    PredictionNJet.SetBinContent(ibin, hSyst_njet.GetBinContent(jetbin))

for ibin in range(1,xax.GetNbins()+1):
    PredictionNJet.GetXaxis().SetBinLabel(ibin, 'QCDNJets')    
fnew.cd()
#PredictionNJet.Write('PredictionNJet')
#fnjetsyst.Close()
'''


hSyst_tail = hStat.Clone('hSyst_tail')
for ibin in range(1,xax.GetNbins()+1):
    hSyst_tail.SetBinContent(ibin, 1.3)
fnew.cd()
for ibin in range(1,xax.GetNbins()+1):
    hSyst_tail.GetXaxis().SetBinLabel(ibin, 'QCDTail')
hSyst_tail.GetYaxis().SetRangeUser(0.0001, 5.0)
hSyst_tail.Write('PredictionTail')

if not year=='Run2':
    fJerImpact = TFile('Vault/JerImpact'+year.replace('PreHem','').replace('PostHem','').replace('DuringHem','')+'.root')
    fJerImpact.ls()
    hUp = fJerImpact.Get('hhLowMhtBaseline_HtRplusSJerUp')
    hNom = fJerImpact.Get('hhLowMhtBaseline_HtRplusSJerNom')
    kinvar = 'Ht'
    if len(redoBinning[kinvar])>3: 
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hUp = hUp.Rebin(nbins,'',newxs)
        hNom = hNom.Rebin(nbins,'',newxs)        
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hUp = hUp.Rebin(nbins,'',newxs)
        hNom = hNom.Rebin(nbins,'',newxs)

    PredictionCore = hStat.Clone('PredictionCore')
    PredictionCore.Reset()
    xaxsyst = hUp.GetXaxis()
    for ibin in range(1, xax.GetNbins()+1): 
        countkey = SearchBinWindows[ibin][0]
        valueinbin = 1.0*countkey[0]+0.01
        #if not countkey in countNom.keys(): 
        #countNom[countkey] += hNom.GetBinContent(ibin)
        #countUp[countkey] += hUp.GetBinContent(ibin)        
        #for ibin in range(1, xaxsyst.GetNbins()+1): 
        #countkey = SearchBinWindows[ibin][:1]
        systBin = xaxsyst.FindBin(valueinbin)
        PredictionCore.SetBinContent(ibin, hUp.GetBinContent(systBin) / hNom.GetBinContent(systBin))

    for ibin in range(1,xax.GetNbins()+1):
        PredictionCore.GetXaxis().SetBinLabel(ibin, 'QCDCore')
else:
    PredictionCore = hStat.Clone('PredictionCore')
    PredictionCore.Reset()
    fForCore = TFile('QcdPredictionRun2_goodforjer.root')
    PredictionCore = fForCore.Get('PredictionCore')
    
fnew.cd()
PredictionCore.GetYaxis().SetRangeUser(0.0001, 5.0)
PredictionCore.Write()

print 'just created', fnew.GetName()




