from ROOT import *
from utils import *
from ra2blibs import *
import os,sys
gROOT.SetBatch(1)

datamc = 'MC'
datamc = 'Data'

DefinitelyUseMC = False
subtractnonq = False #toggle this on to get njet systematic

try: year = sys.argv[1]
except: year = 'Run2016'

#all for not
truthscale = 1.0

LowDPhi = True

if LowDPhi: 
    AscertainNorm = True
    label = 'LDP'
else: 
    AscertainNorm = False
    label = 'HDP'


ftrigteffs = TFile('usefulthings/newfileTriggerEff.root')
ftrigteffs.ls()


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
elif year=='Run2018': 
    lumi = 59200
    fnamePrediction = 'Partial2018Pit/QcdPred2018.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018.root'
    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/MET_LDP_2018.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_Yr2018.root'
    else:
        fnameTruth = 'Vault/MET_signalSideband_2018.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_Yr2018.root'        
    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2018PreHem': 
    lumi = 21077
    fnamePrediction = 'Partial2018Pit/QcdPred2018.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018.root'
    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/Skim_tree_MET_2018_LDPPreHem.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_PreHEM_Yr2018.root'
        #fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_190320.root'#march
    else:
        fnameTruth = 'Vault/Skim_tree_MET_2018_signalSidebandPreHem.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_PreHEM_Yr2018.root'
        #fnameAditee = 'Vault/FromAditeeMarch/Prediction_0_haddData_LLHadtauPred_WithWidenedHEMvetoForJetsWithDphiPt5Cut_1L_190320.root' ##march #going to save this as something else
    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2018PostHem': 
    lumi = 38846
    fnamePrediction = 'Partial2018Pit/QcdPred2018.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2018.root'
    fnamePredJerUp = 'Vault/Run2018RandS_JerUp.root'
    print 'fnamePrediction', fnamePrediction

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'
    if LowDPhi:
        fnameTruth = 'Vault/Skim_tree_MET_2018_LDPDuringHem.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MC2018.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_WithTF2017_190220_UpdatedcsvWP_PostHEM_Yr2018.root'
    else:
        fnameTruth = 'Vault/Skim_tree_MET_2018_signalSidebandDuringHem.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MC2018.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MC2018.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_WithTF2017_190220_UpdatedcsvWP_PostHEM_Yr2018.root'        
    hardCodedJobFailureCorrection = 1.02   
elif year=='Run2': 
    lumi = 35900+41500+59200
    fnamePrediction = 'Partial2018Pit/QcdPredRun2.root'
    fnamePredictionAux = 'Vault/OutputBootstrapRun2.root'

    fnametriglow = 'tEffhMetMhtFakeHt300to800XMht;3'
    fnametrigmed = 'tEffhMetMhtFakeHt800to1700XMht;3'
    fnametrighig = 'tEffhMetMhtFakeHt1700toInfXMht;3'

    if LowDPhi:
        fnameTruth = 'Vault/MET_LDP_Run2.root'
        #fnameTruth = 'Partial2018Pit/QcdPredRun2.root'
        fnameNonQcd = 'Vault/NonQcd_LDP_MCRun2.root'
        fnameNonQcdZJets = 'Vault/NonQcdZJets_LDP_MCRun2.root'
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_LowDphi_190215_CombinedYears.root'
    else:
        fnameTruth = 'Vault/MET_signalSideband_Run2.root'
        fnameNonQcd = 'Vault/NonQcd_signalSideband_MCRun2.root'	
        fnameNonQcdZJets = 'Vault/NonQcdZJets_signalSideband_MCRun2.root'        
        fnameAditee = 'Vault/FromAditee/Prediction_0_haddData_LLHadtauPred_190213_CombinedYears.root'
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
redoBinning = binningAnalysis
#redoBinning = binningUser


additionalHelperScale = 1.0
fPrediction = TFile(fnamePrediction)
if not fnamePredictionAux=='': 
    fPredictionAux = TFile(fnamePredictionAux)
    if not year=='Run2':
        fPredictionBig = TFile('Partial2018Pit/BigPredthingy.root')
        additionalHelperScale = fPredictionBig.Get('hTotFit').Integral()/fPrediction.Get('hTotFit').Integral()
        fPredictionBig.Close()
        print 'additionalHelperScale', additionalHelperScale

#####fPredJerUp = TFile(fnamePredJerUp)
fTruth = TFile(fnameTruth)
fNonQcd = TFile(fnameNonQcd)
fNonQcdZJets = TFile(fnameNonQcdZJets)
fAditee = TFile(fnameAditee)

failfactor = fPrediction.Get('hTotFit').Integral()/fPrediction.Get('hPassFit').Integral()
print 'failfactor', failfactor

