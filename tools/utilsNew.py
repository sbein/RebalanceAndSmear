from ROOT import *
import sys
from array import array
import numpy as np
import random

tl = TLatex()
tl.SetNDC()
cmsTextFont = 61
extraTextFont = 52
lumiTextSize = 0.6
lumiTextOffset = 0.2
cmsTextSize = 0.75
cmsTextOffset = 0.1
regularfont = 42
originalfont = tl.GetTextFont()


BTAG_CSV = 0.8484

def histoStyler(h,color):
    h.SetLineWidth(2)
    h.SetLineColor(color)
    size = 0.065
    font = 132
    h.GetXaxis().SetLabelFont(font)
    h.GetYaxis().SetLabelFont(font)
    h.GetXaxis().SetTitleFont(font)
    h.GetYaxis().SetTitleFont(font)
    h.GetYaxis().SetTitleSize(size)
    h.GetXaxis().SetTitleSize(size)
    h.GetXaxis().SetLabelSize(size)   
    h.GetYaxis().SetLabelSize(size)
    h.GetXaxis().SetTitleOffset(1.0)
    h.GetYaxis().SetTitleOffset(0.9)
    h.Sumw2()


def histoStyler2d(h): 
    h.GetYaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetTitleOffset(1.0)
    size = 0.065
    font = 132
    h.GetXaxis().SetLabelFont(font)
    h.GetYaxis().SetLabelFont(font)
    h.GetXaxis().SetTitleFont(font)
    h.GetYaxis().SetTitleFont(font)
    h.GetYaxis().SetTitleSize(size)
    h.GetXaxis().SetTitleSize(size)
    h.GetXaxis().SetLabelSize(size)   
    h.GetYaxis().SetLabelSize(size)
    h.GetXaxis().SetTitleOffset(1.0)
    h.GetYaxis().SetTitleOffset(1.12)
    h.Sumw2()
    return h




baseline = {}
baseline['Mht'] = 300
baseline['Ht'] = 300
baseline['NJets'] = 2
baseline['BTags'] = 0
baseline['DPhi1'] = 0.5
baseline['DPhi2'] = 0.5
baseline['DPhi3'] = 0.3
baseline['DPhi4'] = 0.3

baselineLowMht = {}
baselineLowMht['Mht'] = 200
baselineLowMht['Ht'] = 300
baselineLowMht['NJets'] = 2
baselineLowMht['BTags'] = 0
baselineLowMht['DPhi1'] = 0.5
baselineLowMht['DPhi2'] = 0.5
baselineLowMht['DPhi3'] = 0.3
baselineLowMht['DPhi4'] = 0.3

baselineStr = {}
baselineStr['Mht']='H_{T}^{miss} > '+str(baseline['Mht'])+' GeV'
baselineStr['Ht']='H_{T} > '+str(baseline['Ht'])+' GeV'
baselineStr['NJets']='N_{jets} #geq '+str(baseline['NJets'])
baselineStr['BTags']=''
baselineStr['DPhi1']='#Delta#phi_{1}'
baselineStr['DPhi2']='#Delta#phi_{2}'
baselineStr['DPhi3']='#Delta#phi_{3}'
baselineStr['DPhi4']='#Delta#phi_{4}'

baselineStrLowMht = {}
baselineStrLowMht['Mht']='H_{T}^{miss} > '+str(baselineLowMht['Mht'])+' GeV'
baselineStrLowMht['Ht']='H_{T} > '+str(baselineLowMht['Ht'])+' GeV'
baselineStrLowMht['NJets']='N_{jets} #geq '+str(baselineLowMht['NJets'])
baselineStrLowMht['BTags']=''
baselineStrLowMht['DPhi1']='#Delta#phi_{1}'
baselineStrLowMht['DPhi2']='#Delta#phi_{2}'
baselineStrLowMht['DPhi3']='#Delta#phi_{3}'
baselineStrLowMht['DPhi4']='#Delta#phi_{4}'


units = {}
units['Mht']='GeV'
units['Met']=units['Mht']
units['Ht']='GeV'
units['NJets']='bin'
units['BTags']='bin'
units['Jet1Pt']='GeV'
units['Jet1Eta']='bin'
units['Jet2Pt']='GeV'
units['Jet2Eta']='bin'
units['Jet3Pt']='GeV'
units['Jet3Eta']='bin'
units['Jet4Pt']='GeV'
units['Jet4Eta']='bin'
units['MhtPhi']='rad'
units['DPhi1']='rad'
units['DPhi2']='rad'
units['DPhi3']='rad'
units['DPhi4']='rad'
units['SearchBins']='bin'
units['MvaLowMht']='bin'
units['MvaLowHt']='bin'
units['Odd']='modulo false'
units['csvAve']=''
units['BestDijetMass']='GeV'
units['MinDeltaM']='GeV'
units['MaxDPhi']='rad'
units['MaxForwardPt'] = 'GeV'


def makehist(hname='hist',var='Mht', color = kBlack):
	if len(binningTrigger[var])==3:
		nbins = binningTrigger[var][0]
		low = binningTrigger[var][1]
		high = binningTrigger[var][2]
		hist = TH1F(hname,hname,nbins,low,high)
	else:
		nBin = len(binningTrigger[var])-1
		binArr = array('d',binningTrigger[var])
		hist = TH1F(hname,hname,nBin,binArr) 
	histoStyler(hist, color) 
	return hist  

def Struct(*args, **kwargs):
    def init(self, *iargs, **ikwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)
        for i in range(len(iargs)):
            setattr(self, args[i], iargs[i])
        for k,v in ikwargs.items():
            setattr(self, k, v)

    name = kwargs.pop("name", "MyStruct")
    kwargs.update(dict((k, None) for k in args))
    return type(name, (object,), {'__init__': init, '__slots__': kwargs.keys()})

def mkHistoStruct(hname, binning):
    if '_' in hname: var = hname[hname.find('_')+1:]
    else: var =  hname
    histoStruct = Struct('Branch','Truth','GenSmeared','Gen','Rebalanced','RplusS')
    if len(binning[var])==3:
        nbins = binning[var][0]
        low = binning[var][1]
        high = binning[var][2]
        histoStruct.Branch = TH1F('h'+hname+'Branch',hname+'Branch',nbins,low,high)
        histoStruct.Truth = TH1F('h'+hname+'Truth',hname+'Truth',nbins,low,high)
        histoStruct.GenSmeared = TH1F('h'+hname+'GenSmeared',hname+'GenSmeared',nbins,low,high)
        histoStruct.Gen = TH1F('h'+hname+'Gen',hname+'Gen',nbins,low,high)
        histoStruct.Rebalanced = TH1F('h'+hname+'Rebalanced',hname+'Rebalanced',nbins,low,high)
        histoStruct.RplusS = TH1F('h'+hname+'RplusS',hname+'RplusS',nbins,low,high)
    else:
        nBin = len(binning[var])-1
        binArr = array('d',binning[var])
        histoStruct.Branch = TH1F('h'+hname+'Branch',hname+'Branch',nBin,binArr)
        histoStruct.Truth = TH1F('h'+hname+'Truth',hname+'Truth',nBin,binArr)
        histoStruct.GenSmeared = TH1F('h'+hname+'GenSmeared',hname+'GenSmeared',nBin,binArr)
        histoStruct.Gen = TH1F('h'+hname+'Gen',hname+'Gen',nBin,binArr)
        histoStruct.Rebalanced = TH1F('h'+hname+'Rebalanced',hname+'Rebalanced',nBin,binArr)
        histoStruct.RplusS = TH1F('h'+hname+'RplusS',hname+'RplusS',nBin,binArr)
    histoStyler(histoStruct.Branch,19)
    histoStyler(histoStruct.Truth,kRed)
    histoStyler(histoStruct.GenSmeared,kBlack)
    histoStyler(histoStruct.Gen,kGreen)
    histoStyler(histoStruct.Rebalanced,kBlue)
    histoStyler(histoStruct.RplusS,kBlack)
    return histoStruct


def writeHistoStruct(hStructDict):
    for key in hStructDict:
        #print 'writing histogram structure:', key
        hStructDict[key].Branch.Write()
        hStructDict[key].Truth.Write()
        hStructDict[key].GenSmeared.Write()
        hStructDict[key].Gen.Write()
        hStructDict[key].Rebalanced.Write()
        hStructDict[key].RplusS.Write()


def mkTag(lo2):
    if lo2[0]==lo2[1]:
        str_ = ' = '+str(lo2[0])
    else:
        str_ = '~['+str(lo2[0])+','+str(lo2[1])+']'
    return str_

def countJets(tlvvec,thresh):
    count = 0
    for j in range(len(tlvvec)):
        if tlvvec[j].Pt()>thresh and abs(tlvvec[j].Eta())<2.4: count+=1
    return count


def countBJets(tlvvec, csvvec,thresh):
    count = 0
    for j in range(len(tlvvec)):
        if tlvvec[j].Pt()>thresh and abs(tlvvec[j].Eta())<2.4 and csvvec[j]>BTAG_CSV: count+=1
    return count


def passesSelectionWithMatching(t, leptype='ele'):
    if not bool(ord(t.JetID)): return False
    if t.NJets<4: return False
    if leptype=='ele': 
        if (t.MuonsNum>0): return False
        if (t.Electrons.size()==0): return False
        matched = False
        for e in range(len(t.Electrons)):
            if not abs(t.genParticles_PDGid[e])==11: continue
            for g in range(len(t.genParticles)):
                if t.Electrons[e].DeltaR(t.genParticles[g])<0.5:
                    matched = True
                    break

