from ROOT import *
from utils import *
from ra2blibs import *
from array import array
import numpy as np
from glob import glob
import os, sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=0,help="increase output verbosity")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='Fall17MiniAODv2.QCD_HT',help="file")#RunIISummer16MiniAODv3.QCD_HT300to500
parser.add_argument("-nprint", "--printevery", type=int, default=100,help="print every n(events)")
parser.add_argument("-jersf", "--JerUpDown", type=str, default='Nom',help="JER scale factor (SFNom, SFUp, ...)")
parser.add_argument("-dmcrw", "--DataMcReweight", type=bool, default=False,help="reweight prior")
parser.add_argument("-quickrun", "--quickrun", type=bool, default=False,help="Quick practice run (True, False)")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
JerUpDown = args.JerUpDown
printevery = args.printevery
DataMcReweight = args.DataMcReweight
quickrun = args.quickrun
nametag = ''
'''
/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV
Fall17MiniAODv2.TTJets_DiLept_TuneCP5
Run2017B-31Mar2018-v1.JetHT
'''

#let's make this all about CSV's now

if 'Summer16' in fnamekeyword: 
    ntupleV = '16'
    isdata = False
elif 'Fall17' in fnamekeyword:
    ntupleV = '16'
elif 'Autumn18' in fnamekeyword:
    ntupleV = '17'
else: 
    ntupleV = '15'
    isdata = True

UseDeep = True
is2017 = False
is2016 = False
is2018 = False

if 'Run2016' in fnamekeyword or 'Summer16' in fnamekeyword: 
    BTAG_CSVv2 = 0.8484
    BTAG_deepCSV = 0.6324
    is2016 = True
if 'Run2017' in fnamekeyword or 'Fall17' in fnamekeyword: 
    BTAG_CSVv2 = 0.8838
    BTAG_deepCSV = 0.4941
    is2017 = True
if 'Run2018' in fnamekeyword or 'Autumn18' in fnamekeyword: 
    BTAG_CSVv2 = 0.8838
    #BTAG_deepCSV = 0.4941
    BTAG_deepCSV = 0.4184#0.4941####    
    is2018 = True

if is2016: jerScaleFactors = ScaleFactors2016
if is2017: jerScaleFactors = ScaleFactors2017
if is2018: jerScaleFactors = ScaleFactors2017

if UseDeep: BTag_Cut = BTAG_deepCSV
else: BTag_Cut = BTAG_CSVv2

tbool = {True:'Yes', False:'No'}
UncSign = {'None':0, 'Nom':0, 'Up':1, 'Down':-1}
uncsign = UncSign[JerUpDown]
llhdMhtThresh = 15

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

pwd = os.getcwd()

if 'YesNeut' in JerUpDown: AddInNeutrinos = True
else: AddInNeutrinos = False
if 'YesLep' in JerUpDown: AddInLeptons = True
else: AddInLeptons = False    

physicsProcess = fnamekeyword.split('.')[1]#datasetID[datasetID.find('_')+1:]
print 'fnamekeyword', fnamekeyword
print 'physicsProcess', physicsProcess

def calcSumPt(jets, obj, conesize=0.6, thresh=10):
    sumpt_ = 0
    for jet in jets:
        if not jet.Pt()>thresh:
            continue
        if not (obj.DeltaR(jet)<conesize):
            continue
        sumpt_+=jet.Pt()
    return sumpt_


hHt = TH1F('hHt','hHt',120,0,2500)
hHt.Sumw2()
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',120,0,2500)
hHtWeighted.Sumw2()

hCsvVsC = TH2F('hCsvVsC','hCsvVsC',100,0,3,105,0,1.05)
hCsvVsCB = TH2F('hCsvVsCB','hCsvVsCB',100,0,3,105,0,1.05)

