#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *
import os, sys

try: year = sys.argv[1]
except: year = 'Run2016'
redoBinning = binningAnalysis
labelfilename = 'Vault/QcdPredictionSUS-16-033.root'
labelfile = TFile(labelfilename)
labeledhist = labelfile.Get('PredictionCV')
labeledhist.Reset()
xax = labeledhist.GetXaxis()

fnew = TFile('QcdPrediction'+year+'.root','recreate')
loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}
redoBinning = binningAnalysis


fCentral = TFile('OutputBootstrap'+year+'.root')
hCentral_ = fCentral.Get('hBaseline_SearchBinsRplusS').Clone('hBaseline_SearchBinsRplusS_aux')
hCentral = labeledhist.Clone('')
for ibin in range(1,xax.GetNbins()+1):
    hCentral.SetBinContent(ibin, hCentral_.GetBinContent(ibin))
    hCentral.SetBinError(ibin, hCentral_.GetBinError(ibin))    

hStat = hCentral.Clone('hStat')
xax = hStat.GetXaxis()
for ibin in range(1,xax.GetNbins()+1):
    hStat.SetBinContent(ibin, 1+TMath.Sqrt(pow(0.5,2)+pow(hStat.GetBinError(ibin)/hStat.GetBinContent(ibin),2)))

fnew.cd()
hCentral.Write('PredictionCV')
hStat.Write('PredictionUncorrelated')
#fCentral.Close()


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


hSyst_tail = hStat.Clone('hSyst_tail')
for ibin in range(1,xax.GetNbins()+1):
    hSyst_tail.SetBinContent(ibin, 1.3)
fnew.cd()
for ibin in range(1,xax.GetNbins()+1):
    hSyst_tail.GetXaxis().SetBinLabel(ibin, 'QCDTail')
hSyst_tail.Write('PredictionTail')

fJerNom = TFile('Vault/Run2017RandS_JerNom.root')
fJerUp = TFile('Vault/Run2017RandS_JerUp.root')
fJerUp.ls()
hUp = fJerUp.Get('hBaseline_SearchBinsRplusS')
hNom = fJerNom.Get('hBaseline_SearchBinsRplusS')
kinvar = 'SearchBins'
if len(redoBinning[kinvar])>3: ##this should be reinstated
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

PredictionCore = hUp.Clone('PredictionCore')
PredictionCore.Reset()
xax = hUp.GetXaxis()
countNom = {}
countUp = {}
for ibin in range(1, xax.GetNbins()+1): 
    countkey = SearchBinWindows[ibin][:2]    
    if not countkey in countNom.keys(): 
        countNom[countkey] = 0
        countUp[countkey] = 0
    countNom[countkey] += hNom.GetBinContent(ibin)
    countUp[countkey] += hUp.GetBinContent(ibin)        
for ibin in range(1, xax.GetNbins()+1): 
    countkey = SearchBinWindows[ibin][:2]
    PredictionCore.SetBinContent(ibin, countUp[countkey]/countNom[countkey])

for ibin in range(1,xax.GetNbins()+1):
    PredictionCore.GetXaxis().SetBinLabel(ibin, 'QCDCore')
    
fnew.cd()
PredictionCore.Write()

print 'just created', fnew.GetName()




