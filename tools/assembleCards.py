#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *
import os, sys

try: year = sys.argv[1]
except: year = 'Run2016'


#if year=='Run2016': NORM = 1.48 #these come from closureData.root!!!!
#elif year=='Run2017': NORM = 1.41
#elif year=='Run2018': NORM = 2.79

        
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

hCentral = labeledhist.Clone('')
if not year== 'Run2':
    fCentral = TFile('validation_data'+year+'.root')#these validation files must be HDP!!!! would be good to change their names as decided in closureData.py to reflect this
    hCentral_ = fCentral.Get('hBaseline_SearchBinsRplusS').Clone('hBaseline_SearchBinsRplusS_aux')
    for ibin in range(1,xax.GetNbins()+1):
        hCentral.SetBinContent(ibin, hCentral_.GetBinContent(ibin))
        hCentral.SetBinError(ibin, hCentral_.GetBinError(ibin))   
else:
    fCentral16 = TFile('validation_dataRun2016.root')
    fCentral17 = TFile('validation_dataRun2017.root')
    fCentral18 = TFile('validation_dataRun2018.root')        
    hCentral16_ = fCentral16.Get('hBaseline_SearchBinsRplusS').Clone('hBaseline_SearchBinsRplusS_16')
    hCentral17_ = fCentral17.Get('hBaseline_SearchBinsRplusS').Clone('hBaseline_SearchBinsRplusS_17')    
    hCentral18_ = fCentral18.Get('hBaseline_SearchBinsRplusS').Clone('hBaseline_SearchBinsRplusS_18')        
    hCentral.Add(hCentral16_)
    hCentral.Add(hCentral17_)
    hCentral.Add(hCentral18_)        

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




