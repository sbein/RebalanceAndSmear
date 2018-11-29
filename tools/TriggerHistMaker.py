#! /usr/bin/env python
# script to create trees with track variables
# created May 3, 2017 -Sam Bein 

#python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_30.root

from ROOT import *
from utils import *
import os, sys
gROOT.SetBatch(1)
csv_b = 0.8484
csv_b = 0.8838# new with CMSSW_9

##########################################################
# files specified with optional wildcards @ command line #
##########################################################
try: fnamekeyword = sys.argv[1]
except: 
    fnamekeyword = 'Run2017C-31Mar2018-v1.SingleElectron'
    #Run2016B-03Feb2017_ver2-v2.SingleElectron
    #Summer16.SMS-T1tttt_mGluino-1200_mLSP-800
    #infilenames = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV15/Run2016B-17Jul2018_ver1-v1.SingleElectron_0_RA2AnalysisTree.root'

if 'Summer16' in fnamekeyword: 
    ntupleV = '14'
    isdata = False
else: isdata = True
if 'Run2016' in fnamekeyword: ntupleV = '14'
if 'Run2017' in fnamekeyword: ntupleV = '15'
if 'Run2018' in fnamekeyword: ntupleV = '15'


#############################################
# Book new file in which to write skim tree #
#############################################
newfilename = ('hists_'+(fnamekeyword.split('/')[-1]).replace('*','')+'.root').replace('.root.root','.root')
fnew = TFile(newfilename,'recreate')
hHt = TH1F('hHt','hHt',100,0,3000)

########################################
# create data containers for the trees #
########################################
import numpy as np
var_Met = np.zeros(1,dtype=float)

#################
# Load in chain #
#################
fnamefile = open('usefulthings/filelistV'+ntupleV+'.txt')
lines = fnamefile.readlines()
fnamefile.close()

c = TChain('TreeMaker2/PreSelection')
filelist = []
for line in lines:
    if not fnamekeyword in line: continue
    fname = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV'+ntupleV+'/'+line
    fname = fname.strip().replace('/eos/uscms/','root://cmsxrootd.fnal.gov//')
    print 'adding', fname
    c.Add(fname)
    filelist.append(fname)
    break
c.Show(0)
c.GetEntry(0)
for itrig in range(len(c.TriggerPass)): print itrig, c.TriggerNames[itrig], c.TriggerPass[itrig], c.TriggerPrescales[itrig]
###########################
# a few utility functions #
###########################

triggerIndecesV15 = {}
triggerIndecesV15['SingleEl'] = [36,39]
triggerIndecesV15['SingleEl45'] = [41]
triggerIndecesV15['SingleElCocktail'] = [21,22,23,24,26,27,30,31,32,33,36,37,40,139]
triggerIndecesV15['MhtMet6pack'] = [108,110,114,123,124,125,126,128,129,130,131,132,133,122,134]#123
triggerIndecesV15["SingleMu"] = [48,50,52,55,63]
triggerIndecesV15["SingleMuCocktail"] = [45,46,47,48,49,50,51,52,54,55,58,59,63,64,65,66]
triggerIndecesV15["SinglePho"] = [139]
triggerIndecesV15["SinglePhoWithHt"] = [138, 139,141,142,143]
triggerIndecesV15['HtTrain'] = [67,68,69,72,73,74,80,84,88,91,92,93,95,96,99,102,103,104]
#triggerIndecesV15['HtTrain'] = [3,4,5,6,7,8,9]

triggerIndecesV14 = {}
triggerIndecesV14['SingleEl'] = [19]
triggerIndecesV14['SingleEl45'] = [21]
triggerIndecesV14['SingleElCocktail'] = [11,12,14,15,16,18,19,20,21,22,63,64,65]
triggerIndecesV14['MhtMet6pack'] = [56,53,54,55,60,57,58,59]
triggerIndecesV14["SingleMu"] = [23,24,25,26,27]
triggerIndecesV14["SingleMuCocktail"] = [23,24,25,26,27,28,29,30,31,32]
triggerIndecesV14["SinglePho"] = [63]
triggerIndecesV14["SinglePhoWithHt"] = [63,64,65,66]
triggerIndecesV14['HtTrain'] = [38,39,42,43,45,47,48,50,51,52]

