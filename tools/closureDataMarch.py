from ROOT import *
from utils import *
from ra2blibs import *
import os,sys
gROOT.SetBatch(1)

#a little cheat sheet for getting the prediction:
# first follow launchClosureData.sh selectively pasting in commands to make the MC and truth information
# then follow StitchUpHemPrediction.py to process the 2018 prediction and observed distributions
# then proceed to the prepareBootstrap.py code and make the predictions even better
# then run this script to do the validation and apply the scale factors
# then run something else to make the integration cards

datamc = 'MC'
datamc = 'Data'

DefinitelyUseMC = True
subtractnonq = False #toggle this on to get njet systematic


try: year = sys.argv[1]
except: year = 'Run2016'

#all for not
aditeescale = 1.0

doit4thesearchbins = False
LowDPhi = False
doit4theprediction = False
useBillsZJets = False
savehistos = True

HalfItMode = False
if HalfItMode:
    anotherBinning = {}
    anotherBinning['SearchBins'] = [87,1,88]
    anotherBinning['SearchBins'] = [87,88,175]


redoBinning = binningAnalysis
if doit4thesearchbins: redoBinning['Mht'] = binningUser['Mht']
else: 
    a = 2
    #redoBinning = binningUser


if LowDPhi: 
    AscertainNorm = True
    label = 'LDP'
else: 
    AscertainNorm = False
    label = 'HDP'

hem_filter = 'Hemv0p5'
fbtagcor = TFile('usefulthings/btagcorrector.root')
hbtagcor = fbtagcor.Get('hBTagCorrection')

ftrigteffs = TFile('usefulthings/newfileTriggerEff.root')
#ftrigteffs.ls()


fnamePredictionAux = ''
if year=='Run2016': 
    lumi = 35900
    fnamePrediction = 'Vault/OutputBootstrapRun2016.root'#'testDumb2016.root'#
    #fnameTruth = 'Vault/OutputBootstrapRun2016.root'#'testDumb2016.root'#
    fnamePredJerUp = 'Vault/Run2016RandS_JerUp.root'

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;1'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;1'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;1'  

    if LowDPhi:
        fnameTruth = 'Vault/MET_LDP_2016.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2016.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2016.root'        
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_190213_Yr2016.root'
    else:
        fnameTruth = 'Vault/MET_signalSideband_2016.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2016.root'	
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2016.root'	        
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_190126_Yr2016.root'	
    hardCodedJobFailureCorrection = 1.02
elif year=='Run2017': 
    lumi = 41500
    fnamePrediction = 'Vault/OutputBootstrapRun2017.root'
    #fnamePrediction = 'testDumb2017.root'##just adding together dumb style

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;2'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;2'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;2'    

    if LowDPhi:
        fnameTruth = 'Vault/MET_LDP_2017.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2017.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2017.root'        
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_190118.root'
    else:
        fnameTruth = 'Vault/MET_signalSideband_2017.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2017.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2017.root'        
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithMHTSidebandPlotsforQCD_190118.root'
    hardCodedJobFailureCorrection = 1.02
