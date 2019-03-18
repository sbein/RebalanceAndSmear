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
python tools/FashionJerSyst.py Run2016 && python tools/FashionJerSyst.py Run2017 && python tools/FashionJerSyst.py Run2018
'''

from ROOT import *
from utils import *
from ra2blibs import *
import sys

gROOT.SetBatch(1)
try: year = sys.argv[1]
except: year = 'Run2016'

redoBinning = binningAnalysis
def nicelabel(label):
    label_ = label
    label_ = label_.replace('Vs',' vs ')
    label_ = label_.replace('Mht','H_{T}^{miss}')
    label_ = label_.replace('Met','E_{T}^{miss}')
    label_ = label_.replace('Ht','H_{T}')
    label_ = label_.replace('NJets','N_{jets}')
    label_ = label_.replace('BTags','N_{b-jets}')
    label_ = label_.replace('Pt',' p_{T}')
    label_ = label_.replace('Eta',' #eta')
    if 'DPhi' in label_:
        label_ = label_.replace('DPhi','#Delta#phi(H^{miss}_{T}, jet')
        label_ = label_+')'
        numberloc = max(label_.find('1'),label_.find('2'),label_.find('3'),label_.find('4'))+1
        label_ = label_[:numberloc]+', '+label_[numberloc:]
        label_ = label_.replace(', )',')')
    return label_

fUp = TFile('JerPit/'+year+'JerUp.root')
fNom = TFile('JerPit/'+year+'JerNom.root')

hNomNorm = fNom.Get('hLdpLmhtSideband_BTagsTruth').Clone('hNomNorm')
hUpNorm = fUp.Get('hLdpLmhtSideband_BTagsTruth').Clone('hUpNorm')
NORM = hNomNorm.GetBinContent(1)/hUpNorm.GetBinContent(1)

#hNomNorm = fNom.Get('hHt').Clone('hNomNorm')
#hUpNorm = fUp.Get('hHt').Clone('hUpNorm')
#NORM = hNomNorm.Integral()/hUpNorm.Integral()

    
fnew = TFile('JerImpact'+year+'.root', 'recreate')
c1 = mkcanvas('c1')
keys = fUp.GetListOfKeys()
for key in keys:
    name = key.GetName()
    if not 'RplusS' in name: continue
    if not 'LowMhtBaseline' in name: continue
    kinvar = name.split('_')[-1].replace('RplusS','')
    hUp = fUp.Get(name)
    histoStyler(hUp, kOrange+1)
    hUp.Scale(NORM)
    hUp.SetFillStyle(1001)
    hUp.SetFillColor(hUp.GetLineColor()+1)    
    hNom = fNom.Get(name)
    hUp.SetTitle('JER-up')
    hNom.SetTitle('JER-nominal')    



    if len(redoBinning[kinvar])>3: ##this should be reinstated
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hNom = hNom.Rebin(nbins,'',newxs)
        hUp = hUp.Rebin(nbins,'',newxs)
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hNom = hNom.Rebin(nbins,'',newxs)
        hUp = hUp.Rebin(nbins,'',newxs)


        
    leg = mklegend(x1=.5, y1=.64, x2=.93, y2=.79)
    hrat, pad1, pad2 = FabDraw(c1,leg,hNom,[hUp],datamc='data',lumi=1, title = '', LinearScale=False, fractionthing='nom/JER-up')
    hrat.GetXaxis().SetTitle(nicelabel(kinvar)+('bin' not in units[kinvar])*(' ['+units[kinvar]+']'))    
    hrat.GetYaxis().SetRangeUser(0,3.5)
    c1.Update()
    fnew.cd()
    c1.Write('c1_'+name)
    hUp.Write('h'+name+'JerUp')
    hNom.Write('h'+name+'JerNom')    

print 'just created', fnew.GetName()
fnew.Close()
    
    
        

