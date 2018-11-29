#! /usr/bin/env python
# script to create trees with track variables
# created May 3, 2017 -Sam Bein 

#python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_30.root

from ROOT import *
from utils import *
import os, sys
csv_b = 0.8484
csv_b = 0.8838# new with CMSSW_9

##########################################################
# files specified with optional wildcards @ command line #
##########################################################
try: fnamekeyword = sys.argv[1]
except: 
    fnamekeyword = 'Summer16.SMS-T1tttt_mGluino-1200_mLSP-800'
    #Run2016B-03Feb2017_ver2-v2.SingleElectron
    #Run2017C-31Mar2018-v1.SingleElectron
    #infilenames = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV15/Run2016B-17Jul2018_ver1-v1.SingleElectron_0_RA2AnalysisTree.root'

if 'Summer16' in fnamekeyword: 
    ntupleV = '14'
    isdata = False
elif 'V15a' in fnamekeyword or 'RelVal' in fnamekeyword:
    ntupleV = '15a'
    isdata = False
else: 
    ntupleV = '15'
    isdata = True
if 'Run2016' in fnamekeyword: ntupleV = '14'
if 'Run2017' in fnamekeyword: ntupleV = '15'
if 'Run2018' in fnamekeyword: ntupleV = '15'


#############################################
# Book new file in which to write skim tree #
#############################################
newfilename = ('skim_'+(fnamekeyword.split('/')[-1]).replace('*','')+'.root').replace('.root.root','.root')
fnew = TFile(newfilename,'recreate')
hHt = TH1F('hHt','hHt',100,0,3000)
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',100,0,3000)
histoStyler(hHt,kBlack)

########################################
# create data containers for the trees #
########################################
import numpy as np
var_Met = np.zeros(1,dtype=float)

var_HtJet2p4 = np.zeros(1,dtype=float)
var_HtCentrality = np.zeros(1,dtype=float)
var_MhtJet2p4 = np.zeros(1,dtype=float)
var_NJetsJet2p4 = np.zeros(1,dtype=int)
var_MinDeltaPhiJetsMhtJet2p4 = np.zeros(1,dtype=float)
var_PassesDeltaPhiJet2p4 = np.zeros(1,dtype=int)


var_HtJet5p0 = np.zeros(1,dtype=float)
var_MhtJet5p0 = np.zeros(1,dtype=float)
var_NJetsJet5p0 = np.zeros(1,dtype=int)
var_MinDeltaPhiJetsMhtJet5p0 = np.zeros(1,dtype=float)
var_PassesDeltaPhiJet5p0 = np.zeros(1,dtype=int)

var_MinDeltaPhiJetsMhtJet2016 = np.zeros(1,dtype=float)
var_PassesDeltaPhiJet2016 = np.zeros(1,dtype=int)

var_BTags = np.zeros(1,dtype=int)
var_NLeptons = np.zeros(1,dtype=int)
var_NPhotons = np.zeros(1,dtype=int)

var_CrossSection = np.zeros(1,dtype=float)
var_GenMet = np.zeros(1,dtype=float)
var_GenMetPhi = np.zeros(1,dtype=float)

if isdata:
    var_PassesTrigMetMht6pack = np.zeros(1,dtype=int)
    var_PassesTrigSingleEl = np.zeros(1,dtype=int)
    var_PassesTrigSinglePho = np.zeros(1,dtype=int)
    var_PassesTrigSingleMu = np.zeros(1,dtype=int)    
