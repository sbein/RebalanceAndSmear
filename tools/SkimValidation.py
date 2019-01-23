#Welcome to the industrial age of Sam's rebalance and smear code. You're going to have a lot of fun!
import os,sys
from ROOT import *
from array import array
from glob import glob
from utils import *
from ra2blibs import *
import time

mhtjetetacut = 5.0 # also needs be be changed in UsefulJet.h
AnMhtJetPtCut = 30 

debugmode = False

#wget https://github.com/AditeeRane/LostLepton_avgTF/blob/LL_Run2_V16for2016_CMSLPC/btag/L1prefiring_jetpt_2017BtoF.root
#wget https://raw.githubusercontent.com/AditeeRane/LostLepton_avgTF/LL_Run2_V16for2017_CMSLPC/btag/DeepCSV_94XSF_V3_B_F.csv
#wget https://github.com/AditeeRane/LostLepton_avgTF/blob/LL_Run2_V16for2016_CMSLPC/btag/L1prefiring_photonpt_2017BtoF.root

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=0,help="increase output verbosity")
parser.add_argument("-nprint", "--printevery", type=int, default=100,help="print every n(events)")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='tree_TTJets_HT-600to800_MC2017.root',help="file")
parser.add_argument("-jersf", "--JerUpDown", type=str, default='Nom',help="JER scale factor (JerNom, JerUp, ...)")
parser.add_argument("-selection", "--selection", type=str, default='signal',help="signal, LDP")
parser.add_argument("-quickrun", "--quickrun", type=bool, default=False,help="Quick practice run (True, False)")
args = parser.parse_args()
printevery = args.printevery
fnamekeyword = args.fnamekeyword
JerUpDown = args.JerUpDown
selection = args.selection
quickrun = args.quickrun
nametag = {'Nom':'', 'Up': 'JerUp'}
UseDeep = True


ntupleV = '16'

if 'MC2017' in fnamekeyword or 'MC2016' in fnamekeyword: isdata = False
else: isdata = True

is2017f = False

print 'isdata, is2017f', isdata, is2017f

if '_2016' in fnamekeyword or 'MC2016' in fnamekeyword: 
    BTAG_CSVv2 = 0.8484
    BTAG_deepCSV = 0.6324
if '_2017' in fnamekeyword or 'MC2017' in fnamekeyword: 
    BTAG_CSVv2 = 0.8838
    BTAG_deepCSV = 0.4941
    if '2017F' in fnamekeyword: is2017f = True
if '_2018' in fnamekeyword or 'MC2018' in fnamekeyword: 
    BTAG_CSVv2 = 0.8838
    BTAG_deepCSV = 0.4941

if UseDeep: BTag_Cut = BTAG_deepCSV
else: BTag_Cut = BTAG_CSVv2

year = '2015'
year = '2016'
year = 'Run2'
if year=='2015':loadSearchBins2015()
if year=='2016':loadSearchBins2016()
if year=='Run2':loadSearchBins2018()

pwd = os.getcwd()

ujf = open('src/UsefulJet.h.aux')
ujfdata = ujf.read()
ujfdata = ujfdata.replace('double BTAG_CSV = XXX;', 'double BTAG_CSV = %f;' % BTag_Cut)
ujf.close()
ujfu= open('src/UsefulJet.h', 'w')
ujfu.write(ujfdata)
ujfu.close()

gROOT.ProcessLine(open('src/UsefulJet.cc').read())
exec('from ROOT import *')

gROOT.ProcessLine(open('src/BayesRandS.cc').read())
exec('from ROOT import *')

gROOT.ProcessLine(open('src/Met110Mht110FakePho.cpp').read())
exec('from ROOT import *')

gROOT.ProcessLine(open('src/BTagCorrector.h').read())
exec('from ROOT import *')


varlist = ['Ht','Mht','NJets','BTags','SearchBins', 'MaxDPhi', 'MaxForwardPt', 'HtRatio']
indexVar = {}
for ivar, var in enumerate(varlist): indexVar[var] = ivar
indexVar[''] = -1
varlistDPhi = ['DPhi1','DPhi2','DPhi3','DPhi4']
indexVarDPhi = {}
for ivar, var in enumerate(varlistDPhi): indexVarDPhi[var] = ivar
indexVarDPhi['']=-1
nmain = len(varlist)

