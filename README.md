# RebalanceAndSmear

*Set up code*

cmsrel CMSSW_10_1_0
cd CMSSW_10_1_0/src
cmsenv
git clone https://github.com/sbein/RebalanceAndSmear/
cd RebalanceAndSmear/

*generate jet response templates and prior distributions*

python tools/ResponseMaker.py --filenamekey TTJets_Tune
