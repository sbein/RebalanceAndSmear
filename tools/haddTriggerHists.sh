python tools/ahadd.py -f output/Run2016-SingleElectron.root output/Run2016*SingleElectron/hists*.root
python tools/ahadd.py -f output/Run2017-SingleElectron.root output/Run2017*SingleElectron/hists*.root
python tools/ahadd.py -f output/Run2018-SingleElectron.root output/Run2018*EGamma/hists*.root

python tools/ahadd.py -f output/Run2016-MET.root output/Run2016*MET/hists*.root
python tools/ahadd.py -f output/Run2017-MET.root output/Run2017*MET/hists*.root
python tools/ahadd.py -f output/Run2018-MET.root output/Run2018*MET/hists*.root

python tools/ahadd.py -f output/Run2016-SinglePhoton.root output/Run2016*SinglePhoton/hists*.root
python tools/ahadd.py -f output/Run2017-SinglePhoton.root output/Run2017*SinglePhoton/hists*.root
python tools/ahadd.py -f output/Run2018-SinglePhoton.root output/Run2018*EGamma/hists*.root

python tools/ahadd.py -f output/Run2016-JetHT.root output/Run2016*JetHT/hists*.root
python tools/ahadd.py -f output/Run2017-JetHT.root output/Run2017*JetHT/hists*.root
python tools/ahadd.py -f output/Run2018-JetHT.root output/Run2018*JetHT/hists*.root

python tools/ahadd.py -f output/Run2016-SingleMuon.root output/Run2016*SingleMuon/hists*.root
python tools/ahadd.py -f output/Run2017-SingleMuon.root output/Run2017*SingleMuon/hists*.root
python tools/ahadd.py -f output/Run2018-SingleMuon.root output/Run2018*SingleMuon/hists*.root

#1) look for more v14 triggers
#2) add photon trigger
#3) plot more things that look like the AN
#4) look at photon
echo scp trees/signal/hist*.root ${DESY}:/nfs/dust/cms/user/beinsam/Ra2b/Run2Legacy/25Sept2018/CMSSW_10_1_0/src/trees/optimization/signal

'''
python tools/ahadd.py -f output/Run2016B-JetHT.root output/Run2016B*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016C-JetHT.root output/Run2016C*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016D-JetHT.root output/Run2016D*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016E-JetHT.root output/Run2016E*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016F-JetHT.root output/Run2016F*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016G-JetHT.root output/Run2016G*JetHT/hists*.root
python tools/ahadd.py -f output/Run2016H-JetHT.root output/Run2016H*JetHT/hists*.root

'''