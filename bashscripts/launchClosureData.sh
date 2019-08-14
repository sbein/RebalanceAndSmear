#I think it's fair to say you can begin here after all jobs are complete

#python tools/ahadd.py -f Vault/Run2016RandS_Nom.root output/Run2016*/*Tree.root
#python tools/ahadd.py -f Vault/Run2016RandS_JerUp.root output/Run2016*/*JerUp.root
python tools/ahadd.py -f Vault/NonQcd_LDP_MC2016.root output/*/*MC2016_LDP.root
python tools/ahadd.py -f Vault/NonQcdZJets_LDP_MC2016.root output/ZJets/*MC2016_LDP.root
python tools/ahadd.py -f Vault/NonQcd_signalSideband_MC2016.root output/*/*MC2016_signalSideband.root
python tools/ahadd.py -f Vault/NonQcdZJets_signalSideband_MC2016.root output/ZJets/*MC2016_signalSideband.root
hadd -f Vault/MET_LDP_2016.root            output/MET_2016/Skim_tree_MET_2016*LDP.root
hadd -f Vault/MET_signalSideband_2016.root output/MET_2016/Skim_tree_MET_2016*signalSideband.root

#python tools/ahadd.py -f Vault/Run2017RandS_Nom.root output/Run2017*/*Tree.root
#python tools/ahadd.py -f Vault/Run2017RandS_JerUp.root output/Run2017*/*JerUp.root
python tools/ahadd.py -f Vault/NonQcd_LDP_MC2017.root output/*/*MC2017_LDP.root
python tools/ahadd.py -f Vault/NonQcdZJets_LDP_MC2017.root output/ZJets/*MC2017_LDP.root
python tools/ahadd.py -f Vault/NonQcd_signalSideband_MC2017.root output/*/*MC2017_signalSideband.root
python tools/ahadd.py -f Vault/NonQcdZJets_signalSideband_MC2017.root output/ZJets/*MC2017_signalSideband.root
hadd -f Vault/MET_LDP_2017.root output/MET_2017/Skim_tree_MET_2017*LDP.root
hadd -f Vault/MET_signalSideband_2017.root output/MET_2017/Skim_tree_MET_2017*signalSideband.root


#python tools/ahadd.py -f Vault/Run2018RandS_Nom.root output/Run2018*/*Tree.root
#python tools/ahadd.py -f Vault/Run2018RandS_JerUp.root output/Run2018*/*JerUp.root
python tools/ahadd.py -f Vault/NonQcd_LDP_MC2018.root output/*/*MC2018_LDP.root
python tools/ahadd.py -f Vault/NonQcdZJets_LDP_MC2018.root output/ZJets/*MC2018_LDP.root
python tools/ahadd.py -f Vault/NonQcd_signalSideband_MC2018.root output/*/*MC2018_signalSideband.root
python tools/ahadd.py -f Vault/NonQcdZJets_signalSideband_MC2018.root output/ZJets/*MC2018_signalSideband.root


#python tools/ahadd.py -f Vault/NonQcd_LDP_MC2018.root output/*/*MC2017_LDP.root #must make dedicated below...
#python tools/ahadd.py -f Vault/NonQcd_signalSideband_MC2018.root output/*/*MC2017_signalSideband.root same...
hadd -f Vault/Skim_tree_MET_Run2018PreHem_LDP.root output/MET_2018/Skim_tree_MET_2018B_LDPPreHem.root output/MET_2018/Skim_tree_MET_2018A_LDPPreHem.root
hadd -f Vault/Skim_tree_MET_Run2018DuringHem_LDP.root output/MET_2018/Skim_tree_MET_2018B_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018C_LDPDuringHem.root output/MET_2018/Skim_tree_MET_2018D_LDPDuringHem.root
hadd -f Vault/Skim_tree_MET_Run2018PreHem_signalSideband.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandPreHem.root output/MET_2018/Skim_tree_MET_2018A_signalSidebandPreHem.root
hadd -f Vault/Skim_tree_MET_Run2018DuringHem_signalSideband.root output/MET_2018/Skim_tree_MET_2018B_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018C_signalSidebandDuringHem.root output/MET_2018/Skim_tree_MET_2018D_signalSidebandDuringHem.root
#This should be followed by a running of StitchUpHemPrediction.py with the stitchskims boolean set to true

python tools/RamRun2NonQcdTogetherMC.py

python tools/closureData.py Run2016
python tools/closureData.py Run2017
python tools/closureData.py Run2018
python tools/closureData.py Run2



#make Vault/NonQcd_signalSideband_Run2.root from 
