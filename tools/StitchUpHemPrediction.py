from ROOT import *
from utils import *
from ra2blibs import *
from glob import glob
import os, sys

stitchskims = True
stitchpredmain = False
stitchSmall2018 = False##try to only have one of these set to true

redoBinning = binningAnalysis

#otherwise does prediction
''' this first for the skims:
hadd -f output/MET_2018/Skim_tree_MET_2018_LDPPreHem.root output/MET_2018/Skim_tree_MET_2018B_LDPPreHem.root output/MET_2018/Skim_tree_MET_2018A_LDPPreHem.root
hadd -f output/MET_2018/Skim_tree_MET_2018_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018B_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018C_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018D_LDPDuringHem.root
hadd -f output/MET_2018/Skim_tree_MET_2018_signalSidebandPreHem.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandPreHem.root output/MET_2018/Skim_tree_MET_2018A_signalSidebandPreHem.root
hadd -f output/MET_2018/Skim_tree_MET_2018_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018C_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018D_signalSidebandDuringHem.root

python tools/ahadd.py -f Vault/RandS_Run2018_PreHem1of5.root output/Run2018B*J/RandS*PreHem1of5.root output/Run2018A*JetHT/*1of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_PreHem2of5.root output/Run2018B*J/RandS*PreHem2of5.root output/Run2018A*JetHT/*2of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_PreHem3of5.root output/Run2018B*J/RandS*PreHem3of5.root output/Run2018A*JetHT/*3of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_PreHem4of5.root output/Run2018B*J/RandS*PreHem4of5.root output/Run2018A*JetHT/*4of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_PreHem5of5.root output/Run2018B*J/RandS*PreHem5of5.root output/Run2018A*JetHT/*5of5.root

python tools/ahadd.py -f Vault/RandS_Run2018_DuringHem1of5.root output/Run2018B*J/RandS*DuringHem1of5.root output/Run2018C*J/RandS*1of5.root output/Run2018D*J/RandS*1of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_DuringHem2of5.root output/Run2018B*J/RandS*DuringHem2of5.root output/Run2018C*J/RandS*2of5.root output/Run2018D*J/RandS*2of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_DuringHem3of5.root output/Run2018B*J/RandS*DuringHem3of5.root output/Run2018C*J/RandS*3of5.root output/Run2018D*J/RandS*3of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_DuringHem4of5.root output/Run2018B*J/RandS*DuringHem4of5.root output/Run2018C*J/RandS*4of5.root output/Run2018D*J/RandS*4of5.root
python tools/ahadd.py -f Vault/RandS_Run2018_DuringHem5of5.root output/Run2018B*J/RandS*DuringHem5of5.root output/Run2018C*J/RandS*5of5.root output/Run2018D*J/RandS*5of5.root



#alternative 2018 prediction scaling up LDP and HDP to get norm and validation
python tools/ahadd.py -f Partial2018Pit/QcdPred2018PreHem.root output/Run2018A-17Sep2018-v1.Jet/*.root output/Run2018B-17Sep2018-v1.Jet/*PreHem*.root && python tools/ahadd.py -f Partial2018Pit/QcdPred2018DuringHem.root output/Run2018B-17Sep2018-v1.Jet/*DuringHem*.root output/Run2018C-17Sep2018-v1.Jet/*.root output/Run2018D-PromptReco-v2.Jet/*.root
'''

#Then transfer the PreHem and during HEM 2018 files into VaultHem and follow these directions

if stitchskims: fileskey = 'output/MET_2018/Skim_tree_MET_2018_*PreHem*.root' 
if stitchpredmain: fileskey = 'VaultHem/*PreHem*.root'
if stitchSmall2018: 
    fileskey = 'Partial2018Pit/*PreHem*.root'
    #order in case you have the terrible situation of needing to scale up a prediction because not enough jobs finished for validation
    #: set helperfactorto 1
    helperfactor = 1
    #then run closureDataDDNonQ.py to get better helpfactor and plug it in here:
    helperfactor = 3.59185545485
    #then 

fnamelistPreHem = glob(fileskey)
if stitchpredmain: os.system('mkdir VaultHem/OutOfTheWay/')
for fnamePreHem in fnamelistPreHem:
    fPreHem = TFile(fnamePreHem)
    fnameDuringHem = fnamePreHem.replace('PreHem','DuringHem')
    fDuringHem = TFile(fnameDuringHem)
    fnameNew = fnamePreHem.replace('PreHem','')
    fnew = TFile(fnameNew, 'recreate')
    #fPreHem.ls()
    keys = fPreHem.GetListOfKeys()
    for key in keys:
        name = key.GetName()

        if not len(name.split('_'))>1: 
            h = fPreHem.Get(name)
            h.Add(fDuringHem.Get(name))
            fnew.cd()
            if stitchSmall2018: h.Scale(helperfactor)
            h.Write()
            continue
        if 'Hemv' in name: continue
        if not ('hLowMhtBase' in name or 'hLdpLmhtBase' in name or 'hLdpLmhtSideband' in name or 'hLowMhtSideband' in name or 'Pass' in name or 'TotFit' in name): continue 
        if 'MaxForward' in name: continue
        objPreHem = fPreHem.Get(name)
        hemname = name.replace('_','Hemv30_').replace('line','')
        objDuringHem = fDuringHem.Get(hemname).Clone('somethingelse')

        objPreHem.Add(objDuringHem)
        if stitchSmall2018: objPreHem.Scale(helperfactor)
        fnew.cd()
        if not stitchskims and False: objPreHem.Write(name.replace('Base_','Baseline_'))
        else: objPreHem.Write(name)
    print 'creating', fnew.GetName()
    fnew.Close()    
if stitchpredmain: 
    print 'mv VaultHem/*Hem* VaultHem/OutOfTheWay/'
    print 'mv VaultHem/*.root Vault/'


if stitchSmall2018: 
    print ''' if stitching little, then do 
hadd -f Partial2018Pit/QcdPredRun2.root Partial2018Pit/QcdPred2018.root Vault/RandS_Run2016_*of5.root Vault/RandS_Run2017_*of5.root
            '''