if AscertainNorm:
    hPredForNorm = fPrediction.Get('hLdpLmhtSideband_BTagsRplusS').Clone('hPredForNorm')
    hPredForNorm.Scale(failfactor)
    hPredForNorm.Scale(hardCodedJobFailureCorrection)        
    hPredForNorm.Scale(additionalHelperScale)
    hNonQcdForNorm = fNonQcdZJets.Get('hLdpLmhtSideband_BTagsTruth').Clone('hNonQcdForNorm')
    hNonQcdForNorm.Scale(lumi)
    hNonQcdForNorm.Add(fAditee.Get('h_NBtag_forQCD_Pre'))
    if 'PostHem' in year: extra='Hemv30'
    else: extra = ''
    print 'truthy name', 'hLdpLmhtSideband'+extra+'_BTagsTruth' 
    print 'truthy for norm:', fTruth.Get('hLdpLmhtSideband'+extra+'_BTagsTruth').GetBinContent(1)
    print 'nonqc for norm:', hNonQcdForNorm.GetBinContent(1)
    print 'predy for norm:', hPredForNorm.GetBinContent(1)
    num = (fTruth.Get('hLdpLmhtSideband'+extra+'_BTagsTruth').GetBinContent(1)-hNonQcdForNorm.GetBinContent(1))
    NORM = num/hPredForNorm.GetBinContent(1)
    print 'NORM ascertained from hLdpLmhtSideband_BTags=0 to be', NORM
    #exit(0)

else:
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
    elif year=='Run2018PostHem': 
        NORM =0.776294319512
    elif year=='Run2018PreHem': 
        NORM =0.428048523897        
    elif year=='Run2': 
        NORM = 1.45137287493
        NORM = 1.30220265066

print 'NORM taken to be', NORM

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

def UpMySyst(hmain, halt):
    xax = hmain.GetXaxis()
    for ibin in range(1,xax.GetNbins()+1):
        oldunc = hmain.GetBinError(ibin)
        addunc = halt.GetBinError(ibin)
        hmain.SetBinError(ibin, TMath.Sqrt(pow(oldunc,2)+pow(addunc,2)))

