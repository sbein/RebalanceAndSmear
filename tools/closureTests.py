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

loadSearchBins2016()
SearchBinNames = {v: k for k, v in SearchBinNumbers.iteritems()}

redoBinning = binningAnalysis
redoBinning = binningUser
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


try: filenameA = sys.argv[1]
except:
    print 'please give command like'
    print 'python python/divideMht.py MethodFile TruthFile Electron'
    filenameA = 'Output/TruthAndMethodHT2000.root'

def mkLabel(str_,kinvar,selection=''):
    newstr = str_
    if newstr[0]=='h':newstr = newstr[1:]
    newstr = newstr.replace('GenSmeared',' gen-smeared ')
    newstr = newstr.replace('Rebalanced',' rebalanced ')
    newstr = newstr.replace('RplusS',' Fall17 QCD R&S')
    if datamc=='Data': newstr = newstr.replace('Truth','Data')
    newstr = newstr.replace('Truth',' Fall17 QCD (truth) ')
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

os.system('cp '+filenameA+' guinnea.root')

fileA = TFile('guinnea.root')
fileA.ls()

keys = fileA.GetListOfKeys()
keys = sorted(keys,key=lambda thing: thing.GetName())
newfilename = filenameA.replace('Output/','').replace('TruthAndMethod','Closure')
newfile = TFile('closure_rands.root','recreate')
#newfile.ls()

norm = 1000*lumi
#hNormNum = fileA.Get('hLowMhtBaseline_MhtTruth').Clone('hNormNum')
#hNormNum.Scale(norm)
#hNormDen = fileA.Get('hLowMhtBaseline_MhtRplusS').Clone('hNormDen')
#normNum = hNormNum.Integral(hNormNum.GetXaxis().FindBin(100),hNormNum.GetXaxis().FindBin(150))
#normDen = hNormDen.Integral(hNormDen.GetXaxis().FindBin(100),hNormDen.GetXaxis().FindBin(150))
#norm = 1.0*normNum/normDen 