elif year=='Run2018': ###this is being phased out
    lumi = 59546.
    fnamePrediction = 'Vault/OutputBootstrapRun2018.root'#'Partial2018Pit/QcdPred2018.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018.root'
    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/Skim_tree_MET_Run2018_LDP.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_Yr2018.root'
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_LowDphi_2018.root'        


    else:
        fnameTruth = 'Vault/Skim_tree_MET_Run2018_signalSideband.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_Yr2018.root' 
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_2018.root' 


    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2018PreHem': 
    lumi = 20919.
    aditeescale = 1.0###aditeescale = lumi/59200
    #fnamePrediction = 'Partial2018Pit/QcdPred2018.root'
    #fnamePredictionAux = 'Vault/OutputBootstrapRun2018.root'
    fnamePrediction = 'Vault/OutputBootstrapRun2018PreHem.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018PreHem.root'#'Vault/OutputBootstrapRun2018PreHem.root'
    fnamePrediction, fnamePredictionAux = 'Vault/OutputBootstrapRun2018PreHem.root', 'Vault/OutputBootstrapRun2018PreHem.root'

    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/Skim_tree_MET_2018_LDPPreHem.root'
        fnameTruth = 'Skim_tree_MET_Run2018PreHem_LDP.root'
        fnameTruth = 'Vault/Skim_tree_MET_Run2018PreHem_LDP.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_PreHEM_Yr2018.root'
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_LowDphi_PreHEM.root'
        #fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_LowDphi_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_190320.root'#march
    else:
        ##fnameTruth = 'Vault/Skim_tree_MET_2018_signalSidebandPreHem.root'
        fnameTruth =       'Skim_tree_MET_Run2018PreHem_signalSideband.root'        
        fnameTruth = 'Vault/Skim_tree_MET_Run2018PreHem_signalSideband.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_PreHEM_Yr2018.root'
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_PreHEM.root'
        #fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_190320.root' ##march #going to save this as something else
    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2018DuringHem': 
    lumi = 38628.
    aditeescale = 1.0### lumi/59200
    fnamePrediction = 'Vault/OutputBootstrapRun2018DuringHem.root'#'Partial2018Pit/QcdPred2018.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018DuringHem.root'#'Vault/OutputBootstrapRun2018DuringHem.root'
    fnameDuringdiction, fnameDuringdictionAux = 'Vault/OutputBootstrapRun2018DuringHem.root', 'Vault/OutputBootstrapRun2018DuringHem.root'

    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/Skim_tree_MET_2018_LDPDuringHem.root'
        fnameTruth = 'Vault/Skim_tree_MET_Run2018DuringHem_LDP.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        ##fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_PostHEM_Yr2018.root'
        #fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_LowDphi_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_PostHEM_190325.root'#march
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_LowDphi_PostHEM.root'#april
    else:
        fnameTruth = 'Vault/Skim_tree_MET_2018_signalSidebandDuringHem.root'
        fnameTruth = 'Vault/Skim_tree_MET_Run2018DuringHem_signalSideband.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        ##fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_PostHEM_Yr2018.root'        
        #fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_PostHEM_190325.root' ##march #will save this as something else
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_Data_MET_Apr16_PostHEM.root'
    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2': 
    lumi = 35900+41500+59546.
    lumi = 137000
    #fnamePrediction = 'testOutputBootsrapRun2.root'#this was the result of a simple hadd of the three independent data periods
    fnamePrediction = 'testOutputBootstrapRun2_v17.root'#here 28 may
    fnamePrediction = 'run2ldptest.root'# just testing a simple hadd 28 may
    
    #fnamePrediction = 'Vault/OutputBootstrapRun2.root'##apr10#'Partial2018Pit/QcdPredRun2.root'
    # fnamePredictionAux = 'testOutputBootsrapRun2.root'#
    fnamePredictionAux = 'testOutputBootstrapRun2_v17.root'# here 28 may #'testOutputBootstrapRun2_v17.root' 
    #fnamePredictionAux = 'Vault/OutputBootstrapRun2.root'#this is a clever file that combines 2018 into a seemless package

    fnamePrediction, fnamePredictionAux = 'Vault/OutputBootstrapRun2.root', 'Vault/OutputBootstrapRun2.root'

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'

    if LowDPhi:
        #fnameTruth = 'Vault/MET_LDP_Run2.root'##orig
        #fnameTruth = 'Partial2018Pit/QcdPredRun2.root'
        fnameTruth = 'Vault/Skim_tree_MET_Run2_LDP.root'##here may 28
        fnameNonQcd = 'Vault/NonQcd_LDP_MCRun2.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MCRun2.root'
        fnameNonQcdZJetsAux___ = 'Vault/ZJetsFromBill.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_190215_CombinedYears.root'
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_haddData_LLHadtauPred_190411_LowDphi_CombinedYears.root'        
    else:
        #fnameTruth = 'Vault/MET_signalSideband_Run2.root'
        #fnameTruth = 'Vault/Skim_tree_MET_2018_LDP.root'
        fnameTruth = 'Vault/Skim_tree_MET_Run2_signalSideband.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MCRun2.root'	
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MCRun2.root'        
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_190213_CombinedYears.root'
        fnameAditee = 'Vault/FromAditeeApril/Prediction_0_haddData_LLHadtauPred_190411_CombinedYears.root'        

    hardCodedJobFailureCorrection = 1.02  



gROOT.ProcessLine(open('src/Met110Mht110FakePho.cpp').read())
exec('from ROOT import *')
#mht, njets = 260, 4
#ht = 2000
#print 'eff(%d,%d,%d)='%(ht,mht,njets), Eff_Met110Mht110FakePho_CenterUpDown(ht, mht, njets)[0]
#exit(0)

tefftriglow = ftrigteffs.Get(fnametriglow)
tefftrigmed = ftrigteffs.Get(fnametrigmed)
tefftrighig = ftrigteffs.Get(fnametrighig)
tax = tefftriglow.GetCopyPassedHisto().GetXaxis()

loadSearchBins2018()
SearchBinWindows = {v: k for k, v in SearchBinNumbers.iteritems()}

fPrediction = TFile(fnamePrediction)
if not fnamePredictionAux=='': 
    fPredictionAux = TFile(fnamePredictionAux)

