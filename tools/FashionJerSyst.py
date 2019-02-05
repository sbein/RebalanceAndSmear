'''on cmsconnect at /uscms_data/d3/sbein/Ra2slashB2018/29Nov2018/CMSSW_10_1_0/src/RebalanceAndSmear, do

python tools/ahadd.py -f JerPit/Run2016_JerUpPartial.root output/Run2016*Jet/*JerUp.root
python tools/ahadd.py -f JerPit/Run2017_JerUpPartial.root output/Run2017*Jet/*JerUp.root
python tools/ahadd.py -f JerPit/Run2018_JerUpPartial.root output/Run2018*Jet/*JerUp.root
python tools/ahadd.py -f JerPit/Run2016_JerNom.root output/Run2016*Jet/*Tree.root
python tools/ahadd.py -f JerPit/Run2017_JerNom.root output/Run2017*Jet/*Tree.root
python tools/ahadd.py -f JerPit/Run2018_JerNom.root output/Run2018*Jet/*Tree.root

#try 2
python tools/ahadd.py JerPit/Run2016JerUp.root output/Run2016*Jet/*TreeJerUp.root
python tools/ahadd.py JerPit/Run2016JerNom.root output/Run2016*Jet/*Tree.root

python tools/ahadd.py JerPit/Run2017JerUp.root output/Run2017*Jet/*TreeJerUp.root
python tools/ahadd.py JerPit/Run2017JerNom.root output/Run2017*Jet/*Tree.root

python tools/ahadd.py JerPit/Run2018JerUp.root output/Run2018*Jet/*TreeJerUp.root
python tools/ahadd.py JerPit/Run2018JerNom.root output/Run2018*Jet/*Tree.root

echo done

Then here, do
python toosl/FashionJerSyst.py Run2016 && python toosl/FashionJerSyst.py Run2017 && python toosl/FashionJerSyst.py Run2018
'''

from ROOT import *
from utils import *
import sys

try: year = sys.argv[1]
except: year = 'Run2016'

fUp = TFile('JerPit/'+year+'_JerUp.root')
fNom = TFile('JerPit/'+year+'_JerNom.root')

fnew = TFile('JerImpact'+year+'.root')
c1 = mkcanvas('c1')
keys = fUp.GetListOfKeys()
for key in keys:
    name = key.GetName()
    if not 'RplusS' in name: continue
    hUp = fUp.Get(name)
    hNom = fNom.Get(name)
    leg = mklegend()
    hrat, pad1, pad2 = FabDraw(c1,leg,hNom,[hUp],datamc='data',lumi=1, title = '', LinearScale=False, fractionthing='nom/JER-up')
    fnew.cd()
    c1.Write('c1_'+name)

print 'just created', fnew.GetName()
fnew.Close()
    
    
        