hResponseVsGenPt = TH2F('gResponseVsGenPt','gResponseVsGenPt',1000,0,1000,400,0,4)
#binPt = [0,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,44,48,52,56,60,66,72,78,84,90,100,110,120,130,140,150,160,170,180,190,200,220,240,260,280,300,330,360,390,420,450,500,550,600,650,700,750,800,900,1000,1100,1200,1300,1400,1500,1600,1800,2000,2200,2500,3000,3500,4000,5000,6000,10000]#golden
binPt = [0,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,44,48,52,56,60,66,72,78,84,90,100,110,120,130,140,150,160,170,180,190,200,220,240,260,280,300,330,360,390,420,450,500,550,600,650,700,750,800,900,1000,10000]

binPtArr = array('d',binPt)
nBinPt = len(binPtArr)-1
hPtTemplate = TH1F('hPtTemplate','hPtTemplate',nBinPt,binPtArr)
templatePtAxis = hPtTemplate.GetXaxis()


#binEta = [0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,6.0]#golden
binEta = [0,0.4,0.8,1.2,1.6,2.0,2.5,6.0]#using this march 7 2017
binEtaArr = array('d',binEta)
nBinEta = len(binEtaArr)-1
hEtaTemplate = TH1F('hEtaTemplate','hEtaTemplate',nBinEta,binEtaArr)
templateEtaAxis = hEtaTemplate.GetXaxis()


hResGenTemplates = ['']
hResRecTemplates = ['']
hResGenTemplatesB = ['']
for ieta in range(1,templateEtaAxis.GetNbins()+1):#changed from +2 March8 2016
    hResGenTemplates.append([''])
    hResGenTemplatesB.append([''])
    hResRecTemplates.append([''])
    etarange = str(templateEtaAxis.GetBinLowEdge(ieta))+'-'+str(templateEtaAxis.GetBinUpEdge(ieta))
    for ipt in range(1,templatePtAxis.GetNbins()+1):#changed from +2 march8 2016
        lowedge = templatePtAxis.GetBinLowEdge(ipt)
        upedge = templatePtAxis.GetBinUpEdge(ipt)
        ptrange = str(lowedge)+'-'+str(upedge)
        if int(lowedge)<17:
            nbins = 650
            rupper = 4.0
            #nbins = 730
            #rupper = 4.5
        else:
            nbins = 350
            rupper = 3.0
        hg = TH1F('hRTemplate(gPt'+ptrange+', gEta'+etarange+')','pt(gen)',nbins,0,rupper)
        hg.Sumw2()
        hResGenTemplates[-1].append(hg)
        hgb = hg.Clone(hg.GetName()+'B')
        hResGenTemplatesB[-1].append(hgb)
        hr = TH1F('hRTemplate(rPt'+ptrange+', rEta'+etarange+')','pt(reco)',nbins,0,rupper)
        hr.Sumw2()
        hResRecTemplates[-1].append(hr)

print 'binningTemplate', binningTemplate
binHt = binningTemplate['Ht']
binHtArr = array('d',binHt)
nBinHt = len(binHtArr)-1
hHtTemplate = TH1F('hHtTemplate','hHtTemplate',nBinHt,binHtArr)
templateHtAxis = hHtTemplate.GetXaxis()
binMhtArr = array('d',binningTemplate['Mht'])
nBinMht = len(binMhtArr)-1
binHybMetArr = binMhtArr
nBinHybMet = nBinMht
binMetArr = binMhtArr
nBinMet = nBinMht

nbinsDphi = binningTemplate['DPhi1'][0]
lowDphi = binningTemplate['DPhi1'][1]
highDphi = binningTemplate['DPhi1'][2]


hMhtPtTemplatesB0 = ['']
hMhtPtTemplatesB1 = ['']
hMhtPtTemplatesB2 = ['']
hMhtPtTemplatesB3 = ['']
hMhtPhiTemplatesB0 = ['']
hMhtPhiTemplatesB1 = ['']
hMhtPhiTemplatesB2 = ['']
hMhtPhiTemplatesB3 = ['']
hMetPtTemplatesB0 = ['']
hMetPtTemplatesB1 = ['']
hMetPhiTemplatesB0 = ['']
hMetPhiTemplatesB1 = ['']

