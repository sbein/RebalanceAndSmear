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

if not year== 'Run2':
    hCentral = labeledhist.Clone('')
    fCentral = TFile('validation_data'+year+'HDP.root')
    hCentral_ = fCentral.Get('hLowMhtBaseline_SearchBinsRplusS').Clone('hLowMhtBaseline_SearchBinsRplusS_aux')
    for ibin in range(1,xax.GetNbins()+1):
        hCentral.SetBinContent(ibin, hCentral_.GetBinContent(ibin))
        hCentral.SetBinError(ibin, hCentral_.GetBinError(ibin))   
        print ibin, 'setting bin error', hCentral_.GetBinError(ibin)
else:
    fCentral16 = TFile('validation_dataRunPreHem/validation_dataRun2016HDP.root')
    fCentral17 = TFile('validation_dataRunPreHem/validation_dataRun2017HDP.root')
    fCentral18PreHem = TFile('validation_dataRun2018PreHemHDP.root')
    fCentral18DuringHem = TFile('validation_dataRun2018DuringHemHDP.root')    
    
    hCentral16_ = fCentral16.Get('hLowMhtBaseline_SearchBinsRplusS').Clone('hLowMhtBaseline_SearchBinsRplusS_16')
    hCentral = hCentral16_.Clone('')
    hCentral.Reset()
    hCentral17_ = fCentral17.Get('hLowMhtBaseline_SearchBinsRplusS').Clone('hLowMhtBaseline_SearchBinsRplusS_17')    
    hCentral18PH_ = fCentral18PreHem.Get('hLowMhtBaseline_SearchBinsRplusS').Clone('hLowMhtBaseline_SearchBinsRplusS_18')
    hCentral18DH_ = fCentral18DuringHem.Get('hLowMhtBaseline_SearchBinsRplusS').Clone('hLowMhtBaseline_SearchBinsRplusS_18')            
    hCentral.Add(hCentral16_)
    hCentral.Add(hCentral17_)
    hCentral.Add(hCentral18PH_)
    hCentral.Add(hCentral18DH_)    

hStat = hCentral.Clone('hStat')
xax = hStat.GetXaxis()
for ibin in range(1,xax.GetNbins()+1):
    hStat.SetBinContent(ibin, 1+TMath.Sqrt(pow(0.5,2)+pow(hStat.GetBinError(ibin)/hStat.GetBinContent(ibin),2)))
    hCentral.GetXaxis().SetBinLabel(ibin, labeledhist.GetXaxis().GetBinLabel(ibin))
fnew.cd()
hCentral.Write('PredictionCV')


for ibin in range(1, xax.GetNbins()+1): 
    bxwindow = SearchBinWindows[ibin][3]
    print 'bxwindow', bxwindow
    if bxwindow[0]>=2: 
        origerror = hStat.GetBinError(ibin)-1
        newerrr = 0.2
        hStat.SetBinError(ibin, 1+TMath.Sqrt(pow(origerror,2)+pow(newerrr,2)))

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