print 'your normalization is', norm


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

    print 'mucking in truth', hTruth.GetName()
    hTruth.Scale(norm)
    hMethod = fileA.Get('h'+selection+'_'+kinvar+method).Clone('h'+selection+'_'+kinvar+method+'')
    if 'SearchBins' in key.GetName(): hMethod = applyCorrections(hMethod, SearchBinNames)    
    hMethod.Scale(norm)

    try: print 'fail factor', fileA.Get('hTotFit').Integral()/fileA.Get('hPassFit').Integral()
    except: pass
    if 'RplusS' in key.GetName(): 
        try: hMethod.Scale(fileA.Get('hTotFit').Integral()/fileA.Get('hPassFit').Integral())
        except: pass
        
    if datamc == 'Data': col = kGreen
    if datamc == 'MC': col = kBlue
    histoStyler(hTruth, 1)
    histoStyler(hMethod, kGray+1)
    hMethod.SetFillColor(col-5)
    hMethod.SetFillStyle(1002)

    
    cGold = TCanvas('cEnchilada','cEnchilada', 800, 800)
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
            
    pad1 = TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0.0)
    pad1.SetLeftMargin(0.12)
    pad1.SetLogy()
    pad1.SetGridx()
    #pad1.SetGridy()
    pad1.Draw()
    pad1.cd()

    l = mklegend(x1=.5, y1=.64, x2=.93, y2=.79)


    #hTruth.SetMarkerStyle(21)
    name = key.GetName() 
    print name
    hTruth.SetTitle('')
    try:
        vallow = baseline[kinvar]
        binlow = hTruth.GetXaxis().FindBin(vallow)
    except:
        binlow = -1

    ##hMethod.Scale(norm)
    if datamc=='MC':
        hMethod.Scale(1,'width')###
        hTruth.Scale(1,'width')
    if datamc == 'Data': units_ = 'bin'
    units_ = units[kinvar]
    #hMethod.GetYaxis().SetTitle('Events/'+units_)
    hMethod.GetYaxis().SetTitle('Events/bin')

    low = 0.01*hTruth.GetBinContent(hTruth.GetXaxis().GetNbins())
    high = 1000*hTruth.GetMaximum()
    #if 'Jet4Pt' in kinvar or 'Jet3Pt' in kinvar: high = 10*high
    if 'DPhi' in kinvar: 
        high = 100*hTruth.GetMaximum()
        low = 0.1*hTruth.GetBinContent(hTruth.GetXaxis().GetNbins()/2)
    if 'Mht' in kinvar:
        low = 0.001
    if low<0.0000005:low=0.0000005

    hMethod.GetYaxis().SetRangeUser(low,high)

    hTruth.SetMarkerColor(1)
    hTruth.SetMarkerStyle(21)
    hMethod.SetLineColor(kGray+1)
    hMethod.SetTitle('')
    hMethod.Draw('hist E')
    hMethod.Draw('e same')
    hTruth.Draw('E1 same')
    print mkLabel(hMethod.GetName(),kinvar,selection)
    l.AddEntry(hTruth,mkLabel(hTruth.GetName(),kinvar,selection),'lp')
    l.AddEntry(hMethod,mkLabel(hMethod.GetName(),kinvar,selection),'fp')
    l.Draw()

    ybottom = hTruth.GetYaxis().GetBinLowEdge(1)
    ypos = high-(high-ybottom)*0.7# + (high-ybottom)*0.01
    xtop = hTruth.GetXaxis().GetBinUpEdge(hTruth.GetXaxis().GetNbins())
    xbottom = hTruth.GetXaxis().GetBinLowEdge(1)
    xpos = xbottom+(xtop-xbottom)*0.03
    if high>1000000 or high<pow(10,-5):xpos=xpos+0.125*(xtop-xbottom)

    oldalign = tl.GetTextAlign()    
    tl.SetTextFont(cmsTextFont)
    tl.SetTextSize(1.12*tl.GetTextSize())
    tl.DrawLatex(0.14,0.84, 'CMS')
    tl.SetTextFont(extraTextFont)
    tl.SetTextSize(1.0/1.12*tl.GetTextSize())
    if 'SearchBins' in kinvar: xlab = 0.19
    else: xlab = 0.22
    tl.DrawLatex(xlab,0.84, ('MC' in datamc)*' simulation '+'preliminary')
    tl.SetTextFont(regularfont)
    if 'LowMht' in name: cutlabel = mkCutsLabel(kinvar,selection, baselineStrLowMht)
    else: cutlabel = mkCutsLabel(kinvar,selection, baselineStr)
        
    if 'LowDeltaPhi' in selection: cutlabel = cutlabel.replace('200','300')
    print kinvar, 'cutlabel=', cutlabel
    xpos = binning[kinvar][1]+(0.05*(binning[kinvar][-1]-binning[kinvar][1]))######
    #tl.DrawLatex(xpos+0.0, ypos/15.0, cutlabel)
    tl.DrawLatex(0.14,0.925, cutlabel)

    tl.SetTextAlign(31)
    tl.DrawLatex(0.894,0.84,'#sqrt{s} = 13 TeV (L = '+str(lumi)+' fb^{-1})')
    tl.SetTextAlign(oldalign)

    print 'ybottom, xbottom, xpos, ypos', ybottom, xbottom, xpos, ypos
    cGold.Update()
    cGold.cd()
    pad2 = TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.SetTopMargin(0.0)
    pad2.SetBottomMargin(0.37)
    pad2.SetLeftMargin(0.12)
    pad2.SetGridx()
    pad2.SetGridy()
    #pad2.SetLogy()
    pad2.Draw()
    pad2.cd()

    hFracDiff = fileA.Get('h'+selection+'_'+kinvar+method).Clone('hFracDiff')###hacks!
    if 'SearchBins' in key.GetName(): hFracDiff = applyCorrections(hFracDiff, SearchBinNames)    
    hFracDiff.Scale(norm)
    hDen = fileA.Get('h'+selection+'_'+kinvar+standard).Clone('hDen')
    hFracDiff.SetMarkerStyle(20)
    hFracDiff.SetMarkerColor(1)
    hDen.SetMarkerStyle(20)
    hDen.SetMarkerColor(1)    
    histoStyler(hFracDiff, 1)
    histoStyler(hDen, 1)
    if len(redoBinning[kinvar])>3: 
        nbins = len(redoBinning[kinvar])-1
        newxs = array('d',redoBinning[kinvar])
        hFracDiff = hFracDiff.Rebin(nbins,'',newxs)
        hDen = hDen.Rebin(nbins,'',newxs)
    else:
        newbinning = []
        stepsize = round(1.0*(redoBinning[kinvar][2]-redoBinning[kinvar][1])/redoBinning[kinvar][0],4)
        for ibin in range(redoBinning[kinvar][0]+1): newbinning.append(redoBinning[kinvar][1]+ibin*stepsize)
        nbins = len(newbinning)-1
        newxs = array('d',newbinning)
        hFracDiff = hFracDiff.Rebin(nbins,'',newxs)
        hDen = hDen.Rebin(nbins,'',newxs)
    try: hDen.Scale(norm)
    except: pass   
    ###hFracDiff.Add(hDen,-1)#####    
    hFracDiff.Divide(hDen)
    hFracDiff.GetYaxis().SetRangeUser(-0.5,3.5)
    ###hFracDiff.GetYaxis().SetRangeUser(-2.1,2.1)####    

    
    #hFracDiff.GetYaxis().SetRangeUser(0.08,30)####    
    hFracDiff.SetTitle('')
    hFracDiff.GetXaxis().SetTitle(nicelabel(kinvar)+('bin' not in units[kinvar])*(' ['+units[kinvar]+']'))
    #hFracDiff.GetYaxis().SetTitle('pred./expectation')
    hFracDiff.GetYaxis().SetTitle('(pred-exp)/exp')
    hFracDiff.GetXaxis().SetTitleSize(0.165)
    hFracDiff.GetXaxis().SetLabelSize(0.165)
    hFracDiff.GetYaxis().SetTitleSize(0.13)
    hFracDiff.GetYaxis().SetLabelSize(0.165)
    hFracDiff.GetYaxis().SetNdivisions(7)
    hFracDiff.GetYaxis().SetTitleOffset(0.42)
    hFracDiff.GetXaxis().SetTitleOffset(1.0)
    hFracDiff.GetXaxis().SetTitle(nicelabel(hFracDiff.GetXaxis().GetTitle()))
    hFracDiff.Draw('e0')
    cGold.Update()   

    cname = (hMethod.GetName()+'_And_'+hTruth.GetName()).replace(' ','')
    cGold.Write(cname)
    print 'trying:','pdfs/ClosureTests/'+selection+'_'+method+'And'+standard+'_'+kinvar+'.pdf'
    cGold.Print('pdfs/ClosureTests/'+selection+'_'+method+'And'+standard+'_'+kinvar+'.pdf')


print 'just created', newfile.GetName()
exit(0)