if ntupleV=='15' in filelist[0]: triggerIndeces = triggerIndecesV15
if ntupleV=='14' in filelist[0]: triggerIndeces = triggerIndecesV14


def PassTrig(c,trigname):
    for trigidx in triggerIndeces[trigname]: 
        if c.TriggerPass[trigidx]==1: return True
    return False


print 'filelist[0]', filelist[0]

commonfilters = 'globalTightHalo2016Filter==1 && HBHENoiseFilter==1 && HBHEIsoNoiseFilter==1 && eeBadScFilter==1 && EcalDeadCellTriggerPrimitiveFilter==1 && BadChargedCandidateFilter && BadPFMuonFilter && NVtx > 0 && PFCaloMETRatio<5'#JetID==1 &&

triggerBundle = {}
if 'SingleElectron' in filelist[0] or 'EGamma' in filelist[0] or 'SinglePhoton' in filelist[0]:
    triggerBundle['MetMhtRealXMht'] = ['MhtMet6pack','SingleEl','MHT','MHT>150 && NJetsclean>1 && HT>300']
    triggerBundle['MetMhtRealXNJets'] = ['MhtMet6pack','SingleEl','NJets','MHT>300 && NJetsclean>0 && HT>300']
    triggerBundle['MetMhtRealXHt'] = ['MhtMet6pack','SingleEl','HT','MHT>300 && NJetsclean>1 && HT>0']
    triggerBundle['MetMhtFakeXMht'] = ['MhtMet6pack','SinglePho','MHT','MHT>150 && NJetsclean>1 && HT>300']
if 'MET' in filelist[0] or 'TTJets' in filelist[0]:
    triggerBundle['SingleElCocktailXElPt'] = ['SingleElCocktail','MhtMet6pack','Electrons[0].Pt()','HT>300 && NMuons==0 && NElectrons==1 && isoMuonTracks==0 && isoPionTracks==0']
    triggerBundle['SingleElCocktailDilepXElPt'] = ['SingleElCocktail','MhtMet6pack','Electrons[0].Pt()','NElectrons==2 && HTclean>300 && NMuons==0 && isoMuonTracks==0 && isoPionTracks==0 && '+diempt+'>250']
    triggerBundle['SingleElCocktailDilepXDiempt'] = ['SingleElCocktail','MhtMet6pack',diempt,'NElectrons==2 && HTclean>300 && NMuons==0 && isoMuonTracks==0 && isoPionTracks==0']
    triggerBundle['SingleElCocktailDilepXHTclean'] = ['SingleElCocktail','MhtMet6pack','HTclean','NElectrons==2 && HTclean>100 && NMuons==0 && isoMuonTracks==0 && isoPionTracks==0 && '+diempt+'>250']
    triggerBundle['SingleMuCocktailXMuPt'] = ['SingleMuCocktail','MhtMet6pack','Muons[0].Pt()','HT>300 && NElectrons==0 && NMuons==1 && isoElectronTracks==0 && isoPionTracks==0']
    triggerBundle['SingleMuCocktailDilepXMuPt'] = ['SingleMuCocktail','MhtMet6pack','Muons[0].Pt()','NMuons==2 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoPionTracks==0 && '+dimupt+'>250']
    triggerBundle['SingleMuCocktailDilepXDimupt'] = ['SingleMuCocktail','MhtMet6pack',dimupt,'NMuons==2 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoPionTracks==0 && '+dimupt+'>100']
    triggerBundle['SingleMuCocktailDilepXHTclean'] = ['SingleMuCocktail','MhtMet6pack','HTclean','NMuons==2 && HTclean>100 && NElectrons==0 && isoElectronTracks==0 && isoPionTracks==0 && '+dimupt+'>250']