#####################################################
# declare tree and associate branches to containers #
#####################################################
tEvent = TTree('tEvent','tEvent')
tEvent.Branch('Met', var_Met,'Met/D')
tEvent.Branch('HtCentrality', var_HtCentrality,'HtCentrality/D')##
tEvent.Branch('HtJet2p4', var_HtJet2p4,'HtJet2p4/D')
tEvent.Branch('HtJet5p0', var_HtJet5p0,'HtJet5p0/D')
tEvent.Branch('MhtJet2p4', var_MhtJet2p4,'MhtJet2p4/D')
tEvent.Branch('MhtJet5p0', var_MhtJet5p0,'MhtJet5p0/D')
tEvent.Branch('NJetsJet2p4', var_NJetsJet2p4,'NJetsJet2p4/I')
tEvent.Branch('NJetsJet5p0', var_NJetsJet5p0,'NJetsJet5p0/I')
tEvent.Branch('MinDeltaPhiJetsMhtJet2p4', var_MinDeltaPhiJetsMhtJet2p4,'MinDeltaPhiJetsMhtJet2p4/D')
tEvent.Branch('MinDeltaPhiJetsMhtJet5p0', var_MinDeltaPhiJetsMhtJet5p0,'MinDeltaPhiJetsMhtJet5p0/D')
tEvent.Branch('PassesDeltaPhiJet2p4', var_PassesDeltaPhiJet2p4,'PassesDeltaPhiJet2p4/I')
tEvent.Branch('PassesDeltaPhiJet5p0', var_PassesDeltaPhiJet5p0,'PassesDeltaPhiJet5p0/I')

tEvent.Branch('MinDeltaPhiJetsMhtJet2016', var_MinDeltaPhiJetsMhtJet2016,'MinDeltaPhiJetsMhtJet2016/D')
tEvent.Branch('PassesDeltaPhiJet2016', var_PassesDeltaPhiJet2016,'PassesDeltaPhiJet2016/I')

tEvent.Branch('BTags', var_BTags,'BTags/I')
tEvent.Branch('NLeptons', var_NLeptons,'NLeptons/I')
tEvent.Branch('NPhotons', var_NPhotons,'NPhotons/I')
tEvent.Branch('CrossSection', var_CrossSection,'CrossSection/D')
tEvent.Branch('GenMetPhi', var_GenMetPhi,'GenMetPhi/D')
tEvent.Branch('GenMet', var_GenMet,'GenMet/D')
if isdata:
    tEvent.Branch('PassesTrigMetMht6pack', var_PassesTrigMetMht6pack,'PassesTrigMetMht6pack/I')
    tEvent.Branch('PassesTrigSingleEl', var_PassesTrigSingleEl,'PassesTrigSingleEl/I')    
    tEvent.Branch('PassesTrigSingleMu', var_PassesTrigSingleMu,'PassesTrigSingleMu/I')
    tEvent.Branch('PassesTrigSinglePho', var_PassesTrigSinglePho,'PassesTrigSinglePho/I')    

#################
# Load in chain #
#################
fnamefile = open('usefulthings/filelistV'+ntupleV+'.txt')
lines = fnamefile.readlines()
fnamefile.close()

c = TChain('TreeMaker2/PreSelection')
filelist = []
for line in lines:
    shortfname = fnamekeyword.split('/')[-1]
    if not shortfname in line: continue
    fname = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV'+ntupleV+'/'+line#RelValQCD_FlatPt
    fname = fname.strip().replace('/eos/uscms/','root://cmsxrootd.fnal.gov//')
    print 'adding', fname
    c.Add(fname)
    filelist.append(fname)
    break


    
###########################
# a few utility functions #
###########################

triggerIndecesV15 = {}
triggerIndecesV15['SingleElPlane'] = [36,39]
triggerIndecesV15['SingleEl'] = [21, 23, 28, 35, 40, 41]
triggerIndecesV15['MhtMet6pack'] = [108, 110, 114, 124, 126, 129, 122, 134, 131, 133, 116, 118]
triggerIndecesV15["SingleMu"] = [48, 50, 52, 53, 55, 63]
triggerIndecesV15["SinglePho"] = [139]
triggerIndecesV15['Ht'] = [68, 69, 72, 73, 74, 80, 84, 88, 91, 92, 93, 95, 96, 99, 102, 103, 104]