def getMatchedCsv_Python(GenJets, RecoJets, CsvVec, histsForHarry):
    CsvVec_ = []
    for ig, gjet in enumerate(GenJets):
        dR = 9
        csv_ = 0
        for ireco, rjet in enumerate(RecoJets):
            dR_ = gjet.DeltaR(rjet)
            if dR_<dR:
                dR=dR_
                csv_ = CsvVec[ireco]
                if dR_<0.25: 
                    if ig==0 and rjet.Pt()>20:histsForHarry[0].Fill(RecoJets[ireco].Pt()/gjet.Pt())
                    if ig==1 and rjet.Pt()>20:histsForHarry[1].Fill(RecoJets[ireco].Pt()/gjet.Pt())                    
                    break
        CsvVec_.append(csv_)
    return CsvVec_

def getMatchedCsv(GenJets, RecoJets, CsvVec, histsForHarry=''):#translate into c++
    CsvVec_ = std.vector('double')()
    for ig, gjet in enumerate(GenJets):
        dR = 9
        csv_ = 0
        for ireco, rjet in enumerate(RecoJets):
            dR_ = gjet.DeltaR(rjet)
            if dR_<dR:
                dR=dR_
                csv_ = CsvVec[ireco]
                if dR_<0.25 and (histsForHarry!=''): 
                    if ig==0 and rjet.Pt()>20:histsForHarry[0].Fill(RecoJets[ireco].Pt()/gjet.Pt())
                    if ig==1 and rjet.Pt()>20:histsForHarry[1].Fill(RecoJets[ireco].Pt()/gjet.Pt())                    
                    break
        CsvVec_.push_back(csv_)
    return CsvVec_


def smearJets(tlvVec, csvVec, histvec, hEtaTemplate, hPtTemplate, n2smear):
    tlvVec_ = []#std.vector('TLorentzVector')()
    csvVec_ = []#std.vector('double')()
    for j in range(len(tlvVec)):   
        tlv = tlvVec[j]
        tlvVec_.append(tlv.Clone())
        csvVec_.append(csvVec[j])        
        if (tlv.Pt()<2 or j>=n2smear): continue   #j>n2smear appears to be a small bug
        ieta = hEtaTemplate.GetXaxis().FindBin(abs(tlv.Eta()))
        ipt = hPtTemplate.GetXaxis().FindBin(tlv.Pt()) 
        rando = histvec[ieta][ipt].GetRandom()
        if rando==float('inf'): 
            rando = 1      
        tlvVec_[-1]*=rando
    tlv_csv = [list(x) for x in zip(*sorted(zip(tlvVec_, csvVec_), key=lambda pair: -pair[0].Pt()))]
    #finalRebJets = std.vector('UsefulJet')()
    finalRebJets = std.vector('TLorentzVector')()
    #for tlv in tlv_csv[0]: finalRebJets.push_back(tlv)
    for tlv in tlv_csv[0]: finalRebJets.push_back(tlv.tlv)
    finalRebCsvs = std.vector('double')()
    for d in tlv_csv[1]: finalRebCsvs.push_back(d)        
    updatedTlv_csv = [finalRebJets, finalRebCsvs]    
    #return tlv_csv
    return updatedTlv_csv


import time
beginning = time.time()
counters = [0 for i in xrange(1000)]
prevTime = time.time()
def uc(i):
    global prevTime
    now = time.time()
    counters[i] += now - prevTime
    prevTime = now
def printResults():
    global prevTime
    for i, x in enumerate(counters):
        print i, x
if time.time()-beginning>10:
    print "it's big!"
    print printResults()
    #exit(0)


def findJetToPin(tlvVec,nparams):
    ht = getHT_Python(tlvVec,thresh)# need this in _CC
    desiredMht = max(0.5*ht,120)
    mhtvec = getMHT(tlvVec,30)
    mhtPt, mhtPhi = mhtvec.Pt(), mhtvec.Phi()
    print 'starting on MHT=', mhtPt
    if mhtPt<desiredMht: 
        return [-1,1.0]
    for i in range(nparams):
        denom = 2*(-pow(desiredMht,2)+pow(tlvVec[i].Pt(),2)+pow(mhtPt,2)+2*(tlvVec[i].Pt())*mhtPt*TMath.Cos(mhtPhi-tlvVec[i].Phi()))
        num = 2*pow(tlvVec[i].Pt(),2)+2*tlvVec[i].Pt()*mhtPt*TMath.Cos(mhtPhi-tlvVec[i].Phi())
        discriminant = 2.0*pow(tlvVec[i].Pt(),2)*(2*pow(desiredMht,2)+pow(mhtPt,2)*(TMath.Cos(2*(mhtPhi-tlvVec[i].Phi()))-1))
        num1 = num+TMath.Sqrt(discriminant)
        num2 = num-TMath.Sqrt(discriminant)
        c1 = num1/denom
        if abs(c1-1)<0.8: return [i,c1]
        c2 = num2/denom
        if abs(c2-1)<0.8: return [i,c2]
    print "couldn't find jet to pin, returning 1"
    return [-2,1.0]