if 'JetHT' in filelist[0] or 'QCD' in filelist[0]: 
    triggerBundle['SingleElCocktailDilepXDiemptZ'] = ['SingleElCocktail','HtTrain',diempt,'MET<100 && NElectrons==2 && HTclean>300 && NMuons==0 && isoMuonTracks==0 && isoPionTracks==0 && '+diemmass+'>60 && '+ diemmass+'<110']
    triggerBundle['SingleMuCocktailDilepXDimuptZ'] = ['SingleMuCocktail','HtTrain',dimupt,'MET<100 && NMuons==2 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoPionTracks==0 && '+dimumass+'>60 && '+ dimumass+'<110']
    triggerBundle['SinglePhoBarrelLoose'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1']
    triggerBundle['SinglePhoEndcapLoose'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1']
    triggerBundle['SinglePhoXHTclean'] = ['SinglePho','HtTrain','HTclean','@Photons.size()==1 && Photons_fullID[0]==1 && Photons[0].Pt()>210 && NMuons==0 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1']
    triggerBundle['SinglePhoXMHTclean'] = ['SinglePho','HtTrain','MHTclean','@Photons.size()==1 && Photons_fullID[0]==1 && Photons[0].Pt()>210 && NMuons==0 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1 && HTclean>300']    
    triggerBundle['SinglePhoLowHoe'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 &&  Photons_hadTowOverEM[0]<0.1 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1']  
      
    if ntupleV=='14': 
        triggerBundle['SinglePhoBarrelTight'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1 && Photons_hadTowOverEM[0]<0.0269 && Photons_sigmaIetaIeta[0]<0.00994 && Photons_pfChargedIsoRhoCorr[0]<0.202 && Photons_pfNeutralIsoRhoCorr[0]<(0.264+0.0148*Photons[0].Pt()+0.000017*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.362+0.0047*Photons[0].Pt())']
        triggerBundle['SinglePhoEndcapTight'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0213 && Photons_sigmaIetaIeta[0]<0.03000  && Photons_pfChargedIsoRhoCorr[0]< 0.034  && Photons_pfNeutralIsoRhoCorr[0]<(0.586+0.0163*Photons[0].Pt()+0.000014*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.617+0.0034*Photons[0].Pt())']

        triggerBundle['SinglePhoBarrelMedium'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0396  && Photons_sigmaIetaIeta[0]<0.01022 && Photons_pfChargedIsoRhoCorr[0]<0.441 && Photons_pfNeutralIsoRhoCorr[0]<(2.725+0.0148*Photons[0].Pt()+0.000017*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.571+0.0047*Photons[0].Pt())']
        triggerBundle['SinglePhoEndcapMedium'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0219 && Photons_sigmaIetaIeta[0]<0.03001  && Photons_pfChargedIsoRhoCorr[0]< 0.442  && Photons_pfNeutralIsoRhoCorr[0]<(1.715+0.0163*Photons[0].Pt()+0.000014*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(3.863+0.0034*Photons[0].Pt())']

        triggerBundle['SinglePhoBarrelMediumXHoe'] = ['SinglePho','HtTrain','Photons_hadTowOverEM[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1 && Photons_sigmaIetaIeta[0]<0.00994 && Photons_pfChargedIsoRhoCorr[0]<0.202 && Photons_pfNeutralIsoRhoCorr[0]<(0.264+0.0148*Photons[0].Pt()+0.000017*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.362+0.0047*Photons[0].Pt()) && Photons[0].Pt()>220']
        triggerBundle['SinglePhoEndcapMediumXHoe'] = ['SinglePho','HtTrain','Photons_hadTowOverEM[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    &&  Photons_sigmaIetaIeta[0]<0.03000  && Photons_pfChargedIsoRhoCorr[0]< 0.034  && Photons_pfNeutralIsoRhoCorr[0]<(0.586+0.0163*Photons[0].Pt()+0.000014*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.617+0.0034*Photons[0].Pt()) && Photons[0].Pt()>220']
        triggerBundle['SinglePhoBarrelMediumXSigmaietaieta'] = ['SinglePho','HtTrain','Photons_sigmaIetaIeta[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1 && Photons_hadTowOverEM[0]<0.0396 && Photons_pfChargedIsoRhoCorr[0]<0.202 && Photons_pfNeutralIsoRhoCorr[0]<(0.264+0.0148*Photons[0].Pt()+0.000017*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.362+0.0047*Photons[0].Pt()) && Photons[0].Pt()>220']
        triggerBundle['SinglePhoEndcapMediumXSigmaietaieta'] = ['SinglePho','HtTrain','Photons_sigmaIetaIeta[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && NMuons==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    &&  Photons_hadTowOverEM[0]<0.0219  && Photons_pfChargedIsoRhoCorr[0]< 0.034  && Photons_pfNeutralIsoRhoCorr[0]<(0.586+0.0163*Photons[0].Pt()+0.000014*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.617+0.0034*Photons[0].Pt()) && Photons[0].Pt()>220']        

                
             
    if ntupleV=='15':      
        triggerBundle['SinglePhoBarrelTight'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.02148 && Photons_sigmaIetaIeta[0]<0.00996  && Photons_pfChargedIsoRhoCorr[0]<0.65  && Photons_pfNeutralIsoRhoCorr[0]<(0.317 + 0.01512*Photons[0].Pt()+2.259e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.044 + 0.004017*Photons[0].Pt())']
        triggerBundle['SinglePhoEndcapTight'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0321  && Photons_sigmaIetaIeta[0]<0.0271   && Photons_pfChargedIsoRhoCorr[0]< 0.517   && Photons_pfNeutralIsoRhoCorr[0]<(2.716 + 0.0117*Photons[0].Pt()+2.3e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(3.032 + 0.0037*Photons[0].Pt())']
        triggerBundle['SinglePhoBarrelMedium'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.02197 && Photons_sigmaIetaIeta[0]<0.01015   && Photons_pfChargedIsoRhoCorr[0]<1.141  && Photons_pfNeutralIsoRhoCorr[0]<(1.189 + 0.01512*Photons[0].Pt()+2.259e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.08 + 0.004017*Photons[0].Pt())']
        triggerBundle['SinglePhoEndcapMedium'] = ['SinglePho','HtTrain','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0326  && Photons_sigmaIetaIeta[0]<0.0272   && Photons_pfChargedIsoRhoCorr[0]< 1.051   && Photons_pfNeutralIsoRhoCorr[0]<(2.718 + 0.0117*Photons[0].Pt()+2.3e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(3.867 + 0.0037*Photons[0].Pt())']  
                
        triggerBundle['SinglePhoBarrelMediumXHoe'] = ['SinglePho','HtTrain','Photons_hadTowOverEM[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_sigmaIetaIeta[0]<0.00996  && Photons_pfChargedIsoRhoCorr[0]<0.65  && Photons_pfNeutralIsoRhoCorr[0]<(0.317 + 0.01512*Photons[0].Pt()+2.259e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.044 + 0.004017*Photons[0].Pt()) && Photons[0].Pt()>220']
        triggerBundle['SinglePhoEndcapMediumXHoe'] = ['SinglePho','HtTrain','Photons_hadTowOverEM[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_sigmaIetaIeta[0]<0.0271   && Photons_pfChargedIsoRhoCorr[0]< 0.517   && Photons_pfNeutralIsoRhoCorr[0]<(2.716 + 0.0117*Photons[0].Pt()+2.3e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(3.032 + 0.0037*Photons[0].Pt()) && Photons[0].Pt()>220']   

        triggerBundle['SinglePhoBarrelMediumXSigmaietaieta'] = ['SinglePho','HtTrain','Photons_sigmaIetaIeta[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.02197  && Photons_pfChargedIsoRhoCorr[0]<0.65  && Photons_pfNeutralIsoRhoCorr[0]<(0.317 + 0.01512*Photons[0].Pt()+2.259e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(2.044 + 0.004017*Photons[0].Pt()) && Photons[0].Pt()>220']
        triggerBundle['SinglePhoEndcapMediumXSigmaietaieta'] = ['SinglePho','HtTrain','Photons_sigmaIetaIeta[0]','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && @Muons.size()==0 && HTclean>300 && NElectrons==0 && isoElectronTracks==0 && isoMuonTracks==0 && isoPionTracks==0 && NJetsclean>1    && Photons_hadTowOverEM[0]<0.0326   && Photons_pfChargedIsoRhoCorr[0]< 0.517   && Photons_pfNeutralIsoRhoCorr[0]<(2.716 + 0.0117*Photons[0].Pt()+2.3e-05*pow(Photons[0].Pt(),2)) && Photons_pfGammaIsoRhoCorr[0]<(3.032 + 0.0037*Photons[0].Pt()) && Photons[0].Pt()>220']           
           
if 'SingleMu' in filelist[0]:
    triggerBundle['SinglePhoBarrelFromMu'] = ['SinglePho','SingleMu','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())<1.48 && @Muons.size()>0 && NElectrons==0 && isoElectronTracks==0 && NJetsclean>1']
    triggerBundle['SinglePhoEndcapFromMu'] = ['SinglePho','SingleMu','Photons[0].Pt()','@Photons.size()==1 && Photons_fullID[0]==1 && abs(Photons[0].Eta())>1.48 && @Muons.size()>0 && NElectrons==0 && isoElectronTracks==0 && NJetsclean>1'] 



c.Draw('HT>>hHt')
hHt = c.GetHistogram().Clone('hHt')
fnew.cd()
hHt.Write('hHt')

def produceNumeratorAndDenominator(trigger,reftrigger,xvar,cuts):
    reftrigexpr = '('
    for index in triggerIndeces[reftrigger]: reftrigexpr+= 'TriggerPass['+str(index) + ']==1 || '
    reftrigexpr+='1==0)'
    selection = reftrigexpr+'*('+cuts+')'+'*('+commonfilters+')'
    eps = 0.0001
    thing2draw = 'max(min('+xvar+',%f),%f)' % (binningTrigger[xvar][-1]-eps,binningTrigger[xvar][1]+eps)
    hist = makehist('hist',xvar)   
    print 'attempting to draw all:'
    print xvar+'>>hist',selection
    c.Draw(thing2draw+'>>hist',selection)
    hAll = c.GetHistogram().Clone('hAll'+trigger+'Vs'+xvar+'From'+reftrigger)
    selection +='*('
    for index in triggerIndeces[trigger]: selection+='TriggerPass['+str(index) + ']==1 ||'
    selection+=' 1==0)'        
    print 'attempting to draw pass:'
    print xvar+'>>hist',selection
    c.Draw(thing2draw+'>>hist',selection)
    hPass = c.GetHistogram().Clone('hPass'+trigger+'Vs'+xvar+'From'+reftrigger)
    return hPass, hAll



for key in triggerBundle:
    trigger,reftrigger,xvar,cuts = triggerBundle[key]
    hPass, hAll = produceNumeratorAndDenominator(trigger,reftrigger,xvar,cuts)
    fnew.cd()
    hPass.SetTitle('hPass'+key)
    hAll.SetTitle('hAll'+key)    
    hPass.Write('hPass'+key)
    hAll.Write('hAll'+key)

print 'just created', fnew.GetName()
fnew.Close()


'''V15
[21, 23, 28, 35, 40, 41]#[45,46,47,48,49,50,51,52,54,55,58,59,63,64,65,66]
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
45 HLT_IsoMu20_v 0 2 #[45, 46, 47, 48, 49, 50, 51, 52, 54, 55, 58, 59, 63, 64, 65, 66]
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
145 HLT_TkMu50_v -1 1'''