triggerIndecesV14 = {}
triggerIndecesV14['SingleEl'] = [19]
triggerIndecesV14['MhtMet6pack'] = [56, 53, 54, 55, 60, 57, 58, 59]
triggerIndecesV14["SingleMu"] = [24, 25, 26, 27, 28]
triggerIndecesV14["SinglePho"] = [63]
triggerIndecesV14['Ht'] = [19]

if ntupleV=='15': triggerIndeces = triggerIndecesV15
if ntupleV=='15a': triggerIndeces = triggerIndecesV15
if ntupleV=='14': triggerIndeces = triggerIndecesV14


def PassTrig(c,trigname):
    for trigidx in triggerIndeces[trigname]: 
        if c.TriggerPass[trigidx]==1: return True
    return False

def SelectCommonData(c):
    if c.JetID==1 and c.globalTightHalo2016Filter==1 and c.HBHENoiseFilter==1 and c.HBHEIsoNoiseFilter==1 and c.eeBadScFilter==1 and c.EcalDeadCellTriggerPrimitiveFilter==1 and c.BadChargedCandidateFilter and c.BadPFMuonFilter and c.NVtx > 0 and c.PFCaloMETRatio<5: return True
    else: return False

def SelectCommonMC(c):
    if c.JetID==1 and c.BadPFMuonFilter and c.NVtx > 0 and c.PFCaloMETRatio<5: return True
    else: return False  

def SelectCommonMC15a(c):
    if c.JetID==1 and c.NVtx > 0 and c.PFCaloMETRatio<5: return True
    else: return False          
        
def SelectCrSel(c):
    if not (c.NMuons==0 and c.NElectrons==1 and c.isoMuonTracksclean==0 and c.isoPionTracksclean==0): return False
    if not (c.MHT>120 and c.Electrons[0].Pt()>30 and c.Electrons_passIso[0] and c.Electrons_tightID[0] and c.HT>300): return False #this
    else: return True
def SelectCrSpho(c):
    if not(len(c.Photons_nonPrompt)==0 and len(c.Photons_fullID)==1 and len(c.Photons)==1 and c.NMuons==0 and c.NElectrons==0 and c.isoElectronTracksclean==0 and c.isoMuonTracksclean==0 and c.isoPionTracksclean==0): return False
    if not (c.Photons[0].Pt()>210 and c.MHT>120): return False
    return True
def SelectCrSelOrSpho(c):
    return SelectCrSel(c) or SelectCrSpho(c)
def SelectCrSmu(c):
    if not (c.NMuons==1): return False
    if not (len(c.NElectrons)>0 or len(c.NPhotons)>0): return False
    return True
def SelectCrZee(c):
    if not(c.NMuons==0 and c.NElectrons==2 and c.isoMuonTracksclean==0 and c.isoPionTracksclean==0): return False
    return True
def SelectCrZmm(c):
    if not(c.NElectrons==0 and c.NMuons==2 and c.isoElectronTracksclean==0 and c.isoPionTracksclean==0): return False
    return True     
def SelectCrHt(c):
    if not(c.NMuons==0 and c.NElectrons==0 and c.isoMuonTracksclean==0 and c.isoPionTracksclean==0 and c.NElectrons==0 and c.NMuons==0 and c.isoElectronTracksclean==0): return False
    if not (c.MHT>120 and c.HT>300): return False
    return True
def SelectLooseBaseline(c):
    if not(c.NElectrons==0 and c.NMuons==0 and c.isoElectronTracksclean==0 and c.isoPionTracksclean==0 and c.isoMuonTracksclean==0 and c.MHT>250 and c.MET>250): return False
    return True     
def AlwaysTrue(c):
    return True

print 'filelist[0]', filelist[0]

if isdata: SelectCommon = SelectCommonData
else:  SelectCommon = SelectCommonMC
if ntupleV=='15a': 
    SelectCommon=SelectCommonMC15a
    RegionSelection = SelectLooseBaseline
