#rm output/*/Skim_tree_*MC20*.root
#rm output/MET_2017/Skim_tree_MET_2017*

python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_MC --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_HT --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WJetsToLNu --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ZJets --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WW --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WZ --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ZZ --selection signalSideband
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ST --selection signalSideband


python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_MC --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_HT --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WJetsToLNu --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ZJets --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WW --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword WZ --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ZZ --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword ST --selection LDP 

python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2018 --selection signalSideband  --periodwrthem PreHem
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2018 --selection signalSideband --periodwrthem DuringHem
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2018 --selection LDP  --periodwrthem PreHem
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2018 --selection LDP  --periodwrthem DuringHem


python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2017 --selection signalSideband 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2016 --selection signalSideband 


python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2017 --selection LDP 
python tools/submitjobsSkims.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2016 --selection LDP



#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_MC --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword TTJets_HT --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword WJetsToLNu --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword ZJets --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword WW --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword WZ --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword ZZ --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword ST --selection LDP &
#python tools/submitjobsSkimsCmsconnect.py --analyzer tools/SkimValidation.py --fnamekeyword MET_2017 --selection LDP &




