from ROOT import *
from utils import *
from ra2blibs import *
import os,sys
gROOT.SetBatch(1)

datamc = 'MC'
lumi = 2.3
lumi = 24.7
lumi = 36.3
lumi = 135

loadSearchBins2018()
SearchBinNames = {v: k for k, v in SearchBinNumbers.iteritems()}


try: filenameA = sys.argv[1]
except:
    print 'please give command like'
    print 'python python/closureTest.py Vault/QCD_Summer16.root'
    filenameA = 'Vault/QCD_Summer16.root'

filenameA = 'Vault/QCD_Summer16.root'
filenameB = 'Vault/QCD_Fall17.root'

if '16' in filenameA:
    year = 'Summer16'
    lumi = 35.9
elif '17' in filenameA:
    year = 'Fall17'
    lumi = 100.7

lumiA = 35900
lumiB = 100700
year = 'Run2'
lumi = lumiA+lumiB
    
redoBinning = binningAnalysis
#redoBinning = binningUser
#redoBinning = binning

gStyle.SetOptStat(0)
gROOT.ForceStyle()

def applyCorrections(hmethod, SearchBinNames):
    hMethod = hmethod.Clone(hmethod.GetName())
    return hMethod
    xax = hMethod.GetXaxis()
    for ibin in range(2, xax.GetNbins()+1):
        nb = int(SearchBinNames[ibin-1][-1])
        nj = int(SearchBinNames[ibin-1][-8])
        if (nj==2 and nb==2) or (nj>2 and nb==3): 
            hMethod.SetBinError(ibin,TMath.Sqrt(pow(hMethod.GetBinContent(ibin), 2)+pow(hMethod.GetBinError(ibin),2)))
            try: fracerr = hMethod.GetBinError(ibin)/hMethod.GetBinContent(ibin)
            except: fracerr = 0
            if nj == 3: 
                print 'yeah, using big scale', hmethod.GetName()
                scale = 5.0
            else: scale = 3.0
            #print 'before', hMethod.GetBinContent(ibin)
            hMethod.SetBinContent(ibin,scale*hMethod.GetBinContent(ibin))
            #print 'after', hMethod.GetBinContent(ibin)
            hMethod.SetBinError(ibin,fracerr*hMethod.GetBinContent(ibin))
    return hMethod


def mkLabel(str_,kinvar,selection=''):
    newstr = str_
    if newstr[0]=='h':newstr = newstr[1:]
    newstr = newstr.replace('GenSmeared',' gen-smeared ')
    newstr = newstr.replace('Rebalanced',' rebalanced ')
    if year=='Summer16': newstr = newstr.replace('RplusS',' Summer16 QCD R&S')
    elif year=='Fall17': newstr = newstr.replace('RplusS',' Fall17 QCD R&S')
    if datamc=='Data': newstr = newstr.replace('Truth','Data')
    if year=='Summer16': newstr = newstr.replace('Truth',' Summer16 QCD (truth) ')
    elif year=='Fall17': newstr = newstr.replace('Truth',' Fall17 QCD (truth) ')
    if datamc == 'Data': newstr = newstr.replace('Truth',' Data ')
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

#os.system('cp '+filenameA+' guinnea.root')

fileA = TFile(filenameA)
fileA.ls()
fileB = TFile(filenameB)

htotfitA = fileA.Get('hTotFit')
hpassfitA = fileA.Get('hPassFit')
htotfitB = fileB.Get('hTotFit')
hpassfitB = fileB.Get('hPassFit')
htotfitA.Scale(lumiA)
hpassfitA.Scale(lumiA)
htotfitB.Scale(lumiB)       
hpassfitB.Scale(lumiB)                
failfactor = (htotfitA.Integral()+htotfitB.Integral())/(hpassfitA.Integral()+hpassfitB.Integral())
print 'fail factor', failfactor 


keys = fileA.GetListOfKeys()
keys = sorted(keys,key=lambda thing: thing.GetName())
newfilename = filenameA.replace('Output/','').replace('TruthAndMethod','Closure')
newfile = TFile('closure_rands.root','recreate')
#newfile.ls()