if 'SingleElectron' in filelist[0]: RegionSelection = SelectCrSel
if 'SingleMuon' in filelist[0]: RegionSelection = SelectCrSmu
if 'SinglePhoton' in filelist[0]: RegionSelection = SelectCrSpho
if 'EGamma' in filelist[0]: RegionSelection = SelectCrSelOrSpho
if 'JetHT' in filelist[0]: RegionSelection = SelectCrHt
if 'MET' in filelist[0]: RegionSelection = SelectLooseBaseline
if 'Summer16' in filelist[0]: RegionSelection = SelectLooseBaseline

c.Show(0)
nentries = c.GetEntries()
print 'will analyze', nentries

verbosity = 10000

for ientry in range(nentries):

    c.GetEntry(ientry)

    if ientry%verbosity==0: 
        print 'analyzing event %d of %d' % (ientry, nentries)+ '....%f'%(100.*ientry/nentries)+'%'
        if ientry==0: 
            for itrig, trigname in enumerate(c.TriggerNames):
                print itrig, trigname, c.TriggerPass[itrig], c.TriggerPrescales[itrig]
                
    weight = 1#c.CrossSection
    hHt.Fill(c.HT)
    hHtWeighted.Fill(c.HT, weight)
    
    if not isdata:
        if 'TTJets_TuneCUET' in fnamekeyword:
         if not c.madHT<600: continue
        if 'TTJets_HT' in fnamekeyword:
            if not c.madHT>600: continue  
        if 'WJetsToLNu_TuneCUET' in fnamekeyword:
            if not c.madHT<100: continue
        elif 'WJetsToLNu_HT' in fnamekeyword:
         if not c.madHT>100: continue  	           
    
    #if not len(c.Muons)>0: continue###
    
    if not SelectCommon(c): continue
    if not isdata: extraallowance = c.GenMET>150
    else: extraallowance = False
    if not (RegionSelection(c) or extraallowance): continue

    var_Met[0] = c.MET

    bjets = []

    
    mhtvec_jet2p4 = TLorentzVector()   
    mhtvec_jet2p4.SetPxPyPzE(0,0,0,0)
    jets_jet2p4 = []
    ht_jet2p4 = 0        

    mhtvec_jet5p0 = TLorentzVector()
    mhtvec_jet5p0.SetPxPyPzE(0,0,0,0)    
    jets_jet5p0 = []
    ht_jet5p0 = 0 


    ht_jet1p5 = 0     

    for ijet, jet in enumerate(c.Jets):
        if not jet.Pt()>30: continue
        #rawpt = jet.Pt()/c.Jets_jecFactor[ijet]
        #if not isdata: rawpt*=1./c.Jets_jerFactor[ijet]
        #if (rawpt<75 and abs(jet.Eta())>2.65 and abs(jet.Eta())<3.139): continue        
        if not abs(jet.Eta())<5.0: continue
        jets_jet5p0.append(jet)
        mhtvec_jet5p0-=jet        
        ht_jet5p0+=jet.Pt()        
        if not abs(jet.Eta())<2.4: continue
        jets_jet2p4.append(jet)        
        mhtvec_jet2p4-=jet
        ht_jet2p4+=jet.Pt()
        if c.Jets_bDiscriminatorCSV[ijet]>csv_b: bjets.append(jet)
        if abs(jet.Eta())<1.5: ht_jet1p5+=jet.Pt()

    '''ht_jet2p4
    if abs(mhtvec_jet5p0.Pt()-c.MHT)>1: 
        print '='*100
        print '%f!=%f (%f)' % (mhtvec_jet5p0.Pt(), c.MHT, mhtvec_jet2p4.Pt())
        for thing in c.Electrons: print 'ele', thing.Pt(), thing.Eta()
        for thing in c.Muons: print 'muon', thing.Pt(), thing.Eta()
        for thing in c.Photons: print 'photon', thing.Pt(), thing.Eta()
        print '='*100            
    else:  
        print 'consistent MHTs'
        for thing in c.Electrons: print 'ele', thing.Pt(), thing.Eta()
        for thing in c.Muons: print 'muon', thing.Pt(), thing.Eta()
        for thing in c.Photons: print 'photon', thing.Pt(), thing.Eta() 
    '''

    if not len(jets_jet5p0)>0: continue

    
    mindphi_jet2p4 = 9999
    mindphi_jet2016 = 9999
    for jet in jets_jet2p4[:4]: 
        mindphi_jet2p4 = min(mindphi_jet2p4,abs(jet.DeltaPhi(mhtvec_jet2p4)))
        mindphi_jet2016 = min(mindphi_jet2016,abs(jet.DeltaPhi(mhtvec_jet5p0)))
    var_MinDeltaPhiJetsMhtJet2p4[0] = mindphi_jet2p4
    var_MinDeltaPhiJetsMhtJet2016[0] = mindphi_jet2016
    mindphi_jet5p0 = 9999        
    for jet in jets_jet5p0[:4]: mindphi_jet5p0 = min(mindphi_jet5p0,abs(jet.DeltaPhi(mhtvec_jet5p0)))
    var_MinDeltaPhiJetsMhtJet5p0[0] = mindphi_jet5p0        

    if ht_jet2p4>0: var_HtCentrality[0] = ht_jet1p5/ht_jet2p4
    else: var_HtCentrality[0] = 0
    var_HtJet2p4[0] = ht_jet2p4
    var_HtJet5p0[0] = ht_jet5p0    
    var_MhtJet2p4[0] = mhtvec_jet2p4.Pt()    
    var_MhtJet5p0[0] = mhtvec_jet5p0.Pt()
    var_NJetsJet2p4[0] = len(jets_jet2p4)
    var_NJetsJet5p0[0] = len(jets_jet5p0)    
    var_BTags[0] = len(bjets)
    var_NLeptons[0] = c.NElectrons+c.NMuons
    var_NPhotons[0] = len(c.Photons)
    if isdata:
        var_PassesTrigMetMht6pack[0] = PassTrig(c, 'MhtMet6pack')
        var_PassesTrigSingleEl[0] = PassTrig(c, 'SingleEl')
        var_PassesTrigSingleMu[0] = PassTrig(c, 'SingleMu')
        var_PassesTrigSinglePho[0] = PassTrig(c, 'SinglePho')  

    
    if len(jets_jet2p4)>0: 
        var_PassesDeltaPhiJet2p4[0] = (abs(jets_jet2p4[0].DeltaPhi(mhtvec_jet2p4))>0.5)
        var_PassesDeltaPhiJet2016[0] = (abs(jets_jet2p4[0].DeltaPhi(mhtvec_jet5p0))>0.5)
    if len(jets_jet2p4)>1: 
        var_PassesDeltaPhiJet2p4[0]*= (abs(jets_jet2p4[1].DeltaPhi(mhtvec_jet2p4))>0.5)
        var_PassesDeltaPhiJet2016[0]*= (abs(jets_jet2p4[1].DeltaPhi(mhtvec_jet5p0))>0.5)
    if len(jets_jet2p4)>2: 
        var_PassesDeltaPhiJet2p4[0]*= (abs(jets_jet2p4[2].DeltaPhi(mhtvec_jet2p4))>0.3)
        var_PassesDeltaPhiJet2016[0]*= (abs(jets_jet2p4[2].DeltaPhi(mhtvec_jet5p0))>0.3)        
    if len(jets_jet2p4)>3: 
        var_PassesDeltaPhiJet2p4[0]*= (abs(jets_jet2p4[3].DeltaPhi(mhtvec_jet2p4))>0.3)
        var_PassesDeltaPhiJet2016[0]*= (abs(jets_jet2p4[3].DeltaPhi(mhtvec_jet5p0))>0.3)        
        
    if len(jets_jet5p0)>0: var_PassesDeltaPhiJet5p0[0] = (abs(jets_jet5p0[0].DeltaPhi(mhtvec_jet5p0))>0.5)
    if len(jets_jet5p0)>1: var_PassesDeltaPhiJet5p0[0]*= (abs(jets_jet5p0[1].DeltaPhi(mhtvec_jet5p0))>0.5)
    if len(jets_jet5p0)>2: var_PassesDeltaPhiJet5p0[0]*= (abs(jets_jet5p0[2].DeltaPhi(mhtvec_jet5p0))>0.3)
    if len(jets_jet5p0)>3: var_PassesDeltaPhiJet5p0[0]*= (abs(jets_jet5p0[3].DeltaPhi(mhtvec_jet5p0))>0.3)        

    try: 
        var_CrossSection[0] = c.CrossSection
        var_GenMet[0] = c.GenMET
        var_GenMetPhi[0] = c.GenMETPhi            
    except: pass
    

    tEvent.Fill()