def selectionFeatureVector(fvector, regionkey='', omitcuts='', omitcuts_dphi=''):
    fvmain, fvdphi, fvfilters = fvector
    if not fvmain[1]>200: return False #let's speed this up a bit
    if not sum(fvfilters)==len(fvfilters): return False
    iomits, iomits_dphi = [], []    
    for cut in omitcuts.split('Vs'): iomits.append(indexVar[cut])
    for i, feature in enumerate(fvmain):
        if i==nmain: break
        if i in iomits: continue
        if not (feature>=regionCuts[regionkey][1][i][0] and feature<=regionCuts[regionkey][1][i][1]): return False
    for cut in omitcuts_dphi.split('Vs'): iomits_dphi.append(indexVarDPhi[cut])    
    if regionCuts[regionkey][0]==0:#high delta phi
        for i, feature in enumerate(fvdphi[:fvmain[2]]):
            if i in iomits_dphi: continue
            if not (feature>=regionCuts[regionkey][2][i][0] and feature<=regionCuts[regionkey][2][i][1]): return False
        return True
    if regionCuts[regionkey][0]==1:#low delta phi
        for i, feature in enumerate(fvdphi[:fvmain[2]]):
            if i in iomits_dphi: continue
            if not (feature>=regionCuts[regionkey][2][i][0] and feature<=regionCuts[regionkey][2][i][1]): return True
        return False 
    print 'should never see this'
    return passmain 


#################
# Scale factors #
#################
# b-tagging
path_bTagCalib = "usefulthings/btag/DeepCSV_94XSF_V3_B_F.csv"
btagcorr = BTagCorrector()

#################
# MadHT ranges #
#################
if 'TTJets_MC' in fnamekeyword:  madranges = [(0,600)]
elif 'TTJets_HT' in fnamekeyword: madranges = [(600,Inf)]
else: madranges = [(0, Inf)]


#################
# Load in chain #
#################
fnamefile = open('usefulthings/filelistSkim_'+selection+'V'+ntupleV+'.txt')
lines = fnamefile.readlines()
fnamefile.close()

c = TChain('tree')
filelist = []
for line in lines:
    shortfname = fnamekeyword
    if not shortfname in line: continue
    fname = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Skims/Run2ProductionV'+ntupleV+'/tree_'+selection+'/'+line#RelValQCD_FlatPt
    fname = fname.strip()
    legalfname = fname.replace('/eos/uscms/','root://cmsxrootd.fnal.gov//')
    print 'adding', legalfname
    c.Add(legalfname)
    filelist.append(legalfname)
    tfile = TFile.Open(legalfname)
    print 'listing'
    tfile.ls()
    btagcorr.SetEffs(tfile)

btagcorr.SetCalib(path_bTagCalib)
btagcorr.SetFastSim(False)

nevents = c.GetEntries()
if quickrun: nevents = min(5000,nevents)
c.Show(0)
print "nevents=", nevents

newFileName = 'Skim_'+filelist[0].split('/')[-1].replace('.root','')+'_'+selection+'.root'
newFileName = newFileName.replace('.root',nametag[JerUpDown]+'.root')
fnew = TFile(newFileName,'recreate')
print 'creating new file:',fnew.GetName()

hHt = TH1F('hHt','hHt',120,0,2500)
hHt.Sumw2()
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',120,0,2500)
hHtWeighted.Sumw2()
hMht = TH1F('hMht','hMht',120,0,2500)
hMht.Sumw2()
hMhtWeighted = TH1F('hMhtWeighted','hMhtWeighted',120,0,2500)
hMhtWeighted.Sumw2()


histoStructDict = {}
for region in regionCuts:
    for var in varlist:
        histname = region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname, binning)
    for var in varlistDPhi:
        histname = region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname, binning)        