#####fPredJerUp = TFile(fnamePredJerUp)
fTruth = TFile(fnameTruth)
fNonQcd = TFile(fnameNonQcd)
fNonQcdZJets = TFile(fnameNonQcdZJets)
if useBillsZJets: fNonQcdZJetsAux = TFile(fnameNonQcdZJetsAux___)
fAditee = TFile(fnameAditee)

failfactor = fPrediction.Get('hTotFit').Integral()/fPrediction.Get('hPassFit').Integral()
print 'failfactor', failfactor

#fPrediction.ls()

if AscertainNorm:
    #if 'DuringHem' in year: extra='Hemv30'
    if 'DuringHem' in year: extra=hem_filter
    else: extra = ''        

    pname = 'hLdpLmhtSideband'+extra+'_BTagsRplusS'
    print 'pname', pname
    hPredForNorm = fPrediction.Get(pname).Clone('hPredForNorm')
    hPredForNorm.Scale(failfactor)
    hPredForNorm.Scale(hardCodedJobFailureCorrection)        
    hNonQcdForNorm = fNonQcdZJets.Get('hLdpLmhtSideband'+extra+'_BTagsTruth').Clone('hNonQcdForNorm')
    hNonQcdForNorm.Scale(lumi)
    nnq = hNonQcdForNorm.GetBinContent(hNonQcdForNorm.GetXaxis().FindBin(0.01))
    fad = fAditee.Get('h_NBtag_forQCD_Pre')
    nnq+= aditeescale*fad.GetBinContent(fad.GetXaxis().FindBin(0.01))
    #hNonQcdForNorm.Add(fAditee.Get('h_NBtag_forQCD_Pre'))
    print 'fAditee.GetName()',fAditee.GetName()

    #print 'truthy for norm:', fTruth.Get('hLdpLmhtSideband'+extra+'_BTagsTruth').GetBinContent(1)
    #print 'nonqc for norm:', hNonQcdForNorm.GetBinContent(1)
    print 'predy for norm:', hPredForNorm.GetBinContent(1)
    num = (fTruth.Get('hLdpLmhtSideband'+extra+'_BTagsTruth').GetBinContent(1)-nnq)
    NORM = num/hPredForNorm.GetBinContent(1)
    print 'lumi, num, pred', lumi, num/lumi, hPredForNorm.GetBinContent(1)/lumi 
    print 'aditee/lumi', aditeescale*fad.GetBinContent(fad.GetXaxis().FindBin(0.01))/lumi
    print 'non-qcd-mc/lumi', hNonQcdForNorm.GetBinContent(hNonQcdForNorm.GetXaxis().FindBin(0.01))/lumi
    print 'NORM ascertained from hLdpLmhtSideband_BTags=0 to be', NORM
    #exit(0)
else:#
    if year=='Run2016': 
        NORM = 1.58598045308
        NORM = 1.49073561527
        NORM = 1.44438530324 #Aditee
    elif year=='Run2017': 
        NORM = 1.46180124366
        NORM = 1.39929490286
        NORM = 1.38591543178 # aditee
    elif year=='Run2018': 
        NORM = 1.40013899358#2.79
        NORM = 1.19822978765# Aditee
        NORM = 1.92804595868# that seemed to change, could be failed jobs
    elif year=='Run2018DuringHem': 
        NORM =0.776294319512
        NORM = 1.3319837735## from March run with new HEM veto based on Aditee's thing with lumi scaling
        #NORM = 1.37401936615# March with veto 0p5
        NORM = 1.3823026598
        #NORM = 2.09469783624### this is a strange change that I don't understand yet , 28 May 2019
    elif year=='Run2018PreHem': 
        NORM =0.428048523897     
        NORM = 1.1822855057##Aditee with lumi weighting 
        NORM = 1.17589478163## Aditee with lumi fixed (missing filter on jet response)
        NORM = 1.70607449234# this is after the 2018 MC
    elif year=='Run2': 
        NORM = 1.45137287493
        NORM = 1.30220265066
        NORM = 1.49907095371##final at time of pre-approval
        NORM = 1.56206550324# this is a bit high likely because of a few failed jobs
        NORM = 2.53699355851

#NORM*=1.3
print 'NORM taken to be', NORM
#exit(0)

gStyle.SetOptStat(0)
gROOT.ForceStyle()


def mkLabel(str_,kinvar,selection=''):
    newstr = str_
    if newstr[0]=='h':newstr = newstr[1:]
    newstr = newstr.replace('GenSmeared',' gen-smeared ')
    newstr = newstr.replace('Rebalanced',' rebalanced ')
    newstr = newstr.replace('RplusS','QCD (R&S)')
    if datamc=='Data': newstr = newstr.replace('Truth','Data')
    newstr = newstr.replace('Truth','Run 2017')
    if datamc == 'Data': newstr = newstr.replace('Truth',' Data (2017)')
    newstr = newstr.replace(kinvar,'')
    newstr = newstr.replace('_b','').replace('_','')
    newstr = newstr.replace(selection+' ','')
    return newstr