#for Pair in PairsToCompare:
for key in keys:
    #if not ('GenSmeared' in key.GetName() or 'Rebalanced' in key.GetName() or 
    if not ('RplusS' in key.GetName()): continue
    if not ('GenSmeared' in key.GetName() or 'RplusS' in key.GetName()): continue
    #if 'Vs' in key.GetName(): continue
    #if not 'Mht' in key.GetName(): continue
    kinvar = key.GetName().replace('GenSmeared','').replace('Rebalanced','').replace('RplusS','')
    selection = kinvar[1:kinvar.find('_')]
    kinvar = kinvar[kinvar.find('_')+1:]
    if '_' in kinvar: continue
    print 'kinvar=', kinvar
    print 'here'    
    #if not 'DPhiJet1Mht' in kinvar: continue
    if 'GenSmeared' in key.GetName(): 
        method = 'GenSmeared'
        standard = 'Truth'
    if 'Rebalanced' in key.GetName(): 
        method = 'Rebalanced'
        standard = 'Gen'
    if 'RplusS' in key.GetName():
        method = 'RplusS'
        #standard = 'GenSmeared'
        standard = 'Truth'
        if datamc == 'Data':
            method = 'RplusS'
            standard = 'Truth'
    hTruth = fileA.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hTruth.Scale(lumiA)
    hTruthB = fileB.Get('h'+selection+'_'+kinvar+standard).Clone('h'+selection+'_'+kinvar+standard+'')
    hTruthB.Scale(lumiB)    
    hTruth.Add(hTruthB)
    hMethod = fileA.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    hMethod.Scale(lumiA)
    hMethodB = fileB.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    hMethodB.Scale(lumiB)    
    hMethod.Add(hMethodB)
    #if 'SearchBins' in key.GetName(): hMethod = applyCorrections(hMethod, SearchBinNames)    


    if 'RplusS' in key.GetName(): 
        hMethod.Scale(failfactor)


    if datamc == 'Data': col = kGreen
    if datamc == 'MC': col = kBlue
    histoStyler(hTruth, 1)
    histoStyler(hMethod, kGray+1)
    hMethod.SetFillColor(col-5)
    hMethod.SetFillStyle(1002)

    leg = mklegend(x1=.405, y1=.53, x2=.90, y2=.77, color=kWhite)
    cGold = mkcanvas('cEnchilada')#TCanvas('cEnchilada','cEnchilada', 800, 800)
    if len(redoBinning[kinvar])>3: ##this should be reinstated
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hTruth = hTruth.Rebin(nbins,'',newxs)
        hMethod = hMethod.Rebin(nbins,'',newxs)
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hTruth = hTruth.Rebin(nbins,'',newxs)
        hMethod = hMethod.Rebin(nbins,'',newxs)


    hrat, pad1, pad2 = FabDraw(cGold,leg,hTruth,[hMethod],datamc='mc',lumi=round(1.0*lumi/1000,1), title = '', LinearScale=False, fractionthing='predicted/obs.')

    print 'hMethod.Integral(), hTruth.Integral()', hMethod.Integral(), hTruth.Integral(), 'h'+selection+'_'+kinvar+standard
    hrat.GetYaxis().SetRangeUser(-0.5,3.5)
   
    hrat.SetTitle('')
    hrat.GetXaxis().SetTitle(nicelabel(kinvar)+('bin' not in units[kinvar])*(' ['+units[kinvar]+']'))
    hrat.GetYaxis().SetTitle('pred./expectation')
    hrat.GetXaxis().SetTitleSize(0.15)
    hrat.GetXaxis().SetLabelSize(0.165)
    hrat.GetYaxis().SetTitleSize(0.1)
    hrat.GetYaxis().SetLabelSize(0.165)
    hrat.GetYaxis().SetNdivisions(7)
    hrat.GetYaxis().SetTitleOffset(0.42)
    hrat.GetXaxis().SetTitleOffset(0.9)
    hrat.GetXaxis().SetTitle(nicelabel(hrat.GetXaxis().GetTitle()))
    pad2.cd()
    hrat.Draw('e0')
    cGold.Update()   

    cname = (hMethod.GetName()+'_And_'+hTruth.GetName()).replace(' ','')
    cGold.Write(cname)
    print 'trying:','pdfs/ClosureTests/'+selection+'_'+method+'And'+standard+'_'+kinvar+'.pdf'
    cGold.Print('pdfs/ClosureTests/'+selection+'_'+method+'And'+standard+'_'+kinvar+year+'.pdf')


print 'just created', newfile.GetName()
exit(0)
