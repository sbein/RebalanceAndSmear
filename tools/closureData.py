from ROOT import *
from utils import *
from ra2blibs import *
import os,sys
gROOT.SetBatch(1)

datamc = 'MC'
datamc = 'Data'
lumi = 2.3
lumi = 24.7
lumi = 36.3
lumi = 135
lumi = 4793.367+9632.85+4247.7+9313.99+13498.41

#loadSearchBins2016()
#SearchBinNames = {v: k for k, v in SearchBinNumbers.iteritems()}

specialscale = lumi/4793.367#b
specialscale = lumi/9632.85#c
specialscale = lumi/4247.7#d
specialscale = lumi/9313.99#e
specialscale = lumi/13498.41#f
specialscale = 1.0

redoBinning = binningAnalysis
#redoBinning = binningUser


fnamePrediction = 'Vault/Run2017RandS_Nom.root'
fnamePrediction = 'OutputBoostrapRun2017.root'
#fnamePrediction = 'testF.root'


fnamePredJerUp = 'Vault/Run2017RandS_JerUp.root'
#fnamePrediction = 'Vault/Run2017RandS_JerUp.root'
fnameTruth = 'Vault/MET_LDP_2017.root'
fnameNonQcd = 'Vault/NonQcd_LDP_MC2017.root'

fPrediction = TFile(fnamePrediction)
fPredJerUp = TFile(fnamePredJerUp)
fTruth = TFile(fnameTruth)
fNonQcd = TFile(fnameNonQcd)

subtractnonq = True #toggle this on to get njet systematic

gStyle.SetOptStat(0)
gROOT.ForceStyle()

def applyCorrections(hmethod, SearchBinNames):
    hPrediction = hmethod.Clone(hmethod.GetName())
    return hPrediction
    xax = hPrediction.GetXaxis()
    for ibin in range(2, xax.GetNbins()+1):
        nb = int(SearchBinNames[ibin-1][-1])
        nj = int(SearchBinNames[ibin-1][-8])
        if (nj==2 and nb==2) or (nj>2 and nb==3): 
            hPrediction.SetBinError(ibin,TMath.Sqrt(pow(hPrediction.GetBinContent(ibin), 2)+pow(hPrediction.GetBinError(ibin),2)))
            try: fracerr = hPrediction.GetBinError(ibin)/hPrediction.GetBinContent(ibin)
            except: fracerr = 0
            if nj == 3: 
                print 'yeah, using big scale', hmethod.GetName()
                scale = 5.0
            else: scale = 3.0
            #print 'before', hPrediction.GetBinContent(ibin)
            hPrediction.SetBinContent(ibin,scale*hPrediction.GetBinContent(ibin))
            #print 'after', hPrediction.GetBinContent(ibin)
            hPrediction.SetBinError(ibin,fracerr*hPrediction.GetBinContent(ibin))
    return hPrediction


def mkLabel(str_,kinvar,selection=''):
    newstr = str_
    if newstr[0]=='h':newstr = newstr[1:]
    newstr = newstr.replace('GenSmeared',' gen-smeared ')
    newstr = newstr.replace('Rebalanced',' rebalanced ')
    newstr = newstr.replace('RplusS','R&S Prediction')
    if datamc=='Data': newstr = newstr.replace('Truth','Data')
    newstr = newstr.replace('Truth','Run 2017')
    if datamc == 'Data': newstr = newstr.replace('Truth',' Data (2017)')
    newstr = newstr.replace(kinvar,'')
    newstr = newstr.replace('_b','').replace('_','')
    newstr = newstr.replace(selection+' ','')
    return newstr

kinvar = 'Mass'
kinvar = 'Zpt'
kinvar = 'Ht'
kinvar = 'Mht'
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



keys = fPrediction.GetListOfKeys()
keys = sorted(keys,key=lambda thing: thing.GetName())
newfile = TFile('validation_data.root','recreate')

if datamc=='MC': norm = 1000*lumi
else: norm = 1

def UpMySyst(hmain, halt):
    xax = hmain.GetXaxis()
    for ibin in range(1,xax.GetNbins()+1):
        oldunc = hmain.GetBinError(ibin)
        addunc = halt.GetBinError(ibin)
        hmain.SetBinError(ibin, TMath.Sqrt(pow(oldunc,2)+pow(addunc,2)))

