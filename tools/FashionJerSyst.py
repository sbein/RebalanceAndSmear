'''on cmsconnect at /uscms_data/d3/sbein/Ra2slashB2018/29Nov2018/CMSSW_10_1_0/src/RebalanceAndSmear, do

python tools/ahadd.py -f JerPit/Run2016_JerUpPartial.root output/Run2016*/*JerUp1of5.root
python tools/ahadd.py -f JerPit/Run2017_JerUpPartial.root output/Run2017*/*JerUp1of5.root
python tools/ahadd.py -f JerPit/Run2018_JerUpPartial.root output/Run2018*/*JerUp1of5.root

python tools/ahadd.py -f JerPit/Run2016_JerNom.root output/Run2016*/*Tree1of5.root
python tools/ahadd.py -f JerPit/Run2017_JerNom.root output/Run2017*/*Tree1of5.root
python tools/ahadd.py -f JerPit/Run2018_JerNom.root output/Run2018*/*Tree1of5.root

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
    
    
        