#for Pair in PairsToCompare:
for key in keys:
    name = key.GetName()
    if not ('RplusS' in name): continue
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

    print 'kinvarrrr', kinvar
    if not (year=='Run2018' or year=='Run2018PostHem') and 'Max' in kinvar and 'Pt' in kinvar: 
        print 'here we are', kinvar
        continue 
        print 'changing', kinvar
        kinvar = kinvar.replace('MaxForwardPt','MaxHemJetPt')

    print 'kinvar=', kinvar
    if 'RplusS' in key.GetName():
        method = 'RplusS'
        standard = 'Truth'##
        if datamc == 'Data':
            method = 'RplusS'
            standard = 'Truth'##

    hPrediction = fPrediction.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')


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



    hPrediction.Scale(failfactor)
    hPrediction.Scale(hardCodedJobFailureCorrection)
    hPrediction.Scale(additionalHelperScale)
    #hPredUp = fPredJerUp.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    #UpMySyst(hPrediction, hPredUp)
    hPrediction.SetTitle('QCD (R&S)')


    if 'PostHem' in year: extra='Hemv30'
    else: extra = ''
    tname = 'h'+selection+extra+'_'+kinvar+standard
    if 'PostHem' in year: tname = tname.replace('Baseline','Base')
    print 'getting truth', tname
    hTruth = fTruth.Get(tname).Clone('h'+selection+'_'+kinvar+standard+'')
    hTruth.Scale(truthscale)
    spacedyear = year.replace('Run', 'Run ')
    hTruth.SetTitle(spacedyear+' observed')

    hNonQcdBackup = fNonQcd.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hNonQcdBackup.Scale(lumi)
    hNonQcd = fNonQcdZJets.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hNonQcd.Scale(lumi)
    hNonQcd.SetLineColor(38)

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

    if kinvar == 'Ht': hname2add = 'h_HT'+doSideband+'_Pre'
    if kinvar == 'NJets': hname2add = 'h_NJet'+doSideband+'_Pre'
    if kinvar == 'BTags': hname2add = 'h_NBtag'+doSideband+'_Pre'
    if kinvar == 'Mht': hname2add = 'h_MHT'+doSideband+'_Pre'
    if kinvar == 'SearchBins': hname2add = 'h_Prediction'



    if hname2add == '':
        lostleptonlabel = 'W#rightarrow l#nu'
    else:
        lostleptonlabel = 'Lost-lepton/had. #tau'        
        hAditee = fAditee.Get(hname2add)
        if kinvar=='SearchBins' and not 'Sideband' in selection:
            if (not fnamePredictionAux==''):
                hPrediction = fPredictionAux.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
                hPrediction.Scale(failfactor*hardCodedJobFailureCorrection*NORM)
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
            hAditeeAux = hTruth.Clone('h2addrebinned')
            hAditeeAux.Reset()
            xax = hAditeeAux.GetXaxis()
            for ibin in range(1, xax.GetNbins()+1):
                hAditeeAux.SetBinContent(ibin, hAditee.GetBinContent(ibin))
                hAditeeAux.SetBinError(ibin, hAditee.GetBinError(ibin))
            hAditee = hAditeeAux
            
    hNonQcd.SetTitle(lostleptonlabel+', Z#rightarrow #nu#nu MC')


    if kinvar == 'SearchBins':####
        xax = hPrediction.GetXaxis()

        for ibin in range(1, xax.GetNbins()+1): 
            windows = SearchBinWindows[ibin]
            ht = 0.5*(windows[0][0]+windows[0][1])
            mht = 0.5*(windows[1][0]+windows[1][1])
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
        if not hname2add=='': 
            fAditee.ls()
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
        if not hname2add=='': hAditee = hAditee.Rebin(nbins,'',newxs)


    if hname2add=='':
        xax = hNonQcd.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
                hNonQcd.SetBinContent(ibin, hNonQcdBackup.GetBinContent(ibin))
                hNonQcd.SetBinError(ibin, hNonQcdBackup.GetBinError(ibin))        
    else:
        hNonQcd.Add(hAditee)
        xax = hAditee.GetXaxis()
        for ibin in range(1, xax.GetNbins()+1):
            if hAditee.GetBinContent(ibin)==0 or DefinitelyUseMC:
                hNonQcd.SetBinContent(ibin, hNonQcdBackup.GetBinContent(ibin))

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
    if subtractnonq: hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')
    else: 
        print 'hNonQcd.Integral()', hNonQcd.Integral()
        #pause()
        hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction,hNonQcd],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')
    hrat.GetYaxis().SetRangeUser(-0.4,2.4)
    if year=='Run2018PostHem' and 'Mht' in key.GetName(): hrat.GetYaxis().SetRangeUser(-0.8,4.2)
    hrat.GetXaxis().SetTitle(kinvar)
    hrat.SetLineColor(kBlack)

    pad1.cd()
    hTruth.Draw("same e")

    if 'PostHem' in year:
        tname = tname.replace(extra,'')
        if (not LowDPhi) and (not 'Hemv' in tname): tname = tname.replace('Base','Baseline')
        if (not LowDPhi) and ('Hemv' in tname): tname = tname.replace('Baseline','Base')            
        hTruthBadHem = fTruth.Get(tname)
        print tname.replace(extra,'')
        hTruthBadHem.SetLineColor(kRed)
        hTruthBadHem = hTruthBadHem.Rebin(nbins,'',newxs)
        hTruthBadHem.SetMarkerStyle(hTruth.GetMarkerStyle())
        hTruthBadHem.SetMarkerColor(kRed)
        hTruthBadHem.Draw('same')
        leg.AddEntry(hTruthBadHem, 'observed (no HEM veto)','l')

    pad2.cd()
    leg2 = mklegend(x1=.46, y1=.295, x2=.8805, y2=.42)
    leg2.AddEntry(hpure, 'QCD-purity','l')
    if 'SearchBins' in kinvar: 
        #pad2.SetLogy()##commented/replaced in april
        #hrat.GetYaxis().SetRangeUser(0.11,9)##commented/replaced in april
        hrat.GetYaxis().SetRangeUser(-0.3, 2.3)
    hpure.Draw('hist same')


    if 'PostHem' in year and 'Mht' in key.GetName():
            hBadHemRatio = hTruthBadHem.Clone('hBadHemRatio')
            hBadHemRatio.Add(hReallyhNonQcd,-1)
            hBadHemRatio.Divide(hInferredQcd)
            pad2.cd()
            hBadHemRatio.Draw('same')
            leg2.AddEntry(hBadHemRatio, 'QCD without veto/QCD w. veto','l')

    leg2.Draw()
    #if kinvar=='NJets': hrat.Fit('pol1','s','')
    cGold.Update()   

    cname = (hPrediction.GetName()+'_And_'+hTruth.GetName()).replace(' ','')#.replace(extra,'')
    cGold.Write(cname)
    hPrediction.Write()	
    if subtractnonq and key.GetName()=='hLdpLmhtSideband_NJetsRplusS':
        print 'activating thingy'
        hrat.Write('hRatio_LdpLmhtSideband_RplusSAndTruth_NJets')
    cGold.Print('pdfs/validation/'+selection+'_'+method+'And'+standard+'_'+kinvar+year+'.pdf')


print 'just created', newfile.GetName()
