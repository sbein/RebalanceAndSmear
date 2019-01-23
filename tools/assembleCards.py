#Vault/data-validation-correction.root
from ROOT import *
from utils import *
from ra2blibs import *

redoBinning = binningAnalysis
fnew = TFile('QcdPrediction2017.root','recreate')
loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}
redoBinning = binningAnalysis


fCentral = TFile('OutputBoostrapRun2017.root')
hCentral = fCentral.Get('hBaseline_SearchBinsRplusS')
hStat = hCentral.Clone('hStat')
xax = hStat.GetXaxis()
for ibin in range(1,xax.GetNbins()+1):
    hStat.SetBinContent(ibin, 1+TMath.Sqrt(pow(0.3,2)+pow(hStat.GetBinError(ibin)/hStat.GetBinContent(ibin),2)))

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
    
fnew.cd()
PredictionNJet.Write('PredictionNJet')
#fnjetsyst.Close()


hSyst_tail = hSyst_njet.Clone('hSyst_tail')
for ibin in range(1,xax.GetNbins()+1):
    hSyst_tail.SetBinContent(ibin, 1.3)
fnew.cd()
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

PredictionCoreUp = hUp.Clone('PredictionCoreUp')
PredictionCoreUp.Reset()
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
    PredictionCoreUp.SetBinContent(ibin, countUp[countkey]/countNom[countkey])

fnew.cd()
PredictionCoreUp.Write()

print 'just created', fnew.GetName()