#varlist2d
var_pairs = []#[['Mht','Ht'],['Mht',''],['Mht','NJets'],['Mht','DPhi1'],['Mht','DPhi2'],['Mht','DPhi3'],['Mht','DPhi4']]
histo2dStructDict = {}
for region in regionCuts:
    for var_pair in var_pairs:
        hname = region+'_'+var_pair[0]+'Vs'+var_pair[1]
        histo2dStructDict[hname] = mk2dHistoStruct(hname)

if ntupleV=='15': triggerIndeces = triggerIndecesV15
if ntupleV=='15a': triggerIndeces = triggerIndecesV15
if ntupleV=='14': triggerIndeces = triggerIndecesV14
if ntupleV=='16a': triggerIndeces = triggerIndecesV16a

def PassTrig(c,trigname):
    for trigidx in triggerIndeces[trigname]: 
        if c.TriggerPass[trigidx]==1: return True
    return False

c.Show(0)
print 'nevents=', nevents
t0 = time.time()
for ientry in range(nevents):
    if debugmode:
        if ientry<54369: continue    
    if ientry%printevery==0:
        print "processing event", ientry, '/', nevents
        print 'time=',time.time()-t0
    c.GetEntry(ientry)

    if True and ientry==0:
        for itrig in range(len(c.TriggerPass)):
            print itrig, c.TriggerNames[itrig], c.TriggerPrescales[itrig], c.HT
        print '='*20
    if isdata:
        ht = c.HTOnline
        fillth1(hHt, ht)
        fillth1(hMht, c.MHT)
    else:
        gHt = getHT(c.GenJets,AnMhtJetPtCut)
        fillth1(hHt, gHt,1)
        fillth1(hMht, c.MHT,1)
        isValidHtRange = False
        for madrange in madranges:
            if (c.madHT>madrange[0] and c.madHT<madrange[1]):
                isValidHtRange = True
                break 
        if not isValidHtRange: continue        


    if not passesUniversalSelection(c): continue
        

    if UseDeep: recojets = CreateUsefulJetVector(c.Jets, c.Jets_bJetTagDeepCSVBvsAll)#fiducial
    else: recojets = CreateUsefulJetVector(c.Jets, c.Jets_bDiscriminatorCSV)#fiducial    

    btagprob = btagcorr.GetCorrections(c.Jets,c.Jets_hadronFlavor,c.Jets_HTMask)

    MetVec = mkmet(c.MET, c.METPhi)
    tHt = getHT(recojets,AnMhtJetPtCut)
    tHt5 = getHT(recojets,AnMhtJetPtCut, 5)
    tMhtVec = getMHT(recojets,AnMhtJetPtCut, mhtjetetacut)
    tMhtPt, tMhtPhi = tMhtVec.Pt(), tMhtVec.Phi()
    tNJets = countJets(recojets,AnMhtJetPtCut)
    tBTags = countBJets_Useful(recojets,AnMhtJetPtCut)
    redoneMET = redoMET(MetVec, recojets, recojets)
    tMetPt,tMetPhi = redoneMET.Pt(), redoneMET.Phi()
    dphijets = []
    for jet in recojets:
        if abs(jet.Eta())<2.4: dphijets.append(jet)    
    tDPhi1,tDPhi2,tDPhi3,tDPhi4 = getDPhis(tMhtVec,dphijets)
    tJet1Pt,tJet1Eta,tJet2Pt,tJet2Eta,tJet3Pt,tJet3Eta,tJet4Pt,tJet4Eta = getJetKinematics(recojets)
    jetPhis = getPhis(recojets,tMhtVec)
    #fv = [tHt,tMhtPt,tNJets,tBTags,tDPhi1,tDPhi2,tDPhi3,tDPhi4,tJet1Pt,tJet1Eta,\
    #      tJet2Pt,tJet2Eta,tJet3Pt,tJet3Eta,tJet4Pt,tJet4Eta,tMetPt,tMhtPhi]
    fv = [[tHt,tMhtPt,tNJets,tBTags],[tDPhi1,tDPhi2,tDPhi3,tDPhi4]]
    binNumber = getBinNumber2018(fv[0])
    fv[0].append(binNumber)     
    fv[0].append(max([tDPhi1,tDPhi2,tDPhi3,tDPhi4]))
    fv[0].append(GetHighestPtForwardPt_prefiring(recojets))
    fv[0].append(tHt5/max(0.0001,tHt))
    fv[0].append(ientry%2==0)    
    fv[0].append(True)
    fv.append([passAndrewsTightHtRatio(tDPhi1, tHt5, tHt), tMetPt<tHt])
    if is2017f: fv[-1].append(EcalNoiseFilter(recojets, tMhtPhi))

    for nb, bprob in enumerate(btagprob):        
        if isdata: 
            weight = 1
            fv[0][3] = c.BTags
            ht = c.HTOnline
            fillth1(hHtWeighted, ht, weight)
            fillth1(hMhtWeighted, c.MHT, weight)                
        else: 
            weight = c.Weight*bprob
            fv[0][3] = nb
            gHt = getHT(c.GenJets,AnMhtJetPtCut)
            fillth1(hHtWeighted, gHt,weight)
            fillth1(hMhtWeighted, c.MHT,weight)            
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname,''): 
                    fillth1(histoStructDict[hname].Branch, fv[0][ivar],weight)
            for ivar, varname in enumerate(varlistDPhi):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,'',varname): 
                    fillth1(histoStructDict[hname].Branch, fv[1][ivar],weight)
        if isdata: break

    #truth
    bMhtVec = mkmet(c.MHT,c.MHTPhi)
    bMetPt = c.MET
    dphijets = []
    for jet in recojets:
        if abs(jet.Eta())<2.4: dphijets.append(jet)
    bDPhi1,bDPhi2,bDPhi3,bDPhi4 = abs(c.DeltaPhi1), abs(c.DeltaPhi2), abs(c.DeltaPhi3), abs(c.DeltaPhi4)##can try doing this the old fashioned way
    bJet1Pt,bJet1Eta,bJet2Pt,bJet2Eta,bJet3Pt,bJet3Eta,bJet4Pt,bJet4Eta = getJetKinematics(recojets)
    jetPhis = getPhis(recojets,bMhtVec)
    ht5 = getHT(recojets,AnMhtJetPtCut, 5.0)
    htratio = ht5/max(0.0001, c.HT)
    fv = [[c.HT,c.MHT,c.NJets,c.BTags],[bDPhi1,bDPhi2,bDPhi3,bDPhi4]]
    binNumber = getBinNumber2018(fv[0])
    fv[0].append(binNumber)        
    fv[0].append(max([bDPhi1,bDPhi2,bDPhi3,bDPhi4]))
    fv[0].append(GetHighestPtForwardPt_prefiring(recojets))
    fv[0].append(htratio)
    fv[0].append(-1)
    fv[0].append(ientry%2==0)    
    #filtery things
    fv.append([passAndrewsTightHtRatio(bDPhi1, c.HT5, c.HT), c.MHT<c.HT])
    if is2017f: fv[-1].append(EcalNoiseFilter(recojets, c.MHTPhi))

    for nb, bprob in enumerate(btagprob):        
        if isdata: 
            weight = 1
            fv[0][3] = c.BTags
            ht = c.HTOnline
            fillth1(hHtWeighted, ht, weight)
            fillth1(hMhtWeighted, c.MHT, weight)                
        else: 
            weight = c.Weight*bprob
            fv[0][3] = nb
            gHt = getHT(c.GenJets,AnMhtJetPtCut)
            fillth1(hHtWeighted, gHt,weight)
            fillth1(hMhtWeighted, c.MHT,weight)            
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname,''): 
                    fillth1(histoStructDict[hname].Truth, fv[0][ivar],weight)
            for ivar, varname in enumerate(varlistDPhi):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,'',varname): 
                    fillth1(histoStructDict[hname].Truth, fv[1][ivar],weight)
        if isdata: break        


fnew.cd()
writeHistoStruct(histoStructDict)
writeHistoStruct(histo2dStructDict)
hHt.Write()
hHtWeighted.Write()
hMht.Write()
hMhtWeighted.Write()
print 'just created', fnew.GetName()
fnew.Close()