#for Pair in PairsToCompare:
for key in keys:
    if not ('RplusS' in key.GetName()): continue
    #if not 'Mht' in key.GetName(): continue
    kinvar = key.GetName().replace('GenSmeared','').replace('Rebalanced','').replace('RplusS','')
    selection = kinvar[1:kinvar.find('_')]
    kinvar = kinvar[kinvar.find('_')+1:]
    if '_' in kinvar: continue
    print 'kinvar=', kinvar
    if 'RplusS' in key.GetName():
        method = 'RplusS'
        standard = 'Truth'
        if datamc == 'Data':
            method = 'RplusS'
            standard = 'Truth'


    hPrediction = fPrediction.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    hPrediction.Scale(specialscale)
    hPredUp = fPredJerUp.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    UpMySyst(hPrediction, hPredUp)
    hPrediction.SetTitle('R&S prediction')

    hTruth = fTruth.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hTruth.Scale(norm)    
    hTruth.SetTitle('Run 2017 observed')
    
    hNonQcd = fNonQcd.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hNonQcd.Scale(lumi)        
    hNonQcd.SetTitle('t#bar{t}+jets, W+jets, Z#rightarrow #nu#nu MC')

    if subtractnonq: hTruth.Add(hNonQcd,-1)
    
    try: 
        failfactor = fPrediction.Get('hTotFit').Integral()/fPrediction.Get('hPassFit').Integral()
        print 'fail factor', 
    except: 
        failfactor = 1.0
    if 'RplusS' in key.GetName(): 
        try: hPrediction.Scale(failfactor)
        except: pass

    #hPrediction.Scale(2.0)
    if datamc == 'Data': col = kGreen
    if datamc == 'MC': col = kBlue
    histoStyler(hTruth, 1)
    histoStyler(hPrediction, kGray+1)
    hPrediction.SetFillColor(col-5)
    hPrediction.SetFillStyle(1002)
    hNonQcd.SetFillStyle(1002)
    hNonQcd.SetFillColor(hNonQcd.GetLineColor())    

    
    cGold = mkcanvas('cEnchilada')
    if len(redoBinning[kinvar])>3: ##this should be reinstated
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hTruth = hTruth.Rebin(nbins,'',newxs)
        hPrediction = hPrediction.Rebin(nbins,'',newxs)
        hNonQcd = hNonQcd.Rebin(nbins,'',newxs)        
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hTruth = hTruth.Rebin(nbins,'',newxs)
        hPrediction = hPrediction.Rebin(nbins,'',newxs)
        hNonQcd = hNonQcd.Rebin(nbins,'',newxs)        

    print key.GetName()
    hpure = hPrediction.Clone(hPrediction.GetName()+'pure')
    htot = hpure.Clone()
    htot.Add(hNonQcd)
    hpure.Divide(htot)
    hpure.SetLineColor(kViolet+2)
    hpure.SetFillStyle(0)
    
    leg = mklegend(x1=.405, y1=.53, x2=.90, y2=.77, color=kWhite)
    if subtractnonq: hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction],datamc='mc',lumi=round(lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')
    else: hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hPrediction, hNonQcd],datamc='mc',lumi=round(lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')
    hrat.GetYaxis().SetRangeUser(0,2.4)
    hrat.GetXaxis().SetTitle(kinvar)

    pad2.cd()
    hpure.Draw('hist same')
    #if kinvar=='NJets': hrat.Fit('pol1','s','')
    cGold.Update()   

    cname = (hPrediction.GetName()+'_And_'+hTruth.GetName()).replace(' ','')
    cGold.Write(cname)
    if subtractnonq and key.GetName()=='hLdpLmhtSideband_NJetsRplusS':
        print 'activating thingy'
        hrat.Write('hRatio_LdpLmhtSideband_RplusSAndTruth_NJets')
    cGold.Print('pdfs/validation/'+selection+'_'+method+'And'+standard+'_'+kinvar+'.pdf')


print 'just created', newfile.GetName()
