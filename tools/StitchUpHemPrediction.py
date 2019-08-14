from ROOT import *
from utils import *
from ra2blibs import *
from glob import glob
import os, sys

#this script creates one file to represent all of 2018 - later it gets scaled to different luminosities... with the full 2018 data processed and the new mission to split the prediction into pre-HEM and post-HEM, maybe it's best to use processBootstrap.py directly for 2018 pre and post. Then I can come back here and do one mega global bootstrap for all of run 2, to be used for central prediction only. 
hem_filter = 'Hemv0p5'

stitchskims = True
stitchpredmain = False
stitchSmall2018 = False##try to only have one of these set to true

redoBinning = binningAnalysis
#otherwise does prediction
''' this first for the skims:
hadd -f Vault/Skim_tree_MET_Run2018PreHem_LDP.root output/MET_2018/Skim_tree_MET_2018B_LDPPreHem.root output/MET_2018/Skim_tree_MET_2018A_LDPPreHem.root
hadd -f Vault/Skim_tree_MET_Run2018DuringHem_LDP.root output/MET_2018/Skim_tree_MET_2018B_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018C_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018D_LDPDuringHem.root
hadd -f Vault/Skim_tree_MET_Run2018PreHem_signalSideband.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandPreHem.root output/MET_2018/Skim_tree_MET_2018A_signalSidebandPreHem.root
hadd -f Vault/Skim_tree_MET_Run2018DuringHem_signalSideband.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018C_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018D_signalSidebandDuringHem.root

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

#if stitchskims: fileskey = 'output/MET_2018/Skim_tree_MET_2018*PreHem*.root'
#if stitchskims: fileskey = 'Vault/Skim_tree_MET_2018_*DuringHem.root'#'Vault/Skim_tree_MET_2018*PreHem.root'
if stitchskims: fileskey = 'Vault/Skim_tree_MET_Run2018DuringHem_*.root'#'Vault/Skim_tree_MET_2018*PreHem.root'
if stitchpredmain: fileskey = 'VaultHem/*DuringHem*.root'
if stitchSmall2018: 
    fileskey = 'Partial2018Pit/*PreHem*.root'
    #order in case you have the terrible situation of needing to scale up a prediction because not enough jobs finished for validation
    #: set helperfactorto 1
    helperfactor = 1
    #then run closureDataDDNonQ.py to get better helpfactor and plug it in here:
    helperfactor = 3.59185545485
    #then 

fnamelistDuringHem = glob(fileskey)

#print 'fnamelistDuringHem', fnamelistDuringHem
#exit(0)

if stitchpredmain: 
    if not os.path.exists('VaultHem/OutOfTheWay'): os.system('mkdir VaultHem/OutOfTheWay')
for fnameDuringHem in fnamelistDuringHem:
    fDuringHem = TFile(fnameDuringHem)
    fnamePreHem = fnameDuringHem.replace('DuringHem','PreHem')
    fPreHem = TFile(fnamePreHem)
    fnameNew = fnameDuringHem.replace('DuringHem','')
    fnew = TFile(fnameNew, 'recreate')
    keys = fDuringHem.GetListOfKeys()
    for key in keys:
        name = key.GetName()

        if not len(name.split('_'))>1: 
            h = fDuringHem.Get(name)
            h.Add(fPreHem.Get(name))
            fnew.cd()
            if stitchSmall2018: h.Scale(helperfactor)
            h.Write()
            continue
        if not hem_filter in name: continue
        #if stitchpredmain and 'SidebandHemv0p5' in name: 
        #    name = name.replace('0p5','0.7')
        if 'MaxHemJetPt' in name: continue
        if not ('hLowMhtBase' in name or 'hLdpLmhtBase' in name or 'hLdpLmhtSideband' in name or 'hLowMhtSideband' in name or 'Pass' in name or 'TotFit' in name): continue 
        if 'MaxForward' in name: continue
        if 'MinDeltaPhiHem' in name: continue
        objDuringHem = fDuringHem.Get(name)
        hemname = name.replace(hem_filter,'').replace('line','').replace('LowMhtBase_','LowMhtBaseline_')
        #print 'trying to get hemname', hemname, 'from', fPreHem.GetName()
        objPreHem = fPreHem.Get(hemname)
        print 'adding ', hemname, 'from', fPreHem.GetName(), 'to', name, 'from', fDuringHem.GetName()
        objPreHem.Add(objDuringHem)
        if stitchSmall2018: objPreHem.Scale(helperfactor)
        fnew.cd()
        #if not stitchskims and False: objPreHem.Write(name.replace('Base_','Baseline_'))
        objPreHem.Write(hemname)
    print 'creating', fnew.GetName()
    fnew.Close()    
if stitchpredmain: 
    print 'mv VaultHem/*Hem* VaultHem/OutOfTheWay/'
    print 'mv VaultHem/*.root Vault/'
    print 'now ready to run processBootstrap on the 2018 data'

if stitchSmall2018: 
    print ''' if stitching little, then do 
hadd -f Partial2018Pit/QcdPredRun2.root Partial2018Pit/QcdPred2018.root Vault/RandS_Run2016_*of5.root Vault/RandS_Run2017_*of5.root
            '''

'''
hadd -f Vault/Skim_tree_MET_Run2_LDP.root Vault/Skim_tree_MET_Run2018_LDP.root Vault/MET_LDP_2017.root Vault/MET_LDP_2016.root
hadd -f Vault/Skim_tree_MET_Run2_signalSideband.root Vault/Skim_tree_MET_Run2018_signalSideband.root Vault/MET_signalSideband_2017.root Vault/MET_signalSideband_2016.root
'''