def rebalanceJets(tlvVec, csvVec, fRTemplates, hEtaTemplate, hPtTemplate, fGenMhtTemplates, fGenDPhiTemplates,hHtTemplate,rebThresh, lhdMhtThresh):
    tlvVec_ = std.vector(TLorentzVector)()
    csvVec_ = std.vector(float)()
    tlvUntouched = std.vector(TLorentzVector)()
    csvUntouched = std.vector(float)()
    ptaxis = hPtTemplate.GetXaxis()
    for j in range(len(tlvVec)):
        tlv = tlvVec[j] 
        csv = csvVec[j]    
        if tlv.Pt()<lhdMhtThresh or j>11:
            tlvUntouched.push_back(tlv.Clone())
            csvUntouched.push_back(csv)
            continue      
        clonejet = tlv.Clone()
        tlvVec_.push_back(clonejet)
        csvVec_.push_back(csv)
    nparams = len(tlvVec_)
    ietaNew = array( 'i', [0] )
    iptNew = array( 'i', [0] )
    ipin, cstart = findJetToPin(tlvVec,nparams)
    if ipin==-2: return [[],[],0]#visit this with care perhaps at some point
    print 'found jet to pin:', ipin, cstart
    def fcn( npar, gin, f, par, iflag ):
        prevTime = time.time()
        rebTlvVec_ = std.vector(TLorentzVector)()
        rebCsvVec_ = std.vector(float)()
        prod = array( 'd', [1.0] )
        uc(0)
        for i in range(nparams):
            rebCsvVec_.push_back(csvVec_[i])
            clonejet = tlvVec_[i].Clone()
            rebTlvVec_.push_back(clonejet)
            rebTlvVec_[i]*=1.0/par[i]
            ptNew = rebTlvVec_[i].Pt()
            ietaNew[0] = abs(hEtaTemplate.GetXaxis().FindBin(abs(rebTlvVec_[i].Eta())))# this should never change.
            iptNew[0] = ptaxis.FindBin(ptNew)
            ptBinC = ptaxis.GetBinCenter(iptNew[0])
            #if i==0: print 'templates=', ietaNew, iptNew
            if ptNew-ptBinC>0: otherbin = 1
            else: otherbin = -1
            PtBinOther = ptaxis.GetBinCenter(iptNew[0]+otherbin)
            a = (PtBinOther-ptNew)/(PtBinOther-ptBinC)
            b = (ptNew-ptBinC)/(PtBinOther-ptBinC)
            try: interpolatedFactor = 0.5*(a*fRTemplates[ietaNew[0]][iptNew[0]].Eval(par[i],0,'S') + \
                                           b*fRTemplates[ietaNew[0]][iptNew[0]+otherbin].Eval(par[i],0,'S'))
            except: interpolatedFactor = 1.0
            #interpolatedFactor = fRTemplates[ietaNew[0]][iptNew[0]].Eval(par[i],0,'S')
            prod[0]*=interpolatedFactor
            #prod*=fRTemplates[ietaNew][iptNew].Eval(par[i])#i think this is right.

        #fRTemplates[ietaNew][iptNew].Draw()
        #fRTemplates[ietaNew][iptNew].DrawDerivative('same')
        #c1.Update()
        #pause()
        rht = getHT(rebTlvVec_,30)
        iht = hHtTemplate.GetXaxis().FindBin(rht)

        ibjet, bjet, nbjets = getLeadingBJet2(rebTlvVec_, rebCsvVec_) #perhaps try to do this only when a clever flag flips.
        if nbjets==0:
            leadjet = max(rebTlvVec_, key=lambda p: p.Pt()).Clone()
            fGenMhtTemplate = fGenMhtTemplates[0][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[0][iht]
        elif nbjets==1: 
            leadjet = bjet
            fGenMhtTemplate = fGenMhtTemplates[1][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[1][iht]
        elif nbjets==2:
            leadjet = bjet
            fGenMhtTemplate = fGenMhtTemplates[2][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[2][iht]
        else:
           leadjet = bjet
           fGenMhtTemplate = fGenMhtTemplates[3][iht]
           fGenDPhiTemplate = fGenDPhiTemplates[3][iht]            


        rebTlvVec_ += tlvUntouched
        rMhtVec = getMHT(rebTlvVec_,lhdMhtThresh)
        rmht, rphi = rMhtVec.Pt(), rMhtVec.Phi()
        rMhtVec = TLorentzVector() 
        rMhtVec.SetPtEtaPhiE(rmht,0,rphi,rmht)
        rdphi = rMhtVec.DeltaPhi(leadjet)
        prod[0]*=fGenMhtTemplate.Eval(rmht,0,'s')#try commenting this line. does MHT always go down?
        prod[0]*=fGenDPhiTemplate.Eval(rdphi,0,'s')
        #print par[0], 'prod=',prod[0], 'ipt,eta',ietaNew[0],iptNew[0]

        #llhd = -TMath.Log10(abs(prod[0]))
        llhd = abs(prod[0])
        #print 'lhd =', llhd
        f[0] = -llhd

    gMinuit = TMinuit(nparams)
    gMinuit.SetPrintLevel(-1)
    gMinuit.SetFCN( fcn )
    arglist = array( 'd', nparams*[1.0] )
    try: arglist[0]=0
    except: pass
    ierflg = Long(1)#Long(1982)#
    ###gMinuit.mnexcm( "SET ERR", arglist, 1, ierflg )##can we do without this?  
    for i in range(nparams):#0.95+(0.1*i%1)
        if i==ipin:
            print 'setting param',i,'to',cstart
            gMinuit.mnparm(i,'c'+str(i),cstart,0.05,0.3,3.5,ierflg)
        else:
            gMinuit.mnparm(i,'c'+str(i),1.0,0.05,0.3,3.5,ierflg) #try much larger step size; with MIGRAD too
    gMinuit.SetMaxIterations(10000)
    arglist[0] = 10000
    try:
        arglist[1] = 1
    except: pass
    test = gMinuit.mnexcm( "MINIMIZE", arglist, 2, ierflg )
    amin, edm, errdef = Double(0.18), Double(0.19), Double(0.05)
    nvpar, nparx, icstat = Long(1983), Long(1984), Long(1985)
    gMinuit.mnstat( amin, edm, errdef, nvpar, nparx, icstat )
    gMinuit.mnprin( 3, amin )
    if not (ierflg==0): 
        a = 1
        return [[],[]]
        #fRTemplates[ietaNew[0]][iptNew[0]].SetRange(0.97,1.03)
        #fRTemplates[ietaNew[0]][iptNew[0]].Draw()
        #c1.Update()
        #print 'drew function for', iptNew[0], ietaNew[0], 'evaluated at',fRTemplates[ietaNew[0]][iptNew[0]].Eval(1.00364)
        #pause()
        #return [[],[]]
    currentValue = np.zeros(1,dtype=float)
    currentError = np.zeros(1,dtype=float)
    for i in range(nparams):
        gMinuit.GetParameter (i, currentValue, currentError)
        tlvVec_[i]*=1.0/currentValue[0]
        #tlvVec_[i]*=currentValue[0]

    tlvVec_+=tlvUntouched
    csvVec_+=csvUntouched

    oMhtVec = getMHT(tlvVec,30)
    omht, odphi = oMhtVec.Pt(), oMhtVec.Phi()
    #for j in range(len(tlvVec)): print 'jet',j,tlvVec[j].Pt(), csvVec[j]
    print 'oldmht = ', omht, odphi
    rMhtVec = getMHT(tlvVec_,30)
    rmht, rdphi = rMhtVec.Pt(), rMhtVec.Phi()
    #for j in range(len(tlvVec_)): print 'jet',j,tlvVec_[j].Pt(), csvVec_[j]
    print 'newmht = ', rmht, rdphi
    tlv_csv = [list(x) for x in zip(*sorted(zip(tlvVec_, csvVec_), key=lambda pair: -pair[0].Pt()))]
    finalRebJets = std.vector('TLorentzVector')()
    for tlv in tlv_csv[0]: finalRebJets.push_back(tlv)
    finalRebCsvs = std.vector('double')()
    for d in tlv_csv[1]: finalRebCsvs.push_back(d)        
    tlv_csv.append(nparams)
    #return tlv_csv
    updatedTlv_Csv = [finalRebJets, finalRebCsvs, nparams]
    return updatedTlv_Csv


def rebalanceJets2Met(tlvVec, csvVec, fRTemplates, hEtaTemplate, hPtTemplate, fGenMhtTemplates, fGenDPhiTemplates,hHtTemplate,RecoMetVec,rebThresh):
    tlvVec_ = []
    csvVec_ = []
    tlvUntouched = []
    csvUntouched = []
    ptaxis = hPtTemplate.GetXaxis()
    for j in range(len(tlvVec)):
        tlv = tlvVec[j] 
        csv = csvVec[j]    
        if tlv.Pt()<rebThresh or j>10:
            tlvUntouched.append(tlv.Clone())
            csvUntouched.append(csv)
            continue           
        tlvVec_.append(tlv.Clone())
        csvVec_.append(csv)
    nparams = len(tlvVec_)
    ietaNew = array( 'i', [0] )
    iptNew = array( 'i', [0] )
    ipin, cstart = findJetToPin(tlvVec,nparams)
    if ipin==-2: return [[],[],0]
    print 'found jet to pin:', ipin, cstart

    def fcn( npar, gin, f, par, iflag ):
        #prevTime = time.time()
        rebTlvVec_ = []
        rebCsvVec_ = []
        prod = array( 'd', [1.0] )
        uc(0)
        for i in range(nparams):
            rebCsvVec_.append(csvVec_[i])
            rebTlvVec_.append(tlvVec_[i].Clone())
            rebTlvVec_[i]*=1.0/par[i]
            ptNew = rebTlvVec_[i].Pt()
            ietaNew[0] = abs(hEtaTemplate.GetXaxis().FindBin(abs(rebTlvVec_[i].Eta())))
            iptNew[0] = ptaxis.FindBin(ptNew)
            ptBinC = ptaxis.GetBinCenter(iptNew[0])
            if ptNew-ptBinC>0: otherbin = 1
            else: otherbin = -1
            PtBinOther = ptaxis.GetBinCenter(iptNew[0]+otherbin)
            a = (PtBinOther-ptNew)/(PtBinOther-ptBinC)
            b = (ptNew-ptBinC)/(PtBinOther-ptBinC)
            interpolatedFactor = 0.5*(a*fRTemplates[ietaNew[0]][iptNew[0]].Eval(par[i],0,'S') + b*fRTemplates[ietaNew[0]][iptNew[0]+otherbin].Eval(par[i],0,'S'))
            prod[0]*=interpolatedFactor

        redoneMET = redoMET(RecoMetVec,tlvVec_,rebTlvVec_)
        hybMetPt, hybMetPhi = redoneMET.Pt(), redoneMET.Phi()
        rHybMetVec = mkmet(hybMetPt,hybMetPhi)        
        rht = getHT(rebTlvVec_,30)
        iht = hHtTemplate.GetXaxis().FindBin(rht)
        ibjet, bjet, nbjets = getLeadingBJet2(rebTlvVec_, rebCsvVec_)
        if nbjets==0:
            leadjet = max(rebTlvVec_, key=lambda p: p.Pt())
            fGenMhtTemplate = fGenMhtTemplates[0][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[0][iht]
        elif nbjets==1: 
            leadjet = bjet
            fGenMhtTemplate = fGenMhtTemplates[1][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[1][iht]
        else:
            leadjet = bjet
            fGenMhtTemplate = fGenMhtTemplates[2][iht]
            fGenDPhiTemplate = fGenDPhiTemplates[2][iht]

        rdphi = rHybMetVec.DeltaPhi(leadjet)
        prod[0]*=fGenMhtTemplate.Eval(hybMetPt,0,'s')
        prod[0]*=fGenDPhiTemplate.Eval(rdphi,0,'s')

        llhd = abs(prod[0])
        #llhd = -TMath.Log10(abs(prod[0]))
        #print par[0], 'prod=',prod[0], 'ipt,eta',ietaNew[0],iptNew[0]
        #print 'lhd =', llhd
        f[0] = -llhd

    gMinuit = TMinuit(nparams)
    gMinuit.SetPrintLevel(-1)
    gMinuit.SetFCN( fcn )
    arglist = array( 'd', nparams*[1.0] )
    try: arglist[0]=0
    except: pass
    ierflg = Long(0)#Long(1982)#
    gMinuit.mnexcm( "SET ERR", arglist, 1, ierflg )
    for i in range(nparams):
        if i==ipin:
            print 'setting param',i,'to',cstart
            gMinuit.mnparm(i,'c'+str(i),cstart,0.05,0.3,3.5,ierflg)
        else:
            gMinuit.mnparm(i,'c'+str(i),1.0,0.05,0.3,3.5,ierflg)
    gMinuit.SetMaxIterations(10000)
    arglist[0] = 10000
    try:
        arglist[1] = 1
    except: pass
    test = gMinuit.mnexcm( "MINIMIZE", arglist, 2, ierflg )
    amin, edm, errdef = Double(0.18), Double(0.19), Double(0.05)
    nvpar, nparx, icstat = Long(1983), Long(1984), Long(1985)
    gMinuit.mnstat( amin, edm, errdef, nvpar, nparx, icstat )
    gMinuit.mnprin( 3, amin )
    print 'eierflg = ', ierflg
    if not (ierflg==0): a = 1

    currentValue = np.zeros(1,dtype=float)
    currentError = np.zeros(1,dtype=float)
    for i in range(nparams):
        gMinuit.GetParameter (i, currentValue, currentError)
        tlvVec_[i]*=1.0/currentValue[0]#tlvVec_[i]*=currentValue[0]
    tlvVec_+=tlvUntouched
    csvVec_+=csvUntouched
    print 'oldmet = ', RecoMetVec.Pt()
    redoneMET = redoMET(RecoMetVec,tlvVec,tlvVec_)
    hybMetPt, hybMetPhi = redoneMET.Pt(), redoneMET.Phi()
    print 'newmht = ', hybMetPt
    tlv_csv = [list(x) for x in zip(*sorted(zip(tlvVec_, csvVec_), key=lambda pair: -pair[0].Pt()))]
    tlv_csv.append(nparams)
    return tlv_csv


def getLeadingGenBJet(GenJets, RecoJets):
    for gjet in GenJets:
        for rjet in RecoJets:
            dR_ = gjet.tlv.DeltaR(rjet.tlv)
            if dR_<0.4 and rjet.csv>BTAG_CSV: return gjet
    emptyvec = UsefulJet()
    return emptyvec

def getLeadingBJet(RecoJets, CsvVec):
    for ireco in range(len(RecoJets)):
        if not RecoJets[ireco].Pt()>30: continue
        if CsvVec[ireco]>BTAG_CSV: return [ireco,RecoJets[ireco]]
    emptyvec = TLorentzVector()
    return [-1,emptyvec]

def getLeadingBJet2(RecoJets, CsvVec):
    bjetlist = []
    nbjets = 0
    for ireco in range(len(RecoJets)):
        if not CsvVec[ireco]>BTAG_CSV: continue 
        if not RecoJets[ireco].Pt()>30: continue#########hello, try changing this to 15 and re-observe closure (also consider changing the template)
        bjetlist.append([ireco,RecoJets[ireco].Clone()])
        nbjets+=1
    if len(bjetlist)>0:
        leadbjet = max(bjetlist, key=lambda p: p[1].Pt())###
    else:
        emptyvec = TLorentzVector()
        leadbjet = [-1,emptyvec]
    leadbjet.append(nbjets)
    return leadbjet#this may need validation


def getZleptons(leptons, zlow=70, zhigh=110):
    tlvVec_ = []
    for ilep in range(leptons):
        for jlep in range(ilep):
            matched = False
            m = (leptons[ilep]+leptons[jlep]).M()
            if not (m>zlow and m<zhigh):continue
            tlvVec_.append(leptons(ilep))
            tlvVec.append(leptons(jlep))
    return tlvVec_


def cleanJets(tlvVec, zleptons, zlow=70, zhigh=110):
    tlvVec_ = []
    for tlv in tlvVec:
        matched = False
        for zlepton in zleptons:
            dr = tlv.DeltaR(zlepton)
            if dr<0.4:
                matched = True
                break
        if matched: continue
        tlvVec_.append(tlv)  
    return tlvVec_


def getMHT_Python(tlvVec,thresh):
    mhtvec = TLorentzVector()
    for tlv in tlvVec:
        if not (tlv.Pt()>thresh): continue
        if not (abs(tlv.Eta())<5.0): continue
        mhtvec-=tlv
    return mhtvec


def redoMET_Python(originalMet,originalJets,newJets):
    if not len(originalJets)==len(newJets):
        print 'mismatch'; exit()
    newMET = originalMet.Clone()
    for jet in originalJets:
        newMET+=jet
    for jet in newJets:
        newMET-=jet
    return [newMET.Pt(), newMET.Phi()]


def getHybridMet(GenJets,RecoJets,RecoMetVec,rebThresh):
    matchedRecoJets_ = []
    matchedGenJets_ = []
    indexMatchedList = []
    for gjet in GenJets:
        if not gjet.Pt() > rebThresh: continue
        dR = 9
        bestmatchedreco = gjet
        ireco2save = -1
        for ireco in range(len(RecoJets)):
            if ireco in indexMatchedList: continue
            rjet = RecoJets[ireco]
            dR_ = gjet.DeltaR(rjet)
            if dR_<dR:
                dR=dR_
                bestmatchedreco = rjet
                ireco2save = ireco
                if dR_<0.25: break
        if not dR<0.5: continue
        indexMatchedList.append(ireco)
        matchedRecoJets_.append(bestmatchedreco)
        matchedGenJets_.append(gjet)
    redoneMET = redoMET(RecoMetVec,matchedRecoJets_,matchedGenJets_)    
    hybMetPt, hybMetPhi = redoneMET.Pt(), redoneMET.Phi()
    hybMetVec = mkmet(hybMetPt,hybMetPhi)
    return hybMetVec



def getHT_Python(tlvVec,thresh):
    ht = 0
    for tlv in tlvVec:
        if not (abs(tlv.Eta())<2.4): continue
        if not (tlv.Pt()>thresh): continue
        ht+=tlv.Pt()
    return ht

def getDPhis(metvec,jetvec):
    dphilist = []
    for j in range(4):
        try:dphilist.append(abs(metvec.DeltaPhi(jetvec[j].tlv)))
        except: dphilist.append(-5)
    return dphilist

def getPhis(jetvec,metvec):
    dphilist = []
    for j in range(4):
        try:dphilist.append(jetvec[j].tlv.DeltaPhi(metvec))
        except: dphilist.append(-5)
    return dphilist


def getJetKinematics(jets):
    kinematics = []
    for j in range(4):
        try:
            kinematics.append(jets[j].Pt())
            kinematics.append(jets[j].Eta())
        except: 
            kinematics.append(-11)
            kinematics.append(-11)
    return kinematics

def mkcanvas(name='canvas'):
    c = TCanvas(name,name, 800, 800)
    c.SetTopMargin(0.07)
    c.SetBottomMargin(0.15)
    c.SetLeftMargin(0.19)
    return c

def mklegend(x1=.1105, y1=.53, x2=.3805, y2=.8, color=kWhite):
    lg = TLegend(x1, y1, x2, y2)
    lg.SetFillColor(color)
    lg.SetTextFont(42)
    lg.SetBorderSize(0)
    lg.SetShadowColor(kWhite)
    lg.SetFillStyle(0)
    return lg


def mk2dHistoStruct(hname):
    var1, var2 = hname[hname.find('_')+1:].split('Vs')
    histoStruct = Struct('Branch','Truth','GenSmeared','Gen')
    if len(binning2d[var1])==3 and len(binning2d[var2])==3:
        nbins1 = binning2d[var1][0]
        low1 = binning2d[var1][1]
        high1 = binning2d[var1][2]
        nbins2 = binning2d[var2][0]
        low2 = binning2d[var2][1]
        high2 = binning2d[var2][2]
        histoStruct.Branch = TH2F('h'+hname+'Branch',hname+'Branch',nbins2,low2,high2,nbins1,low1,high1)
        histoStruct.Truth = TH2F('h'+hname+'Truth',hname+'Truth',nbins2,low2,high2,nbins1,low1,high1)
        histoStruct.GenSmeared = TH2F('h'+hname+'GenSmeared',hname+'GenSmeared',nbins2,low2,high2,nbins1,low1,high1)
        histoStruct.Gen = TH2F('h'+hname+'Gen',hname+'Gen',nbins2,low2,high2,nbins1,low1,high1)
        histoStruct.Rebalanced = TH2F('h'+hname+'Rebalanced',hname+'Rebalanced',nbins2,low2,high2,nbins1,low1,high1)
        histoStruct.RplusS = TH2F('h'+hname+'RplusS',hname+'RplusS',nbins2,low2,high2,nbins1,low1,high1)
    elif len(binning2d[var1])==3 and len(binning2d[var2])!=3:
        nbins1 = binning2d[var1][0]
        low1 = binning2d[var1][1]
        high1 = binning2d[var1][2]
        nBin2 = len(binning2d[var2])-1
        binArr2 = array('d',binning2d[var2])
        histoStruct.Branch = TH2F('h'+hname+'Branch',hname+'Branch',nBin2,binArr2,nbins1,low1,high1)
        histoStruct.Truth = TH2F('h'+hname+'Truth',hname+'Truth',nBin2,binArr2,nbins1,low1,high1)
        histoStruct.GenSmeared = TH2F('h'+hname+'GenSmeared',hname+'GenSmeared',nBin2,binArr2,nbins1,low1,high1)
        histoStruct.Gen = TH2F('h'+hname+'Gen',hname+'Gen',nBin2,binArr2,nbins1,low1,high1)
        histoStruct.Rebalanced = TH2F('h'+hname+'Rebalanced',hname+'Rebalanced',nBin2,binArr2,nbins1,low1,high1)
        histoStruct.RplusS = TH2F('h'+hname+'RplusS',hname+'RplusS',nBin2,binArr2,nbins1,low1,high1)
    elif len(binning2d[var1])!=3 and len(binning2d[var2])==3:
        nBin1 = len(binning2d[var1])-1
        binArr1 = array('d',binning2d[var1])
        nbins2 = binning2d[var2][0]
        low2 = binning2d[var2][1]
        high2 = binning2d[var2][2]
        histoStruct.Branch = TH2F('h'+hname+'Branch',hname+'Branch',nbins2,low2,high2,nBin1,binArr1)
        histoStruct.Truth = TH2F('h'+hname+'Truth',hname+'Truth',nbins2,low2,high2,nBin1,binArr1)
        histoStruct.GenSmeared = TH2F('h'+hname+'GenSmeared',hname+'GenSmeared',nbins2,low2,high2,nBin1,binArr1)
        histoStruct.Gen = TH2F('h'+hname+'Gen',hname+'Gen',nbins2,low2,high2,nBin1,binArr1)
        histoStruct.Rebalanced = TH2F('h'+hname+'Rebalanced',hname+'Rebalanced',nbins2,low2,high2,nBin1,binArr1)
        histoStruct.RplusS = TH2F('h'+hname+'RplusS',hname+'RplusS',nbins2,low2,high2,nBin1,binArr1)
    else:
        nBin1 = len(binning2d[var1])-1
        binArr1 = array('d',binning2d[var1])
        nBin2 = len(binning2d[var2])-1
        binArr2 = array('d',binning2d[var2])
        histoStruct.Branch = TH2F('h'+hname+'Branch',hname+'Branch',nBin2,binArr2,nBin1,binArr1)
        histoStruct.Truth = TH2F('h'+hname+'Truth',hname+'Truth',nBin2,binArr2,nBin1,binArr1)
        histoStruct.GenSmeared = TH2F('h'+hname+'GenSmeared',hname+'GenSmeared',nBin2,binArr2,nBin1,binArr1)
        histoStruct.Gen = TH2F('h'+hname+'Gen',hname+'Gen',nBin2,binArr2,nBin1,binArr1)
        histoStruct.Rebalanced = TH2F('h'+hname+'Rebalanced',hname+'Rebalanced',nBin2,binArr2,nBin1,binArr1)
        histoStruct.RplusS = TH2F('h'+hname+'RplusS',hname+'RplusS',nBin2,binArr2,nBin1,binArr1)
    histoStyler(histoStruct.Branch,6)
    histoStyler(histoStruct.Truth,kRed)
    histoStyler(histoStruct.GenSmeared,kBlack)
    histoStyler(histoStruct.Gen,kGreen)
    histoStyler(histoStruct.Rebalanced,kBlue)
    histoStyler(histoStruct.RplusS,kBlack)
    return histoStruct


def pause(thingy='please push enter'):
    import sys
    print thingy
    sys.stdout.flush()
    raw_input('')

def mkmet(metPt, metPhi):
    met = TLorentzVector()
    met.SetPtEtaPhiE(metPt, 0, metPhi, metPt)
    return met


def mkCutsLabel(kinvar,regionselect='', baselineStr_ = baselineStr):
    str_ = ''
    for key in baselineStr:
        if kinvar in key: continue
        if baselineStr_[key]=='': continue
        if kinvar=='Met' and 'miss' in baselineStr_[key]: continue
        if 'Phi' in key and 'LowDeltaPhi' in regionselect: continue
        if 'Jet' in kinvar and 'Jets' not in kinvar and 'Mht' in key: continue
        str_+= baselineStr_[key]+', '
    if len(str_)>1:
        if str_[-2:]==', ':
            str_=str_[:-2]
    if 'LowDeltaPhi' in regionselect: str_+= ', #Delta#phi(inv.)'
    return str_


SearchBinNumbers = {}
templateNJetsAndBTags = []
templateHtAndMht = []
def loadSearchBins2016():
    SearchBinNumbers['Ht-1,Mht-1,NJets-1,BTags-1']=-1
    SearchBinNumbers['Underflow']=0
    SearchBinNumbers['Ht300,Mht300,NJets2,BTags0']=1
    SearchBinNumbers['Ht500,Mht300,NJets2,BTags0']=2
    SearchBinNumbers['Ht1000,Mht300,NJets2,BTags0']=3
    SearchBinNumbers['Ht350,Mht350,NJets2,BTags0']=4
    SearchBinNumbers['Ht500,Mht350,NJets2,BTags0']=5
    SearchBinNumbers['Ht1000,Mht350,NJets2,BTags0']=6
    SearchBinNumbers['Ht500,Mht500,NJets2,BTags0']=7
    SearchBinNumbers['Ht1000,Mht500,NJets2,BTags0']=8
    SearchBinNumbers['Ht750,Mht750,NJets2,BTags0']=9
    SearchBinNumbers['Ht1500,Mht750,NJets2,BTags0']=10
    SearchBinNumbers['Ht300,Mht300,NJets2,BTags1']=11
    SearchBinNumbers['Ht500,Mht300,NJets2,BTags1']=12
    SearchBinNumbers['Ht1000,Mht300,NJets2,BTags1']=13
    SearchBinNumbers['Ht350,Mht350,NJets2,BTags1']=14
    SearchBinNumbers['Ht500,Mht350,NJets2,BTags1']=15
    SearchBinNumbers['Ht1000,Mht350,NJets2,BTags1']=16
    SearchBinNumbers['Ht500,Mht500,NJets2,BTags1']=17
    SearchBinNumbers['Ht1000,Mht500,NJets2,BTags1']=18
    SearchBinNumbers['Ht750,Mht750,NJets2,BTags1']=19
    SearchBinNumbers['Ht1500,Mht750,NJets2,BTags1']=20
    SearchBinNumbers['Ht300,Mht300,NJets2,BTags2']=21
    SearchBinNumbers['Ht500,Mht300,NJets2,BTags2']=22
    SearchBinNumbers['Ht1000,Mht300,NJets2,BTags2']=23
    SearchBinNumbers['Ht350,Mht350,NJets2,BTags2']=24
    SearchBinNumbers['Ht500,Mht350,NJets2,BTags2']=25
    SearchBinNumbers['Ht1000,Mht350,NJets2,BTags2']=26
    SearchBinNumbers['Ht500,Mht500,NJets2,BTags2']=27
    SearchBinNumbers['Ht1000,Mht500,NJets2,BTags2']=28
    SearchBinNumbers['Ht750,Mht750,NJets2,BTags2']=29
    SearchBinNumbers['Ht1500,Mht750,NJets2,BTags2']=30 
    SearchBinNumbers['Ht300,Mht300,NJets3,BTags0']=31
    SearchBinNumbers['Ht500,Mht300,NJets3,BTags0']=32
    SearchBinNumbers['Ht1000,Mht300,NJets3,BTags0']=33
    SearchBinNumbers['Ht350,Mht350,NJets3,BTags0']=34
    SearchBinNumbers['Ht500,Mht350,NJets3,BTags0']=35
    SearchBinNumbers['Ht1000,Mht350,NJets3,BTags0']=36
    SearchBinNumbers['Ht500,Mht500,NJets3,BTags0']=37
    SearchBinNumbers['Ht1000,Mht500,NJets3,BTags0']=38
    SearchBinNumbers['Ht750,Mht750,NJets3,BTags0']=39
    SearchBinNumbers['Ht1500,Mht750,NJets3,BTags0']=40 
    SearchBinNumbers['Ht300,Mht300,NJets3,BTags1']=41
    SearchBinNumbers['Ht500,Mht300,NJets3,BTags1']=42
    SearchBinNumbers['Ht1000,Mht300,NJets3,BTags1']=43
    SearchBinNumbers['Ht350,Mht350,NJets3,BTags1']=44
    SearchBinNumbers['Ht500,Mht350,NJets3,BTags1']=45
    SearchBinNumbers['Ht1000,Mht350,NJets3,BTags1']=46
    SearchBinNumbers['Ht500,Mht500,NJets3,BTags1']=47
    SearchBinNumbers['Ht1000,Mht500,NJets3,BTags1']=48
    SearchBinNumbers['Ht750,Mht750,NJets3,BTags1']=49
    SearchBinNumbers['Ht1500,Mht750,NJets3,BTags1']=50   
    SearchBinNumbers['Ht300,Mht300,NJets3,BTags2']=51
    SearchBinNumbers['Ht500,Mht300,NJets3,BTags2']=52
    SearchBinNumbers['Ht1000,Mht300,NJets3,BTags2']=53
    SearchBinNumbers['Ht350,Mht350,NJets3,BTags2']=54
    SearchBinNumbers['Ht500,Mht350,NJets3,BTags2']=55
    SearchBinNumbers['Ht1000,Mht350,NJets3,BTags2']=56
    SearchBinNumbers['Ht500,Mht500,NJets3,BTags2']=57
    SearchBinNumbers['Ht1000,Mht500,NJets3,BTags2']=58
    SearchBinNumbers['Ht750,Mht750,NJets3,BTags2']=59
    SearchBinNumbers['Ht1500,Mht750,NJets3,BTags2']=60  
    SearchBinNumbers['Ht300,Mht300,NJets3,BTags3']=61
    SearchBinNumbers['Ht500,Mht300,NJets3,BTags3']=62
    SearchBinNumbers['Ht1000,Mht300,NJets3,BTags3']=63
    SearchBinNumbers['Ht350,Mht350,NJets3,BTags3']=64
    SearchBinNumbers['Ht500,Mht350,NJets3,BTags3']=65
    SearchBinNumbers['Ht1000,Mht350,NJets3,BTags3']=66
    SearchBinNumbers['Ht500,Mht500,NJets3,BTags3']=67
    SearchBinNumbers['Ht1000,Mht500,NJets3,BTags3']=68
    SearchBinNumbers['Ht750,Mht750,NJets3,BTags3']=69
    SearchBinNumbers['Ht1500,Mht750,NJets3,BTags3']=70 
    SearchBinNumbers['Ht300,Mht300,NJets5,BTags0']=71
    SearchBinNumbers['Ht500,Mht300,NJets5,BTags0']=72
    SearchBinNumbers['Ht1000,Mht300,NJets5,BTags0']=73
    SearchBinNumbers['Ht350,Mht350,NJets5,BTags0']=74
    SearchBinNumbers['Ht500,Mht350,NJets5,BTags0']=75
    SearchBinNumbers['Ht1000,Mht350,NJets5,BTags0']=76
    SearchBinNumbers['Ht500,Mht500,NJets5,BTags0']=77
    SearchBinNumbers['Ht1000,Mht500,NJets5,BTags0']=78
    SearchBinNumbers['Ht750,Mht750,NJets5,BTags0']=79
    SearchBinNumbers['Ht1500,Mht750,NJets5,BTags0']=80 
    SearchBinNumbers['Ht300,Mht300,NJets5,BTags1']=81
    SearchBinNumbers['Ht500,Mht300,NJets5,BTags1']=82
    SearchBinNumbers['Ht1000,Mht300,NJets5,BTags1']=83
    SearchBinNumbers['Ht350,Mht350,NJets5,BTags1']=84
    SearchBinNumbers['Ht500,Mht350,NJets5,BTags1']=85
    SearchBinNumbers['Ht1000,Mht350,NJets5,BTags1']=86
    SearchBinNumbers['Ht500,Mht500,NJets5,BTags1']=87
    SearchBinNumbers['Ht1000,Mht500,NJets5,BTags1']=88
    SearchBinNumbers['Ht750,Mht750,NJets5,BTags1']=89
    SearchBinNumbers['Ht1500,Mht750,NJets5,BTags1']=90   
    SearchBinNumbers['Ht300,Mht300,NJets5,BTags2']=91
    SearchBinNumbers['Ht500,Mht300,NJets5,BTags2']=92
    SearchBinNumbers['Ht1000,Mht300,NJets5,BTags2']=93
    SearchBinNumbers['Ht350,Mht350,NJets5,BTags2']=94
    SearchBinNumbers['Ht500,Mht350,NJets5,BTags2']=95
    SearchBinNumbers['Ht1000,Mht350,NJets5,BTags2']=96
    SearchBinNumbers['Ht500,Mht500,NJets5,BTags2']=97
    SearchBinNumbers['Ht1000,Mht500,NJets5,BTags2']=98
    SearchBinNumbers['Ht750,Mht750,NJets5,BTags2']=99
    SearchBinNumbers['Ht1500,Mht750,NJets5,BTags2']=100  
    SearchBinNumbers['Ht300,Mht300,NJets5,BTags3']=101
    SearchBinNumbers['Ht500,Mht300,NJets5,BTags3']=102
    SearchBinNumbers['Ht1000,Mht300,NJets5,BTags3']=103
    SearchBinNumbers['Ht350,Mht350,NJets5,BTags3']=104
    SearchBinNumbers['Ht500,Mht350,NJets5,BTags3']=105
    SearchBinNumbers['Ht1000,Mht350,NJets5,BTags3']=106
    SearchBinNumbers['Ht500,Mht500,NJets5,BTags3']=107
    SearchBinNumbers['Ht1000,Mht500,NJets5,BTags3']=108
    SearchBinNumbers['Ht750,Mht750,NJets5,BTags3']=109
    SearchBinNumbers['Ht1500,Mht750,NJets5,BTags3']=110     
    SearchBinNumbers['Ht500,Mht300,NJets7,BTags0']=111#
    SearchBinNumbers['Ht1000,Mht300,NJets7,BTags0']=112
    SearchBinNumbers['Ht500,Mht350,NJets7,BTags0']=113#
    SearchBinNumbers['Ht1000,Mht350,NJets7,BTags0']=114
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags0']=115
    SearchBinNumbers['Ht1000,Mht500,NJets7,BTags0']=116
    SearchBinNumbers['Ht750,Mht750,NJets7,BTags0']=117
    SearchBinNumbers['Ht1500,Mht750,NJets7,BTags0']=118 
    SearchBinNumbers['Ht500,Mht300,NJets7,BTags1']=119#
    SearchBinNumbers['Ht1000,Mht300,NJets7,BTags1']=120
    SearchBinNumbers['Ht500,Mht350,NJets7,BTags1']=121#
    SearchBinNumbers['Ht1000,Mht350,NJets7,BTags1']=122
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags1']=123
    SearchBinNumbers['Ht1000,Mht500,NJets7,BTags1']=124
    SearchBinNumbers['Ht750,Mht750,NJets7,BTags1']=125
    SearchBinNumbers['Ht1500,Mht750,NJets7,BTags1']=126   
    SearchBinNumbers['Ht500,Mht300,NJets7,BTags2']=127
    SearchBinNumbers['Ht1000,Mht300,NJets7,BTags2']=128
    SearchBinNumbers['Ht500,Mht350,NJets7,BTags2']=129
    SearchBinNumbers['Ht1000,Mht350,NJets7,BTags2']=130
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags2']=131
    SearchBinNumbers['Ht1000,Mht500,NJets7,BTags2']=132
    SearchBinNumbers['Ht750,Mht750,NJets7,BTags2']=133
    SearchBinNumbers['Ht1500,Mht750,NJets7,BTags2']=134 
    SearchBinNumbers['Ht500,Mht300,NJets7,BTags3']=135
    SearchBinNumbers['Ht1000,Mht300,NJets7,BTags3']=136
    SearchBinNumbers['Ht500,Mht350,NJets7,BTags3']=137
    SearchBinNumbers['Ht1000,Mht350,NJets7,BTags3']=138
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags3']=139
    SearchBinNumbers['Ht1000,Mht500,NJets7,BTags3']=140
    SearchBinNumbers['Ht750,Mht750,NJets7,BTags3']=141
    SearchBinNumbers['Ht1500,Mht750,NJets7,BTags3']=142
    SearchBinNumbers['Ht500,Mht300,NJets9,BTags0']=143
    SearchBinNumbers['Ht1000,Mht300,NJets9,BTags0']=144
    SearchBinNumbers['Ht500,Mht350,NJets9,BTags0']=145
    SearchBinNumbers['Ht1000,Mht350,NJets9,BTags0']=146
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags0']=147
    SearchBinNumbers['Ht1000,Mht500,NJets9,BTags0']=148
    SearchBinNumbers['Ht750,Mht750,NJets9,BTags0']=149
    SearchBinNumbers['Ht1500,Mht750,NJets9,BTags0']=150 
    SearchBinNumbers['Ht500,Mht300,NJets9,BTags1']=151
    SearchBinNumbers['Ht1000,Mht300,NJets9,BTags1']=152
    SearchBinNumbers['Ht500,Mht350,NJets9,BTags1']=153
    SearchBinNumbers['Ht1000,Mht350,NJets9,BTags1']=154
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags1']=155
    SearchBinNumbers['Ht1000,Mht500,NJets9,BTags1']=156
    SearchBinNumbers['Ht750,Mht750,NJets9,BTags1']=157
    SearchBinNumbers['Ht1500,Mht750,NJets9,BTags1']=158   
    SearchBinNumbers['Ht500,Mht300,NJets9,BTags2']=159
    SearchBinNumbers['Ht1000,Mht300,NJets9,BTags2']=160
    SearchBinNumbers['Ht500,Mht350,NJets9,BTags2']=161
    SearchBinNumbers['Ht1000,Mht350,NJets9,BTags2']=162
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags2']=163
    SearchBinNumbers['Ht1000,Mht500,NJets9,BTags2']=164
    SearchBinNumbers['Ht750,Mht750,NJets9,BTags2']=165
    SearchBinNumbers['Ht1500,Mht750,NJets9,BTags2']=166  
    SearchBinNumbers['Ht500,Mht300,NJets9,BTags3']=167
    SearchBinNumbers['Ht1000,Mht300,NJets9,BTags3']=168
    SearchBinNumbers['Ht500,Mht350,NJets9,BTags3']=169
    SearchBinNumbers['Ht1000,Mht350,NJets9,BTags3']=170
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags3']=171
    SearchBinNumbers['Ht1000,Mht500,NJets9,BTags3']=172
    SearchBinNumbers['Ht750,Mht750,NJets9,BTags3']=173
    SearchBinNumbers['Ht1500,Mht750,NJets9,BTags3']=174 
    SearchBinNumbers['Ht9999,Mht999,NJets9,BTags9']=175       
templateHtAndMht = [[[300,500],[300,350]],[[500,1000],[300,350]],[[1000,9999],[300,350]],[[350,500],[350,500]],[[500,1000],[350,500]],[[1000,9999],[350,500]],[[500,1000],[500,750]],[[1000,9999],[500,750]],[[750,1500],[750,9999]],[[1500,9999],[750,9999]]]
templateNJetsAndBTags = [[[2,2],[0,0]],[[2,2],[1,1]],[[2,2],[2,2]],[[3,4],[0,0]],[[3,4],[1,1]],[[3,4],[2,2]],[[3,4],[3,9999]],[[5,6],[0,0]],[[5,6],[1,1]],[[5,6],[2,2]],[[5,6],[3,9999]],[[7,8],[0,0]],[[7,8],[1,1]],[[7,8],[2,2]],[[7,8],[3,9999]],[[9,9999],[0,0]],[[9,9999],[1,1]],[[9,9999],[2,2]],[[9,9999],[3,9999]]]

def loadSearchBins2015():
    SearchBinNumbers['Ht-1,Mht-1,NJets-1,BTags-1']=-1
    SearchBinNumbers['Ht500,Mht200,NJets4,BTags0']=1
    SearchBinNumbers['Ht800,Mht200,NJets4,BTags0']=2
    SearchBinNumbers['Ht1200,Mht200,NJets4,BTags0']=3
    SearchBinNumbers['Ht500,Mht500,NJets4,BTags0']=4
    SearchBinNumbers['Ht1200,Mht500,NJets4,BTags0']=5
    SearchBinNumbers['Ht800,Mht750,NJets4,BTags0']=6
    SearchBinNumbers['Ht500,Mht200,NJets4,BTags1']=7
    SearchBinNumbers['Ht800,Mht200,NJets4,BTags1']=8
    SearchBinNumbers['Ht1200,Mht200,NJets4,BTags1']=9
    SearchBinNumbers['Ht500,Mht500,NJets4,BTags1']=10
    SearchBinNumbers['Ht1200,Mht500,NJets4,BTags1']=11
    SearchBinNumbers['Ht800,Mht750,NJets4,BTags1']=12
    SearchBinNumbers['Ht500,Mht200,NJets4,BTags2']=13
    SearchBinNumbers['Ht800,Mht200,NJets4,BTags2']=14
    SearchBinNumbers['Ht1200,Mht200,NJets4,BTags2']=15
    SearchBinNumbers['Ht500,Mht500,NJets4,BTags2']=16
    SearchBinNumbers['Ht1200,Mht500,NJets4,BTags2']=17
    SearchBinNumbers['Ht800,Mht750,NJets4,BTags2']=18
    SearchBinNumbers['Ht500,Mht200,NJets4,BTags3']=19
    SearchBinNumbers['Ht800,Mht200,NJets4,BTags3']=20
    SearchBinNumbers['Ht1200,Mht200,NJets4,BTags3']=21
    SearchBinNumbers['Ht500,Mht500,NJets4,BTags3']=22
    SearchBinNumbers['Ht1200,Mht500,NJets4,BTags3']=23
    SearchBinNumbers['Ht800,Mht750,NJets4,BTags3']=24
    SearchBinNumbers['Ht500,Mht200,NJets7,BTags0']=25
    SearchBinNumbers['Ht800,Mht200,NJets7,BTags0']=26
    SearchBinNumbers['Ht1200,Mht200,NJets7,BTags0']=27
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags0']=28
    SearchBinNumbers['Ht1200,Mht500,NJets7,BTags0']=29
    SearchBinNumbers['Ht800,Mht750,NJets7,BTags0']=30
    SearchBinNumbers['Ht500,Mht200,NJets7,BTags1']=31
    SearchBinNumbers['Ht800,Mht200,NJets7,BTags1']=32
    SearchBinNumbers['Ht1200,Mht200,NJets7,BTags1']=33
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags1']=34
    SearchBinNumbers['Ht1200,Mht500,NJets7,BTags1']=35
    SearchBinNumbers['Ht800,Mht750,NJets7,BTags1']=36
    SearchBinNumbers['Ht500,Mht200,NJets7,BTags2']=37
    SearchBinNumbers['Ht800,Mht200,NJets7,BTags2']=38
    SearchBinNumbers['Ht1200,Mht200,NJets7,BTags2']=39
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags2']=40
    SearchBinNumbers['Ht1200,Mht500,NJets7,BTags2']=41
    SearchBinNumbers['Ht800,Mht750,NJets7,BTags2']=42
    SearchBinNumbers['Ht500,Mht200,NJets7,BTags3']=43
    SearchBinNumbers['Ht800,Mht200,NJets7,BTags3']=44
    SearchBinNumbers['Ht1200,Mht200,NJets7,BTags3']=45
    SearchBinNumbers['Ht500,Mht500,NJets7,BTags3']=46
    SearchBinNumbers['Ht1200,Mht500,NJets7,BTags3']=47
    SearchBinNumbers['Ht800,Mht750,NJets7,BTags3']=48
    SearchBinNumbers['Ht500,Mht200,NJets9,BTags0']=49
    SearchBinNumbers['Ht800,Mht200,NJets9,BTags0']=50
    SearchBinNumbers['Ht1200,Mht200,NJets9,BTags0']=51
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags0']=52
    SearchBinNumbers['Ht1200,Mht500,NJets9,BTags0']=53
    SearchBinNumbers['Ht800,Mht750,NJets9,BTags0']=54
    SearchBinNumbers['Ht500,Mht200,NJets9,BTags1']=55
    SearchBinNumbers['Ht800,Mht200,NJets9,BTags1']=56
    SearchBinNumbers['Ht1200,Mht200,NJets9,BTags1']=57
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags1']=58
    SearchBinNumbers['Ht1200,Mht500,NJets9,BTags1']=59
    SearchBinNumbers['Ht800,Mht750,NJets9,BTags1']=60
    SearchBinNumbers['Ht500,Mht200,NJets9,BTags2']=61
    SearchBinNumbers['Ht800,Mht200,NJets9,BTags2']=62
    SearchBinNumbers['Ht1200,Mht200,NJets9,BTags2']=63
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags2']=64
    SearchBinNumbers['Ht1200,Mht500,NJets9,BTags2']=65
    SearchBinNumbers['Ht800,Mht750,NJets9,BTags2']=66
    SearchBinNumbers['Ht500,Mht200,NJets9,BTags3']=67
    SearchBinNumbers['Ht800,Mht200,NJets9,BTags3']=68
    SearchBinNumbers['Ht1200,Mht200,NJets9,BTags3']=69
    SearchBinNumbers['Ht500,Mht500,NJets9,BTags3']=70
    SearchBinNumbers['Ht1200,Mht500,NJets9,BTags3']=71
    SearchBinNumbers['Ht800,Mht750,NJets9,BTags3']=72
    templateHtAndMht = [[[500,800],[200,500]], [[800,1200],[200,500]],[[1200,9999],[200,500]],[[500,1200],[500,750]],[[1200,9999],[500,750]],[[800,9999],[750,9999]]]##2015!!!
    templateNJetsAndBTags = [[[4,6],[0,0]],[[4,6],[1,1]],[[4,6],[2,2]],[[4,6],[3,9999]],[[7,8],[0,0]],[[7,8],[1,1]],[[7,8],[2,2]],[[7,8],[3,9999]],[[9,9999],[0,0]],[[9,9999],[1,1]],[[9,9999],[2,2]],[[9,9999],[3,9999]]]


def makeSearchBinString(fv):
    mht = 0
    ht = 0
    nj = 0
    nb = 0
    landedHM = False
    for region in templateHtAndMht:
        if fv[0]>=region[0][0] and fv[0]<region[0][1] and fv[1]>=region[1][0] and fv[1]<region[1][1]:
            ht = region[0][0]
            mht = region[1][0]
            landedHM = True
            break
    if not landedHM: return 'Ht'+str(-1)+',Mht'+str(-1)+',NJets'+str(-1)+',BTags'+str(-1) 
    landedJB = False       
    for region in templateNJetsAndBTags:
        if fv[2]>=region[0][0] and fv[2]<=region[0][1] and fv[3]>=region[1][0] and fv[3]<=region[1][1]:
            nj = region[0][0]
            nb = region[1][0]
            landedJB = True
            break
    if not landedJB: return 'Ht'+str(-1)+',Mht'+str(-1)+',NJets'+str(-1)+',BTags'+str(-1) 
    return 'Ht'+str(ht)+',Mht'+str(mht)+',NJets'+str(nj)+',BTags'+str(nb)

def getBinNumber(fv):# a bit dangerous, so the binning better be right.
    #sb = makeSearchBinString(fv)
    #return SearchBinNumbers[sb]
    if fv[1]<300: return -1
    try: 
        sb = makeSearchBinString(fv)
        return SearchBinNumbers[sb]
    except: 
        return -1

#not extremely needed:
def selection(Ht,Mht,NJets,BTags,nminus1var = ''):
    if not 'NJets' in nminus1var:
        if not (NJets>=7 and  NJets<=8): return False
    if not 'Ht' in nminus1var:
        if not Ht>baseline['Ht']: return False
    if not ('Mht' in nminus1var or 'Met' in nminus1var):
        if not Mht>baseline['Mht']: return False
    return True

'''
def passQCDHighMETFilter(t):
    metvec = mkmet(t.MET, t.METPhi)
    for ijet, jet in enumerate(t.Jets):
        muEn = t.Jets_muonEnergyFraction[ijet]*jet.Pt()
        if not (muEn > 200): continue
        if not (t.Jets_muonEnergyFraction[ijet]>0.5):continue 
        if (abs(jet.DeltaPhi(metvec))-3.14159 < 0.4): return False
    return True
'''
def passQCDHighMETFilter(t):
    metvec = mkmet(t.MET, t.METPhi)
    for ijet, jet in enumerate(t.Jets):
        if not (jet.Pt() > 200): continue
        if not (t.Jets_muonEnergyFraction[ijet]>0.5):continue 
        if (abs(jet.DeltaPhi(metvec)) > (3.14159 - 0.4)): return False
    return True

def passesUniversalSelection(t):
    if not (bool(t.JetID) and  t.NVtx>0): return False
    if not (t.NElectrons==0 and t.NMuons==0 and t.isoElectronTracks==0 and t.isoMuonTracks==0 and t.isoPionTracks==0): return False
    if not  passQCDHighMETFilter(t): return False
    if not t.PFCaloMETRatio<5: return False

    #featuring:
    #if not t.globalTightHalo2016Filter: return False ##this alone was good # only these comments weren't saved on last submission
    if not t.globalSuperTightHalo2016Filter: return False
    if not t.HBHEIsoNoiseFilter: return False
    if not t.HBHENoiseFilter: return False
    if not t.BadChargedCandidateFilter: return False
    if not t.BadPFMuonFilter: return False
    if not t.CSCTightHaloFilter: return False
    if not t.eeBadScFilter: return False     

    '''#first half filters up edge
    if not t.EcalDeadCellTriggerPrimitiveFilter: return False    
    #first half filters low edge           
    ####if not t.ecalBadCalibFilter: return False #this says it's deprecated

    '''#second half filters low edge               
    return True


def passesUniversalDataSelection(t):#first figure out why crashing, then run with isomuon tracks
    if not (bool(t.JetID) and  t.NVtx>0): return False
    #from jack
    if not (t.HBHENoiseFilter==1 and t.HBHEIsoNoiseFilter==1 and t.eeBadScFilter==1 and t.EcalDeadCellTriggerPrimitiveFilter==1 and t.BadChargedCandidateFilter and t.BadPFMuonFilter): return False #might need CSCTightHaloFilter
    if not (t.globalTightHalo2016Filter==1): return False # for data only?
    if not (t.Electrons.size()==0 and t.Muons.size()==0 and t.isoElectronTracks==0 and t.isoMuonTracks==0 and t.isoPionTracks==0): return False
    if not  passQCDHighMETFilter(t): return False
    if not t.PFCaloMETRatio<5: return False
    return True


def passesUniversalSkimSelection(t):#first figure out why crashing, then run with isomuon tracks
    jacksselection = t.globalTightHalo2016Filter==1 and t.HBHENoiseFilter==1 and t.HBHEIsoNoiseFilter==1 and t.eeBadScFilter==1 and t.EcalDeadCellTriggerPrimitiveFilter==1 and t.BadChargedCandidateFilter and t.BadPFMuonFilter and t.NVtx > 0
    jacksselection = jacksselection and (t.Electrons.size()==0 and t.Muons.size()==0)# and t.isoElectronTracks==0 and t.isoMuonTracks==0 and t.isoPionTracks==0)
    return jacksselection

def passesForwardJetID(t):
    jetid = True
    for ijet, jet in enumerate(t.Jets):
        if not (abs(jet.Eta())>2.7): continue
        #if not (t.Jets_neutralEmEnergyFraction[ijet]>0.01): return False
        if not (t.Jets_neutralHadronEnergyFraction[ijet]<0.98): return False
        #if not (t.Jets_neutralHadronMultiplicity[ijet]>2): return False
        #if not (abs(jet.Eta())>3.0): continue
        #if not (t.Jets_neutralEmEnergyFraction[ijet]<0.9): return False
        #if not (t.Jets_neutralHadronMultiplicity[ijet]>10): return False
    return True



#varlist = ['Ht','Mht','NJets','BTags','DPhi1','DPhi2','DPhi3','DPhi4','Jet1Pt','Jet1Eta','Jet2Pt','Jet2Eta','Jet3Pt','Jet3Eta','Jet4Pt','Jet4Eta','Met','MhtPhi','SearchBins']
def growTree(tree, fv, aux, weight):
    ____ht[0] = fv[0]
    _mht[0] = fv[1]
    _njets[0] = fv[2]
    _btags[0] = fv[3]
    _jet1pt[0] = aux[0][0]
    _jet1eta[0] = aux[0][1]
    _jet1phi[0] = aux[0][2]
    _jet2pt[0] = aux[1][0]
    _jet2eta[0] = aux[1][1]
    _jet2phi[0] = aux[1][2]
    _jet3pt[0] = aux[2][0]
    _jet3eta[0] = aux[2][1]
    _jet3phi[0] = aux[2][2]
    _jet4pt[0] = aux[3][0]
    _jet4eta[0] = aux[3][1]
    _jet4phi[0] = aux[3][2]
    _mhtphi[0] = aux[4]
    _bestDijetMass[0] = fv[8]
    _minDeltaM[0] = fv[9]    
    _weight[0] = weight
    tree.Fill()


ScaleFactors74x = [[[0.0,0.8],[1.061,0.023]],\
                   [[0.8,1.3],[1.088,0.029]],\
                   [[1.3,1.9],[1.106,0.030]],\
                   [[1.9,2.5],[1.126,0.094]],\
                   [[2.5,3.0],[1.343,0.123]],\
                   [[3.0,3.2],[1.303,0.111]],\
                   [[3.2,5.0],[1.320,0.286]]]


ScaleFactors80x = [[[0.0,0.5],[1.122, 0.026]],\
                   [[0.5,0.8],[1.167, 0.048]],\
                   [[0.8,1.1],[1.168, 0.046]],\
                   [[1.1,1.3],[1.029, 0.066]],\
                   [[1.3,1.7],[1.115, 0.030]],\
                   [[1.7,1.9],[1.041, 0.062]],\
                   [[1.9,2.1],[1.167, 0.086]],\
                   [[2.1,2.3],[1.094, 0.093]],\
                   [[2.3,2.5],[1.168, 0.120]],\
                   [[2.5,2.8],[1.266, 0.132]],\
                   [[2.8,3.0],[1.595, 0.175]],\
                   [[3.0,3.2],[0.998, 0.066]],\
                   [[3.2,5.0],[1.226, 0.145]]]

def getScaleFactor74x(eta):
    for sfBall in ScaleFactors74x:
        if eta>=sfBall[0][0] and eta<=sfBall[0][1]:
            return [sfBall[1][0], sfBall[1][1]]
    print "didn't find any scale factor!", eta
    exit(0)


def getScaleFactor80x(eta):
    for sfBall in ScaleFactors80x:
        if eta>=sfBall[0][0] and eta<=sfBall[0][1]:
            return [sfBall[1][0], sfBall[1][1]]
    print "didn't find any scale factor!", eta
    exit(0)


def calcSumPt(jets, obj, conesize=0.6, thresh=10):
	sumpt_ = 0
	for jet in jets:
		if not jet.Pt()>thresh:
			continue
		if not (obj.DeltaR(jet.tlv)<conesize):
			continue
		sumpt_+=jet.Pt()
	return sumpt_

epsilon = 0.0001
def fillth1(h,x,weight=1):
	h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon),weight)

def fillth2(h,x,y,weight=1):
	h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon), min(max(y,h.GetYaxis().GetBinLowEdge(1)+epsilon),h.GetYaxis().GetBinLowEdge(h.GetYaxis().GetNbins()+1)-epsilon),weight)

def GetHighestPtForwardPt_prefiring(jets):
    highestPt = 0
    for jet in jets:
        if abs(jet.Eta())>2.25 and abs(jet.Eta())<5.0:#prefiring upper eta is 3.0
            if jet.Pt()>highestPt:
                highestPt = jet.Pt()
    return highestPt
    
    
'''
0: HLT_DoubleEle24_22_eta2p1_WPLoose_Gsf_v
1: HLT_DoubleEle8_CaloIdM_Mass8_PFHT300_v
2: HLT_DoubleEle8_CaloIdM_TrackIdM_Mass8_PFHT250_v
3: HLT_DoubleJet90_Double30_TripleCSV0p5_v
4: HLT_DoubleMu18NoFiltersNoVtx_v
5: HLT_DoubleMu8_Mass8_PFHT250_v
6: HLT_DoubleMu8_Mass8_PFHT300_v
7: HLT_Ele15_IsoVVVL_PFHT350_PFMET50_v
8: HLT_Ele15_IsoVVVL_PFHT350_PFMET70_v
9: HLT_Ele15_IsoVVVL_PFHT350_v
10: HLT_Ele15_IsoVVVL_PFHT400_PFMET70_v
11: HLT_Ele15_IsoVVVL_PFHT600_v
12: HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v
13: HLT_Ele23_WPLoose_Gsf_v
14: HLT_Ele27_WP85_Gsf_v
15: HLT_Ele27_eta2p1_WP85_Gsf_v
16: HLT_Ele27_eta2p1_WPLoose_Gsf_v
17: HLT_IsoMu17_eta2p1_v
18: HLT_IsoMu20_eta2p1_IterTrk02_v
19: HLT_IsoMu20_eta2p1_v
20: HLT_Mu15_IsoVVVL_BTagCSV07_PFHT400_v
21: HLT_Mu15_IsoVVVL_BTagCSV0p72_PFHT400_v
22: HLT_Mu15_IsoVVVL_PFHT350_PFMET50_v
23: HLT_Mu15_IsoVVVL_PFHT350_PFMET70_v
24: HLT_Mu15_IsoVVVL_PFHT350_v
25: HLT_Mu15_IsoVVVL_PFHT400_PFMET70_v
26: HLT_Mu15_IsoVVVL_PFHT600_v
27: HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v
28: HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v
29: HLT_Mu20_v
30: HLT_Mu45_eta2p1_v
31: HLT_Mu50_eta2p1_v
32: HLT_Mu50_v
33: HLT_Mu55_v
34: HLT_PFHT200_v2
35: HLT_PFHT250_v2
36: HLT_PFHT300_v2
37: HLT_PFHT350_PFMET100_JetIdCleaned_v
38: HLT_PFHT350_PFMET100_NoiseCleaned_v
39: HLT_PFHT350_PFMET100_v
40: HLT_PFHT350_PFMET120_NoiseCleaned_v
41: HLT_PFHT350_v
42: HLT_PFHT350_v3
43: HLT_PFHT400_SixJet30_BTagCSV0p55_2PFBTagCSV0p72_v
44: HLT_PFHT400_v2
45: HLT_PFHT450_SixJet40_PFBTagCSV0p72_v
46: HLT_PFHT475_v2
47: HLT_PFHT600_v3
48: HLT_PFHT650_v3
49: HLT_PFHT750_4JetPt50_v
50: HLT_PFHT800_v
51: HLT_PFHT800_v2
52: HLT_PFHT900_v
53: HLT_PFMET170_JetIdCleaned_v
54: HLT_PFMET170_NoiseCleaned_v
55: HLT_PFMETNoMu90_JetIdCleaned_PFMHTNoMu90_IDTight_v
56: HLT_PFMETNoMu90_NoiseCleaned_PFMHTNoMu90_IDTight_v
57: HLT_Photon75_v
58: HLT_Photon90_CaloIdL_PFHT500_v
59: HLT_Photon90_v
60: HLT_QuadJet45_TripleCSV0p5_v
'''