fnew.cd()
tEvent.Write()
print 'just created', fnew.GetName()
hHt.Write()
hHtWeighted.Write()
fnew.Close()


'''V15
[21, 23, 28, 35, 40, 41]
0 HLT_AK8DiPFJet250_200_TrimMass30_v -1 1
1 HLT_AK8DiPFJet280_200_TrimMass30_v -1 1
2 HLT_AK8DiPFJet300_200_TrimMass30_v -1 1
3 HLT_AK8PFHT700_TrimR0p1PT0p03Mass50_v -1 1
4 HLT_AK8PFHT800_TrimMass50_v 0 1
5 HLT_AK8PFHT850_TrimMass50_v 0 1
6 HLT_AK8PFHT900_TrimMass50_v 0 1
7 HLT_AK8PFJet360_TrimMass30_v 0 1
8 HLT_AK8PFJet400_TrimMass30_v 0 1
9 HLT_AK8PFJet420_TrimMass30_v 0 1
10 HLT_AK8PFJet450_v 0 7
11 HLT_AK8PFJet500_v 0 1
12 HLT_AK8PFJet550_v 0 1
13 HLT_CaloJet500_NoJetID_v 0 1
14 HLT_CaloJet550_NoJetID_v 0 1
15 HLT_DiCentralPFJet55_PFMET110_v -1 1
16 HLT_DiPFJet40_DEta3p5_MJJ600_PFMETNoMu140_v -1 1
17 HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_DZ_PFHT350_v 0 1
18 HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT300_v -1 1
19 HLT_DoubleMu8_Mass8_PFHT300_v -1 1
20 HLT_DoubleMu8_Mass8_PFHT350_v 0 1
21 HLT_Ele105_CaloIdVT_GsfTrkIdT_v -1 1 ##############
22 HLT_Ele115_CaloIdVT_GsfTrkIdT_v 0 1
23 HLT_Ele135_CaloIdVT_GsfTrkIdT_v 0 1 ##############
24 HLT_Ele145_CaloIdVT_GsfTrkIdT_v 0 1
25 HLT_Ele15_IsoVVVL_PFHT350_PFMET50_v -1 1
26 HLT_Ele15_IsoVVVL_PFHT350_v -1 1
27 HLT_Ele15_IsoVVVL_PFHT400_v -1 1
28 HLT_Ele15_IsoVVVL_PFHT450_CaloBTagCSV_4p5_v 0 1  ##############
29 HLT_Ele15_IsoVVVL_PFHT450_PFMET50_v 0 1
30 HLT_Ele15_IsoVVVL_PFHT450_v 0 1
31 HLT_Ele15_IsoVVVL_PFHT600_v 0 1
32 HLT_Ele20_WPLoose_Gsf_v 0 0
33 HLT_Ele20_eta2p1_WPLoose_Gsf_v 0 0
34 HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v 0 1  ##############
35 HLT_Ele25_eta2p1_WPTight_Gsf_v -1 1
36 HLT_Ele27_WPTight_Gsf_v 1 1
37 HLT_Ele27_eta2p1_WPLoose_Gsf_v -1 1
38 HLT_Ele28_eta2p1_WPTight_Gsf_HT150_v 0 1
39 HLT_Ele32_WPTight_Gsf_v -1 1
40 HLT_Ele35_WPTight_Gsf_v 1 1   ##############
41 HLT_Ele45_WPLoose_Gsf_v -1 1   ##############
42 HLT_Ele50_IsoVVVL_PFHT400_v -1 1
43 HLT_Ele50_IsoVVVL_PFHT450_v 0 1
44 HLT_IsoMu16_eta2p1_MET30_v -1 1
45 HLT_IsoMu20_v 0 2
46 HLT_IsoMu22_eta2p1_v -1 1
47 HLT_IsoMu22_v -1 1
48 HLT_IsoMu24_eta2p1_v 0 1
49 HLT_IsoMu24_v 0 1
50 HLT_IsoMu27_v 0 1
51 HLT_IsoTkMu22_v -1 1
52 HLT_IsoTkMu24_v -1 1
53 HLT_Mu15_IsoVVVL_PFHT350_PFMET50_v -1 1
54 HLT_Mu15_IsoVVVL_PFHT350_v -1 1
55 HLT_Mu15_IsoVVVL_PFHT400_v -1 1
56 HLT_Mu15_IsoVVVL_PFHT450_CaloBTagCSV_4p5_v 0 1
57 HLT_Mu15_IsoVVVL_PFHT450_PFMET50_v 0 1
58 HLT_Mu15_IsoVVVL_PFHT450_v 0 1
59 HLT_Mu15_IsoVVVL_PFHT600_v 0 1
60 HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v 0 17
61 HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v -1 1
62 HLT_Mu45_eta2p1_v -1 1
63 HLT_Mu50_IsoVVVL_PFHT400_v -1 1
64 HLT_Mu50_IsoVVVL_PFHT450_v 0 1
65 HLT_Mu50_v 0 1
66 HLT_Mu55_v -1 1
67 HLT_PFHT1050_v 0 1
68 HLT_PFHT200_v -1 1
69 HLT_PFHT250_v 0 8
70 HLT_PFHT300_PFMET100_v -1 1
71 HLT_PFHT300_PFMET110_v -1 1
72 HLT_PFHT300_v -1 1
73 HLT_PFHT350_v 0 208
74 HLT_PFHT370_v 0 7
75 HLT_PFHT380_SixPFJet32_DoublePFBTagCSV_2p2_v 0 1
76 HLT_PFHT380_SixPFJet32_DoublePFBTagDeepCSV_2p2_v -1 1
77 HLT_PFHT380_SixPFJet32_v 0 18
78 HLT_PFHT400_SixJet30_DoubleBTagCSV_p056_v -1 1
79 HLT_PFHT400_SixJet30_v -1 1
80 HLT_PFHT400_v -1 1
81 HLT_PFHT430_SixJet40_BTagCSV_p056_v -1 1
82 HLT_PFHT430_SixPFJet40_PFBTagCSV_1p5_v 0 1
83 HLT_PFHT430_SixPFJet40_v 0 10
84 HLT_PFHT430_v 0 6
85 HLT_PFHT450_SixJet40_BTagCSV_p056_v -1 1
86 HLT_PFHT450_SixJet40_v -1 1
87 HLT_PFHT450_SixPFJet40_PFBTagCSV_1p5_v -1 1
88 HLT_PFHT475_v -1 1
89 HLT_PFHT500_PFMET100_PFMHT100_IDTight_v 0 1
90 HLT_PFHT500_PFMET110_PFMHT110_IDTight_v 0 1
91 HLT_PFHT510_v 0 190
92 HLT_PFHT590_v 0 102
93 HLT_PFHT600_v -1 1
94 HLT_PFHT650_WideJetMJJ900DEtaJJ1p5_v -1 1
95 HLT_PFHT650_v -1 1
96 HLT_PFHT680_v 0 56
97 HLT_PFHT700_PFMET85_PFMHT85_IDTight_v 0 1
98 HLT_PFHT700_PFMET95_PFMHT95_IDTight_v 0 1
99 HLT_PFHT780_v 0 30
100 HLT_PFHT800_PFMET75_PFMHT75_IDTight_v 0 1
101 HLT_PFHT800_PFMET85_PFMHT85_IDTight_v 0 1
102 HLT_PFHT800_v -1 1
103 HLT_PFHT890_v 0 17
104 HLT_PFHT900_v -1 1
105 HLT_PFJet500_v 0 1
106 HLT_PFJet550_v 0 1
107 HLT_PFMET100_PFMHT100_IDTight_PFHT60_v -1 1
108 HLT_PFMET100_PFMHT100_IDTight_v -1 1
109 HLT_PFMET110_PFMHT110_IDTight_PFHT60_v -1 1
110 HLT_PFMET110_PFMHT110_IDTight_v 0 105
111 HLT_PFMET120_PFMHT120_IDTight_HFCleaned_v 0 1
112 HLT_PFMET120_PFMHT120_IDTight_PFHT60_HFCleaned_v 0 1
113 HLT_PFMET120_PFMHT120_IDTight_PFHT60_v 0 1
114 HLT_PFMET120_PFMHT120_IDTight_v 0 1
115 HLT_PFMET130_PFMHT130_IDTight_PFHT60_v -1 1
116 HLT_PFMET130_PFMHT130_IDTight_v 0 1
117 HLT_PFMET140_PFMHT140_IDTight_PFHT60_v -1 1
118 HLT_PFMET140_PFMHT140_IDTight_v 0 1
119 HLT_PFMET500_PFMHT500_IDTight_CalBTagCSV_3p1_v -1 1
120 HLT_PFMET700_PFMHT700_IDTight_CalBTagCSV_3p1_v -1 1
121 HLT_PFMET800_PFMHT800_IDTight_CalBTagCSV_3p1_v -1 1
122 HLT_PFMET90_PFMHT90_IDTight_v -1 1
123 HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60_v -1 1
124 HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_v -1 1
125 HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_PFHT60_v -1 1
126 HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_v 0 107
127 HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_HFCleaned_v 0 1
128 HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_v 0 1
129 HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_v 0 1
130 HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_PFHT60_v -1 1
131 HLT_PFMETNoMu130_PFMHTNoMu130_IDTight_v 0 1
132 HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_PFHT60_v -1 1
133 HLT_PFMETNoMu140_PFMHTNoMu140_IDTight_v 0 1
134 HLT_PFMETNoMu90_PFMHTNoMu90_IDTight_v -1 1
135 HLT_Photon135_PFMET100_v -1 1
136 HLT_Photon165_HE10_v -1 1
137 HLT_Photon165_R9Id90_HE10_IsoM_v 0 2
138 HLT_Photon175_v 0 42
139 HLT_Photon200_v 0 1
140 HLT_Photon300_NoHE_v 0 1
141 HLT_Photon90_CaloIdL_PFHT500_v -1 1
142 HLT_Photon90_CaloIdL_PFHT600_v -1 1
143 HLT_Photon90_CaloIdL_PFHT700_v -1 1
144 HLT_TkMu100_v 0 1
145 HLT_TkMu50_v -1 1


 rgs_SMS-T2tt_mStop-250_mLSP-50_TuneCUETP8M1_Ra2bCutsJetProp1MinDPhi.root  trees
hists   oldscripts    sammysays                                                                 trees_idealjets
jobs    output        temp.sh                                                                   usefulthings
-bash-4.1$ python tools/rgs_analyze.py rgs_SMS-T2tt_mStop-250_mLSP-50_TuneCUETP8M1_Ra2bCutsJetProp1MinDPhi.root


'''