kinvar = 'Mass'
kinvar = 'Zpt'
kinvar = 'Ht'
kinvar = 'Mht'
def nicelabel(label):
    label_ = label
    label_ = label_.replace('Vs',' vs ')
    label_ = label_.replace('Mht','H_{T}^{miss}')
    label_ = label_.replace('Met','E_{T}^{miss}')
    label_ = label_.replace('Ht','H_{T}')
    label_ = label_.replace('NJets','N_{jets}')
    label_ = label_.replace('BTags','N_{b-jets}')
    label_ = label_.replace('Pt',' p_{T}')
    label_ = label_.replace('Eta',' #eta')
    label_ = label_.replace('SearchBins',' Control region bin number')    
    if 'DPhi' in label_:
        label_ = label_.replace('DPhi','#Delta#phi(H^{miss}_{T}, jet')
        label_ = label_+')'
        numberloc = max(label_.find('1'),label_.find('2'),label_.find('3'),label_.find('4'))+1
        label_ = label_[:numberloc]+', '+label_[numberloc:]
        label_ = label_.replace(', )',')')
    return label_



keys = fPrediction.GetListOfKeys()
keys = sorted(keys,key=lambda thing: thing.GetName())
newfile = TFile('validation_data'+year+label+'.root','recreate')


#for Pair in PairsToCompare:
for key in keys:
    name = key.GetName()
    if not ('RplusS' in name): continue
    if 'Hemv15' in name or 'Hemv30' in name: continue
    if doit4thesearchbins: 
        if 'Sideband' in name: continue
    ###if year=='Run2018DuringHem' and LowDPhi==False and 'hLowMhtSideband' in name:
    ###if not 'Hemv0p7' in name: continue#######this is to compensate for lacking histograms in intermediate run; fix me!

    if year=='Run2':
        if 'Hemv' in name: continue
        if 'MinDeltaPhiHem' in name: continue

    if 'LowDeltaPhi' in name: continue

    #if LowDPhi:
    #	if not ('LowDeltaPhi' in name or 'Ldp' in name): continue
    #else:
    #		if not ('LowMhtSideband' in name or 'hBaseline' in name): continue


    if LowDPhi:
        #if not ('hLdpLmhtBase' in name): continue
        if not ('hLdpLmht' in name): continue        
    else:
        if not ('hLowMht' in name): continue

    #these lines must remain in order to make sure Aditee's histograms are added correctly 


    #if not 'Mht' in key.GetName(): continue
    kinvar = key.GetName().replace('GenSmeared','').replace('Rebalanced','').replace('RplusS','')
    selection = kinvar[1:kinvar.find('_')]
    kinvar = kinvar[kinvar.find('_')+1:]
    if '_' in kinvar: continue

    if 'Max' in kinvar and 'Pt' in kinvar: continue

    print 'kinvar=', kinvar
    if 'RplusS' in key.GetName():
        method = 'RplusS'
        standard = 'Truth'##
        if datamc == 'Data':
            method = 'RplusS'
            standard = 'Truth'##

    hPrediction = fPrediction.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method)
    if doit4theprediction: 
        for ibin in range(1, hPrediction.GetXaxis().GetNbins()+1): hPrediction.SetBinError(ibin, TMath.Sqrt(pow(hPrediction.GetBinError(ibin),2) + pow(.5*hPrediction.GetBinContent(ibin),2)))
    else:
        for ibin in range(1, hPrediction.GetXaxis().GetNbins()+1): hPrediction.SetBinError(ibin, TMath.Sqrt(pow(hPrediction.GetBinError(ibin),2) + pow(.5*hPrediction.GetBinContent(ibin),2) + pow(0.7*hPrediction.GetBinContent(ibin),2) ))


    if kinvar == 'Ht':
        xax = hPrediction.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
            ht = xax.GetBinCenter(ibin)
            mht = 260
            njets = 4
            efforig = Eff_Met110Mht110FakePho_CenterUpDown(ht, mht, njets)[0]
            if ht<800:
                effnewtrig = tefftriglow.GetEfficiency(tax.FindBin(mht))
            elif ht<1700:
                effnewtrig = tefftrigmed.GetEfficiency(tax.FindBin(mht))
            else:
                effnewtrig = tefftrighig.GetEfficiency(tax.FindBin(mht))
            correctionweight = effnewtrig/efforig
            origcontent = hPrediction.GetBinContent(ibin)
            origerror = hPrediction.GetBinError(ibin)
            hPrediction.SetBinContent(ibin, correctionweight*origcontent)
            hPrediction.SetBinError(ibin, correctionweight*origerror)            
            print ibin, ht, 'correcting content by', correctionweight
            #exit(0)

    if kinvar == 'BTags':
        xax = hPrediction.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
            continue
            btags = xax.GetBinLowEdge(ibin)
            if not btags>2: continue
            correctionweight = 2
            origcontent = hPrediction.GetBinContent(ibin)
            origerror = hPrediction.GetBinError(ibin)
            hPrediction.SetBinContent(ibin, correctionweight*origcontent)
            hPrediction.SetBinError(ibin, TMath.Sqrt(pow(correctionweight*origerror,2)+pow(0.5*correctionweight*origcontent,2)))            
            print ibin, btags, 'correcting content by', correctionweight
            #exit(0)            



    hPrediction.Scale(failfactor)
    hPrediction.Scale(hardCodedJobFailureCorrection)
    #hPredUp = fPredJerUp.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method)
    #UpMySyst(hPrediction, hPredUp)
    hPrediction.SetTitle('QCD (R&S)')


    #if 'DuringHem' in year: extra='Hemv30'
    if 'DuringHem' in year and False: extra=hem_filter
    else: extra = ''
    tname = 'h'+selection+extra+'_'+kinvar+standard
    print 'getting truth', tname, 'from', fTruth.GetName()
    hTruth = fTruth.Get(tname).Clone('h'+selection+'_'+kinvar+standard)
    spacedyear = year.replace('Run', 'Run ')
    hTruth.SetTitle(spacedyear+' observed')
    if 'DuringHem' in year: extra=hem_filter

    hNonQcdBackup = fNonQcd.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard)
    hNonQcdBackup.Scale(lumi)
    hNonQcd = fNonQcdZJets.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard)
    for ibin in range(1, hNonQcd.GetXaxis().GetNbins()+1): hNonQcd.SetBinError(ibin, TMath.Sqrt(pow(hNonQcd.GetBinError(ibin),2) + pow(0.3*hNonQcd.GetBinContent(ibin),2)))
    hNonQcd.Scale(lumi)

    if useBillsZJets and kinvar=='SearchBins':
        hname2grab = 'h'+selection+'_'+kinvar+standard
        print 'hname2grab', hname2grab
        hzbill = fNonQcdZJetsAux.Get(hname2grab).Clone('h'+selection+'_'+kinvar+standard)
        xaxb = hzbill.GetXaxis()
        xaxnq = hNonQcd.GetXaxis()
        for ibin in range(1, xaxb.GetNbins()+1):
            print 'setting bin', ibin, 'to', hzbill.GetBinContent(ibin)
            
            hNonQcd.SetBinContent(xaxnq.FindBin(ibin), hzbill.GetBinContent(ibin))
            hNonQcd.SetBinError(xaxnq.FindBin(ibin), hzbill.GetBinError(ibin))            
        
            
    hNonQcd.SetLineColor(kOrange)

    '''
    if kinvar == 'BTags':
        print 'selection', selection
        print 'truth name name:', hTruth.GetName()
        print 'truthy for norm:', hTruth.GetBinContent(1)
        print 'nonqc for norm:', hNonQcdForNorm.GetBinContent(1)
        print 'predy for norm:', hPredForNorm.GetBinContent(1)
        pause()
    '''
    hPrediction.Scale(NORM)

    hname2add = ''
    if LowDPhi: doSideband = ''              
    else: doSideband = '_forQCD' 

    if doit4thesearchbins: doSideband = '_forQCD' #########always doing sideband

    if kinvar == 'Ht': hname2add = 'h_HT'+doSideband+'_Pre'
    if kinvar == 'NJets': hname2add = 'h_NJet'+doSideband+'_Pre'
    if kinvar == 'BTags': hname2add = 'h_NBtag'+doSideband+'_Pre'
    if kinvar == 'Mht': hname2add = 'h_MHT'+doSideband+'_Pre'
    if kinvar == 'SearchBins': hname2add = 'h_Prediction'



    if hname2add == '':
        lostleptonlabel = 'W#rightarrow l#nu'
    else:
        lostleptonlabel = 'Lost-lepton/had. #tau'        
        print 'going for', hname2add, 'from', fAditee.GetName()
        hAditee = fAditee.Get(hname2add)
        hAditee.Scale(aditeescale)
        if kinvar=='SearchBins' and not 'Sideband' in selection:
            if (not fnamePredictionAux==''):
                hpname = 'h'+selection+'_'+kinvar+method
                print 'hpname', hpname, 'from', fPredictionAux.GetName()
                hPrediction = fPredictionAux.Get(hpname).Clone('h'+selection+'_'+kinvar+method)
                hPrediction.SetTitle('QCD (R&S)')
                hPrediction.Scale(failfactor*hardCodedJobFailureCorrection*NORM)

                for ibin in range(1, hPrediction.GetXaxis().GetNbins()+1): 
                    hPrediction.SetBinError(ibin, TMath.Sqrt(pow(hPrediction.GetBinError(ibin),2) + pow(0.5*hPrediction.GetBinContent(ibin),2))) 
                    if not doit4theprediction: hPrediction.SetBinError(ibin, TMath.Sqrt(pow(hPrediction.GetBinError(ibin),2) +pow(0.7*hPrediction.GetBinContent(ibin),2)  + pow(0.3*hPrediction.GetBinContent(ibin),2) ))
            hstat = fAditee.Get('h_CSStat')
            xaxa = hAditee.GetXaxis()
            for ibin in range(1, xaxa.GetNbins()+1):
                hAditee.SetBinError(ibin, abs(hstat.GetBinContent(ibin)-hAditee.GetBinContent(ibin)))

            newbinning = []
            stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
            for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
            nbins = len(newbinning)-1
            newxs = array('d',newbinning)
            hTruth = hTruth.Rebin(nbins,'',newxs)
            if kinvar=='SearchBins': 
                print kinvar, 'before all is said and done, aditees histogram has', xaxa.GetNbins(), xaxa.GetBinLowEdge(1), xaxa.GetBinUpEdge(xaxa.GetNbins())
                print 'rebinning', kinvar, newxs

            hAditeeAux = hTruth.Clone('h2addrebinned')
            hAditeeAux.Reset()
            xax = hAditeeAux.GetXaxis()
            for ibin in range(1, xax.GetNbins()+1):
                #print ibin, 'setting aditees bin number', ibin, 'located at', xaxa.GetBinCenter(ibin), 'to', hAditee.GetBinContent(ibin), 'with center', hAditeeAux.GetXaxis().GetBinCenter(ibin)
                hAditeeAux.SetBinContent(ibin, hAditee.GetBinContent(ibin))
                hAditeeAux.SetBinError(ibin, hAditee.GetBinError(ibin))
                hAditeeAux.SetBinError(ibin, TMath.Sqrt(pow(hAditee.GetBinError(ibin),2) + pow(0.3*hAditee.GetBinContent(ibin),2)))
            hAditee = hAditeeAux

    hNonQcd.SetTitle(lostleptonlabel+', Z#rightarrow #nu#nu')


    if kinvar == 'SearchBins':####
        xax = hPrediction.GetXaxis()
        print 'this prediction histo has dimensions', xax.GetNbins(), xax.GetBinLowEdge(1), xax.GetBinUpEdge(xax.GetNbins())
        for ibin in range(1, xax.GetNbins()+1): 
            ibinAnalysis = xax.GetBinLowEdge(ibin)
            if ibinAnalysis>174: continue
            #ibinAnalysis = ibin
            windows = SearchBinWindows[ibinAnalysis]
            #ht = 0.5*(windows[0][0]+windows[0][1])
            ht = windows[0][1]
            #if ht>3000: ht = windows[0][0]
            mht = 0.5*(windows[1][0]+windows[1][1])
            njets = 4
            #njets = windows[2][1]
            efforig = Eff_Met110Mht110FakePho_CenterUpDown(ht, mht, njets)[0]
            if ht<800:
                effnewtrig = tefftriglow.GetEfficiency(tax.FindBin(mht))
            elif ht<1700:
                effnewtrig = tefftrigmed.GetEfficiency(tax.FindBin(mht))
            else:
                effnewtrig =  max(tefftriglow.GetEfficiency(tax.FindBin(min(mht,999))), max(tefftrighig.GetEfficiency(tax.FindBin(min(mht,999))) ,tefftrigmed.GetEfficiency(tax.FindBin(min(mht,999)))))
                #effnewtrig =  tefftrighig.GetEfficiency(tax.FindBin(mht))
            correctionweight = max(1.0,effnewtrig/efforig)
            #correctionweight = effnewtrig/efforig
            origcontent = hPrediction.GetBinContent(ibin)
            origerror = hPrediction.GetBinError(ibin)
            #if year!='Run2016':
            hPrediction.SetBinContent(ibin, correctionweight*origcontent)
            hPrediction.SetBinError(ibin, correctionweight*origerror)            
            print ibin, ht, 'correct by', correctionweight, '(',ht,') old', efforig, 'new:', effnewtrig, 'bincenter', xax.GetBinCenter(ibin), 'anal', ibinAnalysis
            bhigh = windows[3][1]
            blow = windows[3][0]+1
            jhigh = windows[2][1]
            if jhigh<6:
                correctionweight = hbtagcor.GetBinContent(hbtagcor.GetXaxis().FindBin(blow))
                origcontent = hPrediction.GetBinContent(ibin)
                origerror = hPrediction.GetBinError(ibin)
                hPrediction.SetBinContent(ibin, correctionweight*origcontent)
                #print 'correcting low njet, btags', blow, correctionweight
                if doit4theprediction: 
                    hPrediction.SetBinError(ibin, TMath.Sqrt(pow(correctionweight*origerror,2)+pow(0.2*hPrediction.GetBinContent(ibin),2)))
                else:
                    hPrediction.SetBinError(ibin, TMath.Sqrt(pow(correctionweight*origerror,2)+pow(abs(1-correctionweight)*hPrediction.GetBinContent(ibin),2)))

    if kinvar == 'BTags':####
        xax = hPrediction.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1): 
            continue
            correctionweight = hbtagcor.GetBinContent(hbtagcor.GetXaxis().FindBin(ibin))
            origcontent = hPrediction.GetBinContent(ibin)
            origerror = hPrediction.GetBinError(ibin)
            hPrediction.SetBinContent(ibin, correctionweight*origcontent)
            hPrediction.SetBinError(ibin, correctionweight*origerror)


            #exit(0)            


    if subtractnonq: hTruth.Add(hNonQcd,-1)
    if datamc == 'Data': col = kGreen
    if datamc == 'MC': col = kBlue
    histoStyler(hTruth, 1)
    histoStyler(hPrediction, kGray+1)
    hPrediction.SetFillColor(col-5)
    hPrediction.SetFillStyle(1002)
    hNonQcd.SetFillStyle(1002)
    hNonQcd.SetFillColor(hNonQcd.GetLineColor())    



    cGold = mkcanvas('cEnchilada')
    print 'kinvar', kinvar, hname2add
    if len(redoBinning[kinvar])>3: ##this should be reinstated
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hTruth = hTruth.Rebin(nbins,'',newxs)
        hPrediction = hPrediction.Rebin(nbins,'',newxs)
        hNonQcd = hNonQcd.Rebin(nbins,'',newxs)
        hNonQcdBackup = hNonQcdBackup.Rebin(nbins,'',newxs)
        if  hname2add!='' and kinvar != 'SearchBins': 
            #fAditee.ls()
            hAditee = hAditee.Rebin(nbins,'',newxs)
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hTruth = hTruth.Rebin(nbins,'',newxs)
        if kinvar=='SearchBins': print 'before 1', hPrediction.GetBinContent(1)   
        if kinvar=='SearchBins': print 'bin at 1', hPrediction.GetBinContent(hPrediction.GetXaxis().FindBin(1.5))                    
        if kinvar=='SearchBins': print 'before 174', hPrediction.GetBinContent(174)        
        if kinvar=='SearchBins': print 'bin at 174', hPrediction.GetBinContent(hPrediction.GetXaxis().FindBin(174.5))                                
        hPrediction = hPrediction.Rebin(nbins,'',newxs)
        if kinvar=='SearchBins': print 'before 1', hPrediction.GetBinContent(1)                
        if kinvar=='SearchBins': print 'after at 1', hPrediction.GetBinContent(hPrediction.GetXaxis().FindBin(1.5))            
        if kinvar=='SearchBins': print 'after 174', hPrediction.GetBinContent(174)     
        if kinvar=='SearchBins': print 'bin at 174', hPrediction.GetBinContent(hPrediction.GetXaxis().FindBin(174.5))                                           
        hNonQcd = hNonQcd.Rebin(nbins,'',newxs)
        hNonQcdBackup = hNonQcdBackup.Rebin(nbins,'',newxs)
        if  hname2add!='' and kinvar != 'SearchBins': 
            hAditee = hAditee.Rebin(nbins,'',newxs)


    if hname2add=='':
        xax = hNonQcd.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
                hNonQcd.SetBinContent(ibin, hNonQcdBackup.GetBinContent(ibin))
                hNonQcd.SetBinError(ibin, hNonQcdBackup.GetBinError(ibin))        
    else:
        #print 'adding', hNonQcd.GetName(), hAditee.GetName()# might be nice to double check that these are compatible
        hNonQcd.Add(hAditee)###
        xax = hAditee.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
            if hAditee.GetBinContent(ibin)==0 or DefinitelyUseMC:
                print ibin, 'using MC contingency'
                hNonQcd.SetBinContent(ibin, hNonQcdBackup.GetBinContent(ibin))
        #pause()

    '''
    hTruth.Write(hTruth.GetName()+'_truth')
    hNonQcd.Write(hNonQcd.GetName()+'_nonqcd')
    hPrediction.Write(hPrediction.GetName()+'_rands')
    '''
    #hPrediction.Write()
    for ibin in range(1, hNonQcd.GetXaxis().GetNbins()+1): hNonQcd.SetBinError(ibin, TMath.Sqrt(pow(hNonQcd.GetBinError(ibin),2) + pow(0.3*hNonQcd.GetBinContent(ibin),2)))

    print key.GetName()
    hpure = hPrediction.Clone(hPrediction.GetName()+'pure')
    htot = hpure.Clone()
    htot.Add(hNonQcd)
    hpure.Divide(htot)
    hpure.SetLineColor(kViolet+2)
    hpure.SetFillStyle(0)

    leg = mklegend(x1=.405, y1=.53, x2=.90, y2=.77, color=kWhite)
    hInferredQcd = hTruth.Clone('hInferredQcd')
    hInferredQcd.Add(hNonQcd,-1)
    hReallyhNonQcd = hNonQcd.Clone('hReallyhNonQcd')

    if HalfItMode and kinvar=='SearchBins':
            if len(anotherBinning[kinvar])>3: ##this should be reinstated
                nbins = len(anotherBinning[kinvar])-1
                newxs = array('d',anotherBinning[kinvar])
                hTruth = hTruth.Rebin(nbins,'',newxs)
                hPrediction = hPrediction.Rebin(nbins,'',newxs)
                hNonQcd = hNonQcd.Rebin(nbins,'',newxs)
                hNonQcdBackup = hNonQcdBackup.Rebin(nbins,'',newxs)
                if  hname2add!='' and kinvar != 'SearchBins': 
                    hAditee = hAditee.Rebin(nbins,'',newxs)
            else:
                newbinning = []
                stepsize = round(1.0*(anotherBinning[kinvar][2]-anotherBinning[kinvar][1])/anotherBinning[kinvar][0],4)
                for ibin in range(anotherBinning[kinvar][0]+1): newbinning.append(anotherBinning[kinvar][1]+ibin*stepsize)
                nbins = len(newbinning)-1
                newxs = array('d',newbinning)
                hTruth = hTruth.Rebin(nbins,'',newxs)
                hPrediction = hPrediction.Rebin(nbins,'',newxs)
                hNonQcd = hNonQcd.Rebin(nbins,'',newxs)
                hNonQcdBackup = hNonQcdBackup.Rebin(nbins,'',newxs)                

    if subtractnonq: hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')
    else: 
        print 'hNonQcd.Integral()', hNonQcd.Integral()
        #pause()
        #hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction,hNonQcd],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='obs./predicted')
        hrat, stuff, pad1, pad2 = FabDrawSystyRatio(cGold,leg,hTruth,[hPrediction,hNonQcd],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='obs./predicted')
    hrat.GetYaxis().SetRangeUser(-0.2,2.2)
    if year=='Run2018DuringHem' and 'Mht' in key.GetName(): hrat.GetYaxis().SetRangeUser(-0.8,4.2)
    hrat.GetXaxis().SetTitle(nicelabel(kinvar))
    hrat.SetLineColor(kBlack)
    for ibin in range(1,hrat.GetXaxis().GetNbins()+1):
        if hrat.GetBinContent(ibin)==0: hrat.SetBinContent(ibin, -20)

    pad1.cd()
    hTruth.Draw("same e")
    pad2.cd()
    leg2 = mklegend(x1=.46, y1=.295, x2=.8805, y2=.42)
    ###leg2.AddEntry(hpure, 'QCD-purity','l')
    if 'SearchBins' in kinvar: 
        #pad2.SetLogy()
        #hrat.GetYaxis().SetRangeUser(0.11,9)
        hrat.GetYaxis().SetRangeUser(-0.3, 3.9)
    ###hpure.Draw('hist same')

    leg2.Draw()
    #if kinvar=='NJets': hrat.Fit('pol1','s','')
    cGold.Update()   

    cname = (hPrediction.GetName()+'_And_'+hTruth.GetName()).replace(' ','')#.replace(extra,'')
    cGold.Write(cname)
    if savehistos:
        hNonQcd.Write(hPrediction.GetName()+'_full')
        hNonQcd.Add(hPrediction,-1)        
        hNonQcd.Write(hPrediction.GetName()+'_nonqcd')
        hTruth.Write()
    if subtractnonq and key.GetName()=='hLdpLmhtSideband_NJetsRplusS':
        print 'activating thingy'
        hrat.Write('hRatio_LdpLmhtSideband_RplusSAndTruth_NJets')
    if doit4thesearchbins: continue
    cGold.Print('pdfs/validation/'+selection+'_'+method+'And'+standard+'_'+kinvar+year+'.pdf')


print 'just created', newfile.GetName()