for iht in range(1,templateHtAxis.GetNbins()+2):
    htrange = str(templateHtAxis.GetBinLowEdge(iht))+'-'+str(templateHtAxis.GetBinUpEdge(iht))
    hGenMhtPtB0 = TH1F('hGenMhtPtB0(ght'+htrange+')','hGenMhtPtB0(ght'+htrange+')',nBinMht,binMhtArr)
    hGenMhtPhiB0 = TH1F('hGenMhtPhiB0(ght'+htrange+')','hGenMhtPhiB0(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMhtPtTemplatesB0.append(hGenMhtPtB0)
    hMhtPhiTemplatesB0.append(hGenMhtPhiB0)
    hGenMhtPtB1 = TH1F('hGenMhtPtB1(ght'+htrange+')','hGenMhtPtB1(ght'+htrange+')',nBinMht,binMhtArr)
    hGenMhtPhiB1 = TH1F('hGenMhtPhiB1(ght'+htrange+')','hGenMhtPhiB1(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMhtPtTemplatesB1.append(hGenMhtPtB1)
    hMhtPhiTemplatesB1.append(hGenMhtPhiB1)
    hGenMhtPtB2 = TH1F('hGenMhtPtB2(ght'+htrange+')','hGenMhtPtB2(ght'+htrange+')',nBinMht,binMhtArr)
    hGenMhtPhiB2 = TH1F('hGenMhtPhiB2(ght'+htrange+')','hGenMhtPhiB2(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMhtPtTemplatesB2.append(hGenMhtPtB2)
    hMhtPhiTemplatesB2.append(hGenMhtPhiB2)
    hGenMhtPtB3 = TH1F('hGenMhtPtB3(ght'+htrange+')','hGenMhtPtB3(ght'+htrange+')',nBinMht,binMhtArr)
    hGenMhtPhiB3 = TH1F('hGenMhtPhiB3(ght'+htrange+')','hGenMhtPhiB3(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMhtPtTemplatesB3.append(hGenMhtPtB3)
    hMhtPhiTemplatesB3.append(hGenMhtPhiB3)
    hMetPtB0 = TH1F('hMetPtB0(ght'+htrange+')','hMetPtB0(ght'+htrange+')',nBinMet,binMetArr)
    hMetPhiB0 = TH1F('hMetPhiB0(ght'+htrange+')','hMetPhiB0(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMetPtTemplatesB0.append(hMetPtB0)
    hMetPhiTemplatesB0.append(hMetPhiB0)
    hMetPtB1 = TH1F('hMetPtB1(ght'+htrange+')','hMetPtB1(ght'+htrange+')',nBinMet,binMetArr)
    hMetPhiB1 = TH1F('hMetPhiB1(ght'+htrange+')','hMetPhiB1(ght'+htrange+')',nbinsDphi,lowDphi,highDphi)
    hMetPtTemplatesB1.append(hMetPtB1)
    hMetPhiTemplatesB1.append(hMetPhiB1)



#################
# Load in chain #
#################
fnamefile = open('usefulthings/filelistV'+ntupleV+'.txt')
lines = fnamefile.readlines()
fnamefile.close()

listofvariations = []

c = TChain('TreeMaker2/PreSelection')
filelist = []
for line in lines:
    shortfname = fnamekeyword
    if not shortfname in line: continue
    fname = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV'+ntupleV+'/'+line#RelValQCD_FlatPt
    fname = fname.strip().replace('/eos/uscms/','root://cmseos.fnal.gov//')
    print 'adding', fname
    c.Add(fname)
    filelist.append(fname)
    break
nevents = c.GetEntries()
if quickrun: nevents = min(nevents, 100000)
c.Show(0)
print "nevents=", nevents

fdatamc = TFile('usefulthings/weights/datamcsyst.root') 
hMhtWeight = fdatamc.Get('rDataOverMC').Clone('hMhtWeight')
weightax = hMhtWeight.GetXaxis()

newFileName = 'Templates'+filelist[0].split('/')[-1].replace('.root','')+'Jer'+JerUpDown+DataMcReweight*'ModMht'+'.root'#tbool[AddInNeutrinos]+'Lep'
newFileName = newFileName.replace('.root',nametag+'.root')
fnew = TFile(newFileName,'recreate')

for ientry in range(nevents):
    if ientry%printevery==0:
        print "processing event", ientry, '/', nevents
    c.GetEntry(ientry)

    #if not passesUniversalSelection(c): continue###this is fiducial
    if not passesUniversalSelectionForResponses(c): continue
    if UseDeep: recojets = CreateUsefulJetVector(c.Jets, c.Jets_bJetTagDeepCSVBvsAll)#fiducial
    else: recojets = CreateUsefulJetVector(c.Jets, c.Jets_bDiscriminatorCSV)#fiducial


    if not (len(c.Jets)>0): continue
    if not c.Jets_neutralEmEnergyFraction[0]>0.02: continue

    matchedCsvVec = createMatchedCsvVector(c.GenJets, recojets);
    genjets = CreateUsefulJetVector(c.GenJets, matchedCsvVec)

    if (AddInNeutrinos or AddInLeptons):
        gens2add = []
        for igp, gp in enumerate(c.GenParticles):
            if AddInNeutrinos:
                if abs(c.GenParticles_PdgId[igp]) in [12,14,16]:
                    gens2add.append(gp)
            if AddInLeptons:
                if abs(c.GenParticles_PdgId[igp]) in [11,13,15]:
                    gens2add.append(gp)                
        for igen in range(len(genjets)):              
            for igen2add, gen2add in enumerate(gens2add):
                dr = genjets[igen].DeltaR(gen2add)
                if not (dr<0.4): continue # maybe one day you can use .5 and then put hold that neutrino
                genjets[igen]+=gen2add

    ght = getHT(genjets, 30)# make HT include the neutrinos 
    iht = templateHtAxis.FindBin(ght)      
    #weight = t.CrossSection/nevents
    hHt.Fill(ght,1)
    hHtWeighted.Fill(ght,c.Weight)


    weight = 1#t.Weight # all jets are the same, regardless of their origin.#as far as I know, this was 1 through thick and thin
    gMhtVec = getMHT(genjets,lhdMhtThresh)# changed from genjets, why not?
    gMhtPt, gMhtPhi = gMhtVec.Pt(), gMhtVec.Phi()


    RecoMetVec = mkmet(c.MET,c.METPhi)#fiducial
    if False:
        print 'RECO: nbtags =' , c.BTags
        for jet in recojets:
            print 'RECO: pt, eta, csv', jet.Pt(),jet.Eta(), jet.csv
        for jet in genjets:
            print 'GEN: pt, eta, csv', jet.Pt(),jet.Eta(), jet.csv            

    #make response templates
    for gjet in genjets:
        if not (gjet.Pt()>2):continue
        geta = abs(gjet.Eta())
        if not (geta<6): continue
        ieta = templateEtaAxis.FindBin(geta)               
        gpt = gjet.Pt()
        ipt = templatePtAxis.FindBin(gpt)

        sumGpt = calcSumPt(genjets, gjet, 0.7, 2)
        ratioGPtSumpt1 = gjet.Pt()/sumGpt
        if not ratioGPtSumpt1 > 0.98: continue #g-isolation
        matched = False
        isolated = False
        dRbig = 9
        ratioRPtSumpt1 = 1
        recoCsv = -1
        for ireco, rjet in enumerate(c.Jets):
            dR_ = rjet.DeltaR(gjet.tlv)
            if dR_<0.5 and dR_<dRbig:
                dRbig = dR_
                matched = True
                pt0 = rjet.Pt()

                '''
                if uncsign==1: 
                    sf, sfunc = getScaleFactor(abs(rjet.Eta()), jerScaleFactors)
                    variation = sfunc/sf
                else: variation, sfunc = 0, 0
                '''
                
                #print 'compare', variation/sfunc                    
                #if uncsign==1:    variation = (c.Jets_jerFactorUp[ireco]-c.Jets_jerFactor[ireco])/c.Jets_jerFactor[ireco]
                #elif uncsign==-1: variation = (c.Jets_jerFactorDown[ireco]-c.Jets_jerFactor[ireco])/c.Jets_jerFactor[ireco]
                #else: variation = 0
                #print 'c.Jets_jerFactorUp[ireco], c.Jets_jerFactorDown[ireco], c.Jets_jerFactor[ireco]', c.Jets_jerFactorUp[ireco], c.Jets_jerFactorDown[ireco], c.Jets_jerFactor[ireco], variation
                #listofvariations.append(variation)
                #print np.mean(listofvariations)
                #pt1 = max(0.,gpt+(1+variation)*(pt0-gpt))
                if uncsign==1: pt1 = rjet.Pt()*c.Jets_jerFactorUp[ireco]/c.Jets_jerFactor[ireco]
                elif uncsign==-1: pt1 = rjet.Pt()*c.Jets_jerFactorDown[ireco]/c.Jets_jerFactor[ireco]
                else: pt1 = rjet.Pt()
                response = pt1/gpt#cosine did nothing man! * TMath.Cos(rjet.DeltaPhi(gjet))
                #response = pt0/gpt
                sumpt = calcSumPt(c.Jets, rjet, 0.7, 0)
                ratioRPtSumpt1 = rjet.Pt()/sumpt
                recoCsv = c.Jets_bDiscriminatorCSV[ireco]
                if dR_<0.4:  break # if there's not one within 0.4, keep looking
        if ratioRPtSumpt1 > 0.98: isolated = True
        if not isolated: continue
        if not matched: continue
        if recoCsv<BTag_Cut:
            hResGenTemplates[ieta][ipt].Fill(response,weight)
        else:   hResGenTemplatesB[ieta][ipt].Fill(response,weight)
        hResponseVsGenPt.Fill(gpt,response,weight)
        #if nbs==0: hCsvVsC.Fill(response, recoCsv)



    if not ('QCD_HT' in physicsProcess): continue

    weight = c.Weight
    if gMhtPt<200 and DataMcReweight:
        weight*=hMhtWeight.GetBinContent(weightax.FindBin(gMhtPt))

    nbtags = countBJets_Useful(recojets, llhdMhtThresh, BTag_Cut)###
    nGenJets = countJets(genjets, 30)    
    if nbtags>2: 
        if nGenJets>2:
            genBjet = getLeadingGenBJet(genjets, recojets, BTag_Cut)
            hMhtPtTemplatesB3[iht].Fill(gMhtPt,weight)
            hMhtPhiTemplatesB3[iht].Fill(abs(genBjet.tlv.DeltaPhi(gMhtVec)),weight)
    elif nbtags>1: 
        if nGenJets>1:
            genBjet = getLeadingGenBJet(genjets, recojets, BTag_Cut)
            hMhtPtTemplatesB2[iht].Fill(gMhtPt,weight)
            hMhtPhiTemplatesB2[iht].Fill(abs(genBjet.tlv.DeltaPhi(gMhtVec)),weight)
    elif nbtags>0: 
        if nGenJets>1:
            genBjet = getLeadingGenBJet(genjets, recojets, BTag_Cut)
            hMhtPtTemplatesB1[iht].Fill(gMhtPt,weight)
            hMhtPhiTemplatesB1[iht].Fill(abs(genBjet.tlv.DeltaPhi(gMhtVec)),weight)
    elif nGenJets>1:
        hMhtPtTemplatesB0[iht].Fill(gMhtPt,weight)
        hMhtPhiTemplatesB0[iht].Fill(abs(genjets[0].tlv.DeltaPhi(gMhtVec)),weight)


fnew.cd()

def func(x,par):
    return par[0]*TMath.Gaus(x[0], par[1], par[2], True)+\
           par[3]*TMath.Gaus(x[0], par[4], par[5], True)+\
           par[6]*TMath.Gaus(x[0], par[7], par[8], True)


for etachain in hResGenTemplates[1:]:
    for hrat in etachain[1:]:
        hrat.Write()
        continue 

for etachain in hResGenTemplatesB[1:]:
    for hrat in etachain[1:]:
        hrat.Write()
        continue

for h in hMhtPtTemplatesB0[1:]: h.Write()
for h in hMhtPtTemplatesB1[1:]: h.Write()
for h in hMhtPtTemplatesB2[1:]: h.Write()
for h in hMhtPtTemplatesB3[1:]: h.Write()
for h in hMhtPhiTemplatesB0[1:]: h.Write()
for h in hMhtPhiTemplatesB1[1:]: h.Write()
for h in hMhtPhiTemplatesB2[1:]: h.Write()
for h in hMhtPhiTemplatesB3[1:]: h.Write()

hResponseVsGenPt.Write()
hHt.Write()
hHtWeighted.Write()
hPtTemplate.Write()
hEtaTemplate.Write()
hHtTemplate.Write()
hCsvVsC.Write()
hCsvVsCB.Write()           

print 'just created file', fnew.GetName()
fnew.Close()


'''
python tools/submitjobs.py --analyzer tools/ResponseMaker.py --fnamekeyword Summer16MiniAODv3.QCD_H --JerUpDown Nom

python tools/submitjobs.py --analyzer tools/ResponseMaker.py --fnamekeyword Summer16MiniAODv3.QCD_H  --JerUpDown Up

echo 1
ls -1 -d output/Run2017B-31Mar2018-v1.JetHT/*1of5*.root |wc -l
ls -1 -d output/Run2017B-31Mar2018-v1.JetHT/*2of5*.root |wc -l
ls -1 -d output/Run2017B-31Mar2018-v1.JetHT/*3of5*.root |wc -l
ls -1 -d output/Run2017B-31Mar2018-v1.JetHT/*4of5*.root |wc -l
ls -1 -d output/Run2017B-31Mar2018-v1.JetHT/*5of5*.root |wc -l
echo 2
ls -1 -d output/Run2017C-31Mar2018-v1.JetHT/*1of5*.root |wc -l
ls -1 -d output/Run2017C-31Mar2018-v1.JetHT/*2of5*.root |wc -l
ls -1 -d output/Run2017C-31Mar2018-v1.JetHT/*3of5*.root |wc -l
ls -1 -d output/Run2017C-31Mar2018-v1.JetHT/*4of5*.root |wc -l
ls -1 -d output/Run2017C-31Mar2018-v1.JetHT/*5of5*.root |wc -l
echo 3
ls -1 -d output/Run2017D-31Mar2018-v1.JetHT/*1of5*.root |wc -l
ls -1 -d output/Run2017D-31Mar2018-v1.JetHT/*2of5*.root |wc -l
ls -1 -d output/Run2017D-31Mar2018-v1.JetHT/*3of5*.root |wc -l
ls -1 -d output/Run2017D-31Mar2018-v1.JetHT/*4of5*.root |wc -l
ls -1 -d output/Run2017D-31Mar2018-v1.JetHT/*5of5*.root |wc -l
echo 4
ls -1 -d output/Run2017E-31Mar2018-v1.JetHT/*1of5*.root |wc -l
ls -1 -d output/Run2017E-31Mar2018-v1.JetHT/*2of5*.root |wc -l
ls -1 -d output/Run2017E-31Mar2018-v1.JetHT/*3of5*.root |wc -l
ls -1 -d output/Run2017E-31Mar2018-v1.JetHT/*4of5*.root |wc -l
ls -1 -d output/Run2017E-31Mar2018-v1.JetHT/*5of5*.root |wc -l
echo 5
ls -1 -d output/Run2017F-31Mar2018-v1.JetHT/*1of5*.root |wc -l
ls -1 -d output/Run2017F-31Mar2018-v1.JetHT/*2of5*.root |wc -l
ls -1 -d output/Run2017F-31Mar2018-v1.JetHT/*3of5*.root |wc -l
ls -1 -d output/Run2017F-31Mar2018-v1.JetHT/*4of5*.root |wc -l
ls -1 -d output/Run2017F-31Mar2018-v1.JetHT/*5of5*.root |wc -l



'''
