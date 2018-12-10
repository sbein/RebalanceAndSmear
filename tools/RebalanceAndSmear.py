#Welcome to the industrial age of Sam's rebalance and smear code. You're going to have a lot of fun!
import os,sys
from ROOT import *
from array import array
from glob import glob
from utils import *
from ra2blibs import *
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=0,help="increase output verbosity")
parser.add_argument("-nprint", "--printevery", type=int, default=100,help="print every n(events)")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='RunIIFall17MiniAODv2.QCD',help="file")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
printevery = args.printevery
nametag = ''

quickrun = True


if 'Summer16' in fnamekeyword: 
    ntupleV = '14'
    isdata = False
elif 'V15a' in fnamekeyword or 'RelVal' in fnamekeyword:
    ntupleV = '15a'
    isdata = False
elif 'Fall17' in fnamekeyword:
	ntupleV = '16'
else: 
    ntupleV = '15'
    isdata = True
if 'Run2016' in fnamekeyword: ntupleV = '14'
if 'Run2017' in fnamekeyword: ntupleV = '15'
if 'Run2018' in fnamekeyword: ntupleV = '15'
    
year = '2015'
year = '2016'
if year=='2015':loadSearchBins2015()
if year=='2016':loadSearchBins2016()
isskim = False ##thing one to switch xxx


pwd = os.getcwd()

gROOT.ProcessLine(open('src/UsefulJet.cc').read())
exec('from ROOT import *')

gROOT.ProcessLine(open('src/BayesRandS.cc').read())
exec('from ROOT import *')

gROOT.ProcessLine(open('src/Met110Mht110FakePho.cpp').read())
exec('from ROOT import *')

doHybridMet = False
lhdMhtJetPtCut = 15.0
AnMhtJetPtCut = 30.0
cutoff = 15.0
nCuts = 8
#loadSearchBins2015()
mktree = False
PrintJets = False
CuttingEdge = True

print 'hello'

#varlist = ['Ht','Mht','NJets','BTags','DPhi1','DPhi2','DPhi3','DPhi4','Jet1Pt','Jet1Eta','Jet2Pt','Jet2Eta','Jet3Pt','Jet3Eta','Jet4Pt','Jet4Eta','Met','MhtPhi','SearchBins','Odd','MvaLowMht','MvaLowHt']
varlist = ['Ht','Mht','NJets','BTags','DPhi1','DPhi2','DPhi3','DPhi4','SearchBins']
indexVar = {}
for ivar, var in enumerate(varlist): indexVar[var] = ivar


def selectionFeatureVector(fvector, regionkey='', omitcuts=''):
    iomits = []
    for cut in omitcuts.split('Vs'): iomits.append(indexVar[cut])
    nSpareJets = max(0,4-fvector[2])
    nCuts_ = nCuts-nSpareJets
    for i, feature in enumerate(fvector):
        if i>=nCuts_: break #make selections except for nonexistant jets
        if i in iomits: continue
        if not (feature>=regionCuts[regionkey][0][i][0] and feature<=regionCuts[regionkey][0][i][1]): return False
    if regionkey[1]==1:# this is the help you were looking for
        for ijet in range(min(4,fvector[2])):
            if (fvector[4+ijet]<=regionCuts['LowMhtBaseline'][4+ijet][0]): 
                return True #inverted dPhi selection
        return False
    #if 'Odd' in regionkey:
    #    if not fvector[-3]==True: return False
    return True 

StressData = {'Neuts': [pwd+'/Templates/TemplatesSFNomNeuts80x.root'],'Nom':[pwd+'/Templates/TemplatesSFNom80x.root'], 'CoreUp': [pwd+'/Templates/Templates80xCoreUp.root'], 'CoreDown': [pwd+'/Templates/Templates80xCoreDown.root'], 'TailUp': [pwd+'/Templates/Templates80xTailUp.root'], 'TailDown': [pwd+'/Templates/Templates80xTailDown.root'], 'ModPrior': [pwd+'/Templates/Templates80xModPrior.root'], 'NomFine': [pwd+'/Templates/TemplatesSFNom80xFine.root'], 'NomUltraFine':[pwd+'/Templates/TemplatesSFNom80xUltraFine.root'], 'NomV12':[pwd+'/Templates/TemplatesCoreNomTailNomV12.root'], 'NoSFV12':[pwd+'/Templates/TemplatesSFNomV12.root'], 'CoreUpCoarse':[pwd+'/Templates/TemplatesCoreUpTailNomV12coarse.root'], 'CoreDownCoarse':[pwd+'/Templates/TemplatesCoreDownTailNomV12coarse.root'], 'TailUpCoarse':[pwd+'/Templates/TemplatesCoreNomTailUpV12coarse.root'], 'TailDownCoarse':[pwd+'/Templates/TemplatesCoreNomTailDownV12coarse.root'], 'NomCoarse':[pwd+'/Templates/TemplatesCoreNomTailNomV12coarse.root'], 'NomNotProcessed':[pwd+'/Templates/TemplatesSFNomV12.root'], 'NomNotProcessedCoarse':[pwd+'/Templates/TemplatesSFNomV12coarse.root'], 'NomMoriond':[pwd+'/Templates/TemplatesSFNomV12Moriond.root'], 'NomMoriondCodeV11':[pwd+'/Templates/TemplatesSFNomV11MoriondCode.root'],'NomMoriondCodeV11Csvp8':[pwd+'/Templates/TemplatesSFNomV11MoriondCodeCsvp8.root'],'NomAncientMoriondCodeCsvp8':[pwd+'/Templates/TemplatesSFNomAncientMoriondCodeCsvp8.root'],'NomV11MoriondBitFiner':[pwd+'/Templates/TemplatesSFNomV11MoriondBitFiner.root'],'NomV12MoriondGuts':[pwd+'/Templates/TemplatesSFNomV12FixPriorGutEta.root'], 'NomV12MoriondNoFilters':[pwd+'/Templates/TemplatesSFNomV12NoFilters.root']}
StressData['NomNom'] = [pwd+'/Templates/megatemplateNoSF.root']#sam added Nov29

branchonly = False

if 'Run20' in fnamekeyword: isdata = True
else: isdata = False

#templateFileName = StressData[stressdata][0]
templateFileName = 'usefulthings/ResponseFunctionsMC17.root'
tfilename = templateFileName[templateFileName.rfind('/')+1:templateFileName.find('.root')].replace('Templates','')
print tfilename

ftemplate = TFile(templateFileName)
print 'using templates from',templateFileName
hPtTemplate = ftemplate.Get('hPtTemplate')
templatePtAxis = hPtTemplate.GetXaxis()
hEtaTemplate = ftemplate.Get('hEtaTemplate')
templateEtaAxis = hEtaTemplate.GetXaxis()
hHtTemplate = ftemplate.Get('hHtTemplate')
templateHtAxis = hHtTemplate.GetXaxis()


#################
# Load in chain #
#################
fnamefile = open('usefulthings/filelistV'+ntupleV+'.txt')
lines = fnamefile.readlines()
fnamefile.close()

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
if quickrun: nevents = min(1000,nevents)
c.Show(0)
print "nevents=", nevents

newFileName = 'RandS_'+filelist[0].split('/')[-1].replace('.root','')+'.root'
newFileName = newFileName.replace('.root',nametag+'.root')
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


hPassFit = TH1F('hPassFit','hPassFit',5,0,5)
hPassFit.Sumw2()
hTotFit = TH1F('hTotFit','hTotFit',5,0,5)
hTotFit.Sumw2()
hPassFar2big = TH1F('hPassFar2big','hPassFar2big',5,0,5)
hPassFar2big.Sumw2()
hTotFar2big = TH1F('hTotFar2big','hTotFar2big',5,0,5)
hTotFar2big.Sumw2()

hLeadJetEtaVsNeutralFraction_Blob = TH2F('hLeadJetEtaVsNeutralFraction_Blob','hLeadJetEtaVsNeutralFraction_Blob',100,0,1,100,-5,5)
hLeadJetEtaVsNeutralFraction_NonBlob = TH2F('hLeadJetEtaVsNeutralFraction_NonBlob','hLeadJetEtaVsNeutralFraction_NonBlob',100,0,1,100,-5,5)

hLeadJetEta_Blob = TH1F('hLeadJetEta_Blob','hLeadJetEta_Blob',200,-5,5)
hLeadJetEta_NonBlob = TH1F('hLeadJetEta_NonBlob','hLeadJetEta_NonBlob',200,-5,5)

hJet1RecoResponse = TH1F('hJet1RecoResponse','hJet1RecoResponse',300,0,3)
hJet2RecoResponse = TH1F('hJet2RecoResponse','hJet2RecoResponse',300,0,3)
harryhistosReco = [hJet1RecoResponse,hJet2RecoResponse]
hJet1RebaResponse = TH1F('hJet1RebaResponse','hJet1RebaResponse',300,0,3)
hJet2RebaResponse = TH1F('hJet2RebaResponse','hJet2RebaResponse',300,0,3)
harryhistosReba = [hJet1RebaResponse,hJet2RebaResponse]


if CuttingEdge: GleanTemplatesFromFile(ftemplate)
else:
    hNull = TH1F('hNull','hNull',1,-4,-3)
    hNullVec = std.vector('TH1F*')()
    hNullVec.push_back(hNull)
    gNull = TGraph()
    gNullVec = std.vector('TGraph*')()
    gNullVec.push_back(gNull)

    hResTemplates = ['']####turn this thing over to c++ style stuff!
    hResTemplates_CC = std.vector('std::vector<TH1F*>')()
    hResTemplates_CC.push_back(hNullVec)
    hRebTemplates = ['']
    hRebTemplates_CC = std.vector('std::vector<TH1F*>')()
    hRebTemplates_CC.push_back(hNullVec)
    gRebTemplates = ['']
    gRebTemplates_CC = std.vector('std::vector<TGraph*>')()
    gRebTemplates_CC.push_back(gNullVec)
    nsmooth = 5
    for ieta in range(1,templateEtaAxis.GetNbins()+1):
        hResTemplates.append([''])
        hRebTemplates.append([''])
        gRebTemplates.append([''])
        hResTemplates_CC.push_back(hNullVec)
        hRebTemplates_CC.push_back(hNullVec)
        gRebTemplates_CC.push_back(gNullVec)    
        etarange = str(templateEtaAxis.GetBinLowEdge(ieta))+'-'+str(templateEtaAxis.GetBinUpEdge(ieta))
        for ipt in range(1,templatePtAxis.GetNbins()+1):
            lowedge = templatePtAxis.GetBinLowEdge(ipt)
            upedge = templatePtAxis.GetBinUpEdge(ipt)
            ptrange = str(lowedge)+'-'+str(upedge)
            h = ftemplate.Get('hRTemplate(gPt'+ptrange+', gEta'+etarange+')')
            hResTemplates[-1].append(h)
            hResTemplates_CC[-1].push_back(h)
            h2 = ftemplate.Get('hRTemplate(gPt'+ptrange+', gEta'+etarange+')')#these were once rPt's
            hRebTemplates[-1].append(h2)
            hRebTemplates_CC[-1].push_back(h2)
            #f = ftemplate.Get('splines/hRTemplate(gPt'+ptrange+', gEta'+etarange+')_spline')
            g = ftemplate.Get('splines/hRTemplate(gPt'+ptrange+', gEta'+etarange+')_graph')
            gRebTemplates[-1].append(g)
            gRebTemplates_CC[-1].push_back(g)

    gGenMhtPtTemplatesB0 = ['']
    gGenMhtPtTemplatesB1 = ['']
    gGenMhtPtTemplatesB2 = ['']
    gGenMhtPtTemplatesB3 = ['']
    gGenMhtDPhiTemplatesB0 = ['']
    gGenMhtDPhiTemplatesB1 = ['']
    gGenMhtDPhiTemplatesB2 = ['']
    gGenMhtDPhiTemplatesB3 = ['']
    gGenMhtPtTemplatesB0_CC = std.vector('TGraph*')()
    gGenMhtPtTemplatesB0_CC.push_back(gNull)
    gGenMhtPtTemplatesB1_CC = std.vector('TGraph*')()
    gGenMhtPtTemplatesB1_CC.push_back(gNull)
    gGenMhtPtTemplatesB2_CC = std.vector('TGraph*')()
    gGenMhtPtTemplatesB2_CC.push_back(gNull)
    gGenMhtPtTemplatesB3_CC = std.vector('TGraph*')()
    gGenMhtPtTemplatesB3_CC.push_back(gNull)
    gGenMhtDPhiTemplatesB0_CC = std.vector('TGraph*')()
    gGenMhtDPhiTemplatesB0_CC.push_back(gNull)
    gGenMhtDPhiTemplatesB1_CC = std.vector('TGraph*')()
    gGenMhtDPhiTemplatesB1_CC.push_back(gNull)
    gGenMhtDPhiTemplatesB2_CC = std.vector('TGraph*')()
    gGenMhtDPhiTemplatesB2_CC.push_back(gNull)
    gGenMhtDPhiTemplatesB3_CC = std.vector('TGraph*')()
    gGenMhtDPhiTemplatesB3_CC.push_back(gNull)

    if doHybridMet: keyvar = 'HybMet'
    else: keyvar = 'Mht'

    for iht in range(1,templateHtAxis.GetNbins()+2):
            htrange = str(templateHtAxis.GetBinLowEdge(iht))+'-'+str(templateHtAxis.GetBinUpEdge(iht))
            fb0 = ftemplate.Get('splines/hGen'+keyvar+'PtB0(ght'+htrange+')_graph')
            #fb0 = ftemplate.Get('hGenMhtPtB0(ght'+htrange+')')#using histos! for rebalancejets2
            #fb0.Scale(1.0/fb0.Integral(-1,999),'width')
            gGenMhtPtTemplatesB0.append(fb0)
            gGenMhtPtTemplatesB0_CC.push_back(fb0)
            fb0phi = ftemplate.Get('splines/hGen'+keyvar+'PhiB0(ght'+htrange+')_graph')
            #fb0phi = ftemplate.Get('hGenMhtPhiB0(ght'+htrange+')')
            #fb0phi.Scale(1.0/fb0phi.Integral(-1,999),'width')
            gGenMhtDPhiTemplatesB0.append(fb0phi)
            gGenMhtDPhiTemplatesB0_CC.push_back(fb0phi)
            fb1 = ftemplate.Get('splines/hGen'+keyvar+'PtB1(ght'+htrange+')_graph')
            #fb1 = ftemplate.Get('hGenMhtPtB1(ght'+htrange+')')
            #fb1.Scale(1.0/fb1.Integral(-1,999),'width')
            gGenMhtPtTemplatesB1.append(fb1)
            gGenMhtPtTemplatesB1_CC.push_back(fb1)
            #print "'splines/hGenMhtPhiB1(ght'+htrange+')_graph'",'splines/hGenMhtPhiB1(ght'+htrange+')_graph'
            fb1phi = ftemplate.Get('splines/hGen'+keyvar+'PhiB1(ght'+htrange+')_graph')
            #fb1phi = ftemplate.Get('hGenMhtPhiB1(ght'+htrange+')')
            #fb1phi.Scale(1.0/fb1phi.Integral(-1,999),'width')
            gGenMhtDPhiTemplatesB1.append(fb1phi)
            gGenMhtDPhiTemplatesB1_CC.push_back(fb1phi)
            fb2 = ftemplate.Get('splines/hGen'+keyvar+'PtB2(ght'+htrange+')_graph')
            #fb2 = ftemplate.Get('hGenMhtPtB2(ght'+htrange+')')
            #fb2.Scale(2.0/fb2.Integral(-2,999),'width')
            gGenMhtPtTemplatesB2.append(fb2)
            gGenMhtPtTemplatesB2_CC.push_back(fb2)
            #print "'splines/hGenMhtPhiB2(ght'+htrange+')_graph'",'splines/hGenMhtPhiB2(ght'+htrange+')_graph'
            fb2phi = ftemplate.Get('splines/hGen'+keyvar+'PhiB2(ght'+htrange+')_graph')
            #fb2phi = ftemplate.Get('hGenMhtPhiB2(ght'+htrange+')')
            #fb2phi.Scale(2.0/fb2phi.Integral(-2,999),'width')
            gGenMhtDPhiTemplatesB2.append(fb2phi)
            gGenMhtDPhiTemplatesB2_CC.push_back(fb2phi)
            fb3 = ftemplate.Get('splines/hGen'+keyvar+'PtB3(ght'+htrange+')_graph')
            #fb3 = ftemplate.Get('hGenMhtPtB3(ght'+htrange+')')
            #fb3.Scale(2.0/fb3.Integral(-2,999),'width')
            gGenMhtPtTemplatesB3.append(fb3)
            gGenMhtPtTemplatesB3_CC.push_back(fb3)
            #print "'splines/hGenMhtPhiB3(ght'+htrange+')_graph'",'splines/hGenMhtPhiB3(ght'+htrange+')_graph'
            fb3phi = ftemplate.Get('splines/hGen'+keyvar+'PhiB3(ght'+htrange+')_graph')
            #fb3phi = ftemplate.Get('hGenMhtPhiB3(ght'+htrange+')')
            #fb3phi.Scale(2.0/fb3phi.Integral(-2,999),'width')
            gGenMhtDPhiTemplatesB3.append(fb3phi)  
            gGenMhtDPhiTemplatesB3_CC.push_back(fb3phi)        


    gGenMhtPtTemplates = [gGenMhtPtTemplatesB0,gGenMhtPtTemplatesB1,gGenMhtPtTemplatesB2,gGenMhtPtTemplatesB3]
    gGenMhtDPhiTemplates = [gGenMhtDPhiTemplatesB0,gGenMhtDPhiTemplatesB1,gGenMhtDPhiTemplatesB2,gGenMhtDPhiTemplatesB3]

    Templates = TemplateSet()
    Templates.hEtaTemplate = hEtaTemplate
    Templates.hPtTemplate = hPtTemplate
    Templates.hHtTemplate = hHtTemplate
    Templates.ResponseFunctions = gRebTemplates_CC
    Templates.ResponseHistos = hResTemplates_CC
    Templates.gGenMhtPtTemplatesB0 = gGenMhtPtTemplatesB0_CC
    Templates.gGenMhtPtTemplatesB1 = gGenMhtPtTemplatesB1_CC
    Templates.gGenMhtPtTemplatesB2 = gGenMhtPtTemplatesB2_CC
    Templates.gGenMhtPtTemplatesB3 = gGenMhtPtTemplatesB3_CC
    Templates.gGenMhtDPhiTemplatesB0 = gGenMhtDPhiTemplatesB0_CC
    Templates.gGenMhtDPhiTemplatesB1 = gGenMhtDPhiTemplatesB1_CC
    Templates.gGenMhtDPhiTemplatesB2 = gGenMhtDPhiTemplatesB2_CC
    Templates.gGenMhtDPhiTemplatesB3 = gGenMhtDPhiTemplatesB3_CC
    Templates.lhdMhtJetPtCut = lhdMhtJetPtCut
    MakeTemplatesGlobal(Templates)

histoStructDict = {}
for region in regionCuts:
    for var in varlist:
        histname = region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname)

#varlist2d
var_pairs = []#[['Mht','Ht'],['Mht','BTags'],['Mht','NJets'],['Mht','DPhi1'],['Mht','DPhi2'],['Mht','DPhi3'],['Mht','DPhi4']]
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

if mktree:
    treefile = TFile('littletreeLowMht'+fnamekeyword+'.root','recreate')
    littletree = TTree('littletree','littletree')
    prepareLittleTree(littletree)

#t.Show(0)
print 'nevents=', nevents
t0 = time.time()
for ientry in range(nevents):
    if ientry%printevery==0:
        print "processing event", ientry, '/', nevents
        print 'time=',time.time()-t0
    c.GetEntry(ientry)

    if True and ientry==0:
        for itrig in range(len(c.TriggerPass)):
            print itrig, c.TriggerNames[itrig], c.TriggerPrescales[itrig], c.HT
        print '='*20
    #if not (c.BTags>5): continue

    if isdata:
        prescaleweight = c.PrescaleWeightHT#c.Online_HtPrescaleWeight
        ht = c.HTOnline
        if prescaleweight == 0: continue
        #.Online_Ht
        fillth1(hHt, ht,1)
        fillth1(hHtWeighted, ht,prescaleweight)
        fillth1(hMht, c.MHT,1)
        fillth1(hMhtWeighted, c.MHT,prescaleweight)
    else:
        gHt = getHT(c.GenJets,AnMhtJetPtCut)
        fillth1(hHt, gHt,1)
        fillth1(hHtWeighted, gHt,c.CrossSection)
        fillth1(hMht, c.MHT,1)
        fillth1(hMhtWeighted, c.MHT,c.CrossSection)    
        prescaleweight = 1

    if isdata: 
        if isskim:
            if not passesUniversalSkimSelection(c): continue
        else:
            if not passesUniversalDataSelection(c): continue
    else:
        if not passesUniversalSelection(c): continue


    #if datamc=='MC' and (c.HT>5*c.GenHT):
    #    print 'DEBUG suspicious event', ientry, c.HT, c.GenHT
    #    if c.HT>5*c.GenHT: continue

    MetVec = mkmet(c.MET, c.METPhi)
    MhtVec = mkmet(c.MHT,c.MHTPhi)
    
    ntries = 1
    if isdata: weight = 1.0*prescaleweight
    else: weight = c.CrossSection        

    if PrintJets: 
        print '===gen particles==='*5
        for igp, gp in enumerate(c.GenParticles):
            if gp.Pt()>1: print gp.Pt(), gp.Eta(), c.GenParticles_PdgId[igp]
        print 'MHT, GenMHT = ', c.MHT, c.GenMHT


    recojets = CreateUsefulJetVector(c.Jets, c.Jets_bDiscriminatorCSV)

    '''
    if not isskim:
        softrecojets = CreateUsefulJetVector(c.SoftJets, c.SoftJets_bDiscriminatorCSV)
        #for softjet in softrecojets: softjet.csv = 1.01
        recojets = ConcatenateVectors(recojets, softrecojets)
    '''

    ht5 = getHT(recojets,AnMhtJetPtCut, 5.0)#Run2016H-PromptReco-v2.MET
    try: htratio = ht5/c.HT
    except: htratio = 5
    if False and c.MHT>300 and c.HT>300:################switched off
        maxneutralfraction = -1
        maxindex = -1
        for idatum, datum in enumerate(c.Jets_neutralHadronEnergyFraction):
            if datum>maxneutralfraction:
                maxneutralfraction = datum
                maxindex = idatum
        if htratio>2: 
            fillth1(hLeadJetEtaVsNeutralFraction_Blob, c.Jets_neutralHadronEnergyFraction[maxindex], c.Jets[maxindex].Eta())
            fillth1(hLeadJetEta_Blob, c.Jets[0].Eta())
        else:
            fillth1(hLeadJetEtaVsNeutralFraction_NonBlob, c.Jets_neutralHadronEnergyFraction[maxindex], c.Jets[maxindex].Eta())
            fillth1(hLeadJetEta_NonBlob, c.Jets[0].Eta())    
    #if not passesForwardJetID(c): continue

    if not htratio<2: 
        print 'htratio', htratio
        continue

    if not isdata:
        matchedCsvVec = createMatchedCsvVector(c.GenJets, recojets)
        genjets = CreateUsefulJetVector(c.GenJets, matchedCsvVec)
        ##ignore jets that aren't matched!!!
        #recojets = RemoveUnmatchedJets(recojets, genjets)
        #recojets = VetoOnUnmatchedJets100(recojets, genjets)
        gMhtVec = getMHT(genjets,AnMhtJetPtCut)
        gMht, gMhtPhi = gMhtVec.Pt(), gMhtVec.Phi()
        #for jet in genjets: 
        #    if jet.csv==0: jet.csv = 1.01   
        if PrintJets:                
            gbtags = countBJets_Useful(genjets,AnMhtJetPtCut)
            gmht = getMHT(genjets,AnMhtJetPtCut)
            print 'GEN: nbtags, mht =' , gbtags, gmht
            for jet in genjets:
                print 'GEN: pt, csv', jet.Pt(), jet.Eta(), jet.csv    
    ###     

    #branch
    bMhtVec = mkmet(c.MHT,c.MHTPhi)
    bMetPt = c.MET



    bDPhi1,bDPhi2,bDPhi3,bDPhi4 = getDPhis(bMhtVec, recojets)
    bJet1Pt,bJet1Eta,bJet2Pt,bJet2Eta,bJet3Pt,bJet3Eta,bJet4Pt,bJet4Eta = getJetKinematics(recojets)
    jetPhis = getPhis(recojets,bMhtVec)
    fv = [c.HT,c.MHT,c.NJets,c.BTags,bDPhi1,bDPhi2,bDPhi3,bDPhi4]#,bJet1Pt,bJet1Eta,\
          #bJet2Pt,bJet2Eta,bJet3Pt,bJet3Eta,bJet4Pt,bJet4Eta,c.MET,c.MHTPhi]#must be synchronized with varlist 
    #if ientry==47: print 'fv', fv
    binNumber = getBinNumber(fv)
    fv.append(binNumber)
    fv.append(-1)
    fv.append(ientry%2==0)    
    if PrintJets:
        print 'RECO: nbtags =' , c.BTags
        print fv
        for jet in recojets:
            print 'RECO: pt, csv', jet.Pt(),jet.Eta(), jet.csv    
    for regionkey in regionCuts:
        for ivar, varname in enumerate(varlist):
            hname = regionkey+'_'+varname
            if selectionFeatureVector(fv,regionkey,varname): 
                fillth1(histoStructDict[hname].Branch, fv[ivar],weight)
        for varpair in var_pairs:
            varY, varX = varpair
            hname = regionkey+'_'+varY+'Vs'+varX
            ivarX, ivarY = indexVar[varX], indexVar[varY]
            if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX): 
                fillth1(histo2dStructDict[hname].Branch, fv[ivarX],fv[ivarY],weight)
    if mktree and 'T1' in fnamekeyword:
        if fv[1]>=150 and fv[1]<=200 and fv[0]>500 and fv[2]>3:# and ientry>nevents/2:
            growTree(littletree, fv, jetPhis, weight)            


    if branchonly: continue

    tHt = getHT(recojets,AnMhtJetPtCut)
    tHt5 = getHT(recojets,AnMhtJetPtCut, 5)
    tMhtVec = getMHT(recojets,AnMhtJetPtCut)
    tMhtPt, tMhtPhi = tMhtVec.Pt(), tMhtVec.Phi()
    tNJets = countJets(recojets,AnMhtJetPtCut)
    tBTags = countBJets_Useful(recojets,AnMhtJetPtCut)
    redoneMET = redoMET(MetVec, recojets, recojets)
    tMetPt,tMetPhi = redoneMET.Pt(), redoneMET.Phi()
    tDPhi1,tDPhi2,tDPhi3,tDPhi4 = getDPhis(tMhtVec,recojets)
    tJet1Pt,tJet1Eta,tJet2Pt,tJet2Eta,tJet3Pt,tJet3Eta,tJet4Pt,tJet4Eta = getJetKinematics(recojets)
    jetPhis = getPhis(recojets,tMhtVec)
    #fv = [tHt,tMhtPt,tNJets,tBTags,tDPhi1,tDPhi2,tDPhi3,tDPhi4,tJet1Pt,tJet1Eta,\
    #      tJet2Pt,tJet2Eta,tJet3Pt,tJet3Eta,tJet4Pt,tJet4Eta,tMetPt,tMhtPhi]
    fv = [tHt,tMhtPt,tNJets,tBTags,tDPhi1,tDPhi2,tDPhi3,tDPhi4]          
    binNumber = getBinNumber(fv)
    fv.append(binNumber)     
    fv.append(ientry%2==0)    
    fv.append(True)
    if isdata: wtrig_nom = Eff_Met110Mht110FakePho_CenterUpDown(fv[0], fv[1], fv[2])[0]
    else:  wtrig_nom = 1.0   
    if (tHt>0 and tHt5/tHt<2):        
      for regionkey in regionCuts:
        for ivar, varname in enumerate(varlist):
            hname = regionkey+'_'+varname
            if selectionFeatureVector(fv,regionkey,varname): 
                fillth1(histoStructDict[hname].Truth, fv[ivar],wtrig_nom*weight)
        for varpair in var_pairs:
            varY, varX = varpair
            hname = regionkey+'_'+varY+'Vs'+varX
            ivarX, ivarY = indexVar[varX], indexVar[varY]
            if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX): 
                fillth1(histo2dStructDict[hname].Truth, fv[ivarX],fv[ivarY],wtrig_nom*weight)

    if isdata: weight = 1.0*prescaleweight/ntries                
    else: weight = c.CrossSection/ntries


    fitsucceed = True
    if CuttingEdge:
        fitsucceed = RebalanceJets_BayesFitter(recojets)
        rebalancedJets = _Templates_.dynamicJets
    else:
        recojetsCsv = []
        for recojet in recojets: recojetsCsv.append(recojet.csv)
        rebalancedJets_,csvRebalancedJets, nparams = rebalanceJets(recojets,recojetsCsv,\
                                                                   gRebTemplates,hEtaTemplate,hPtTemplate,\
                                                                   gGenMhtPtTemplates,gGenMhtDPhiTemplates,\
                                                                   hHtTemplate,cutoff,lhdMhtJetPtCut)
        rebalancedJets = CreateUsefulJetVector(rebalancedJets_,csvRebalancedJets)

        #rebalancedJets_,csvRebalancedJets, nparams = rebalanceJets(t.JetSlim,t.JetsSlim_bDiscriminatorCSV,\
        #                                                           gRebTemplates,hEtaTemplate,hPtTemplate,\
        #                                                           gGenMhtPtTemplates,gGenMhtDPhiTemplates,\
        #                                                           hHtTemplate,cutoff,lhdMhtJetPtCut)
        #rebalancedJets = CreateUsefulJetVector(rebalancedJets_,csvRebalancedJets)
        #
        _nparams_ = nparams

    mHt = getHT(rebalancedJets,AnMhtJetPtCut)
    mHt5 = getHT(rebalancedJets,AnMhtJetPtCut, 5.0)
    mMhtVec = getMHT(rebalancedJets,AnMhtJetPtCut)
    mMhtPt, mMhtPhi = mMhtVec.Pt(), mMhtVec.Phi()

    mNJets = countJets(rebalancedJets,AnMhtJetPtCut)
    mBTags = countBJets_Useful(rebalancedJets,AnMhtJetPtCut)###

    hope = (fitsucceed and mMhtPt<160)# mMhtPt>min(mHt/2,180):

    redoneMET = redoMET(MetVec,recojets,rebalancedJets)
    mMetPt,mMetPhi = redoneMET.Pt(), redoneMET.Phi()
    mDPhi1,mDPhi2,mDPhi3,mDPhi4 = getDPhis(mMhtVec,rebalancedJets)
    mJet1Pt,mJet1Eta,mJet2Pt,mJet2Eta,mJet3Pt,mJet3Eta,mJet4Pt,mJet4Eta = getJetKinematics(rebalancedJets)
    jetPhis = getPhis(rebalancedJets,mMhtVec)
    fv = [mHt,mMhtPt,mNJets,mBTags,mDPhi1,mDPhi2,mDPhi3,mDPhi4]#mJet1Pt,mJet1Eta,\
          #mJet2Pt,mJet2Eta,mJet3Pt,mJet3Eta,mJet4Pt,mJet4Eta,mMetPt,mMhtPhi]
    binNumber = getBinNumber(fv)
    fv.append(binNumber)
    fv.append(ientry%2==0)

    if PrintJets:
        print 'Rebalanced'
        print fv
        for ireb, rjet in enumerate(rebalancedJets):
            if rjet.Pt()>15: print ireb, rjet.Pt(), rjet.Eta(), rjet.csv
        print 'fit passed?=',fitsucceed
    if isdata: wtrig_nom = Eff_Met110Mht110FakePho_CenterUpDown(fv[0], fv[1], fv[2])[0]
    else:  wtrig_nom = 1.0
    if (mHt>0 and mHt5/mHt<2):                
      for regionkey in regionCuts:        
        for ivar, varname in enumerate(varlist):
            hname = regionkey+'_'+varname
            if selectionFeatureVector(fv,regionkey,varname): 
                fillth1(histoStructDict[hname].Rebalanced, fv[ivar],wtrig_nom*weight)
        for varpair in var_pairs:
            varY, varX = varpair
            hname = regionkey+'_'+varY+'Vs'+varX
            ivarX, ivarY = indexVar[varX], indexVar[varY]
            if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX): 
                fillth1(histo2dStructDict[hname].Rebalanced, fv[ivarX],fv[ivarY],wtrig_nom*weight)

    fillth1(hTotFit, fv[3], weight)
    fillth1(hTotFar2big, fv[3], weight)    
    if fitsucceed: 
        fillth1(hPassFit, fv[3], weight)
    if fv[1]<200:
        fillth1(hPassFar2big, fv[3], weight)
    if not fitsucceed: print ientry, 'fit failed with mht, btags = ', fv[1], fv[3]
    if fnamekeyword=='TTJets' or fnamekeyword=='WJetsToLNu' or fnamekeyword=='ZJetsToNuNu':upfactor = 2000
    else: upfactor = 200
    if not isdata: 
        upfactor = 2
        ntries = upfactor
        weight = c.CrossSection/ntries
    if isdata: 
        ntries = min(int(upfactor*prescaleweight),200)
        weight = prescaleweight/ntries

    for i in range(ntries):
        if not hope: break
        if CuttingEdge:
            RplusSJets = smearJets_CC(rebalancedJets,99+_Templates_.nparams)#this is one key difference between the golden and space ages (this script currenlty has 99+nparams here.)
        else:
            RplusSJets_,csvRplusSJets_=smearJets(rebalancedJets,csvRebalancedJets,hResTemplates,hEtaTemplate,hPtTemplate,nparams)
            RplusSJets = CreateUsefulJetVector(RplusSJets_,csvRplusSJets_)
        rpsHt = getHT(RplusSJets,AnMhtJetPtCut)
        rpsHt5 = getHT(RplusSJets,AnMhtJetPtCut, 5)
        rMhtVec = getMHT(RplusSJets,AnMhtJetPtCut)
        rpsMht, rpsMhtPhi = rMhtVec.Pt(), rMhtVec.Phi()
        if rpsMht>2000: 
            print 'DEBUG passing on unusually high R+S event', ientry#this is a safeguard against mystery
            continue
        rpsNJets = countJets(RplusSJets,AnMhtJetPtCut)
        rpsBTags = countBJets_Useful(RplusSJets,AnMhtJetPtCut)
        rpsMhtVec = mkmet(rpsMht,rpsMhtPhi)
        redoneMET = redoMET(MetVec, recojets, RplusSJets)
        rpsMetPt, rpsMetPhi = redoneMET.Pt(), redoneMET.Phi()
        rpsDPhi1,rpsDPhi2,rpsDPhi3,rpsDPhi4 = getDPhis(rpsMhtVec,RplusSJets)
        rpsJet1Pt,rpsJet1Eta,rpsJet2Pt,rpsJet2Eta,rpsJet3Pt,rpsJet3Eta,rpsJet4Pt,rpsJet4Eta = getJetKinematics(RplusSJets)
        jetPhis = getPhis(RplusSJets,rpsMhtVec)
        #fv = [rpsHt,rpsMht,rpsNJets,rpsBTags,rpsDPhi1,rpsDPhi2,rpsDPhi3,rpsDPhi4,rpsJet1Pt,rpsJet1Eta,\
        #      rpsJet2Pt,rpsJet2Eta,rpsJet3Pt,rpsJet3Eta,rpsJet4Pt,rpsJet4Eta,rpsMetPt,rpsMhtPhi]
        fv = [rpsHt,rpsMht,rpsNJets,rpsBTags,rpsDPhi1,rpsDPhi2,rpsDPhi3,rpsDPhi4]              
        binNumber = getBinNumber(fv)     
        fv.append(binNumber)
        fv.append(ientry%2==0)

        if isdata: wtrig_nom = Eff_Met110Mht110FakePho_CenterUpDown(fv[0], fv[1], fv[2])[0]
        else:  wtrig_nom = 1.0        
        #if rpsMht>250: print 'r&s trigger',wtrig_nom, fv
        if (rpsHt>0 and rpsHt5/rpsHt<2):
          for regionkey in regionCuts:     
            for ivar, varname in enumerate(varlist):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname): 
                    fillth1(histoStructDict[hname].RplusS, fv[ivar],wtrig_nom*weight)
            for varpair in var_pairs:
                varY, varX = varpair
                hname = regionkey+'_'+varY+'Vs'+varX
                ivarX, ivarY = indexVar[varX], indexVar[varY]
                if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX): 
                    fillth1(histo2dStructDict[hname].RplusS, fv[ivarX],fv[ivarY],wtrig_nom*weight)
        if mktree and 'JetHT' in physicsProcess and fv[1]>=150 and fv[1]<200 and fv[0]>=500 and fv[2]>=4: 
            growTree(littletree, fv, jetPhis, weight)

        if PrintJets:                
            print 'RplusS: nbtags =' , rpsBTags
            print fv
            if fv[-2]!=-1:
                for jet in RplusSJets:
                    print 'RplusS: pt, csv', jet.Pt(),jet.Eta(), jet.csv


    if isdata: continue    
    genMetVec = mkmet(c.GenMET, c.GenMETPhi)

    #matchedCsvVec = createMatchedCsvVector(t.GenJets, recojets)
    #genjets = CreateUsefulJetVector(t.GenJets, matchedCsvVec)
    gMhtVec = getMHT(genjets,AnMhtJetPtCut)
    gMht, gMhtPhi = gMhtVec.Pt(), gMhtVec.Phi()
    #matchedRebCsvVec = getMatchedCsv(genjets,rebalancedJets,csvRebalancedJets,harryhistosReba)#for Harry!
    weight = c.CrossSection
    gHt = getHT(genjets,AnMhtJetPtCut)
    gMhtVec = getMHT(genjets,AnMhtJetPtCut)
    gMht, gMhtPhi = gMhtVec.Pt(), gMhtVec.Phi()
    gNJets = countJets(genjets,AnMhtJetPtCut)
    gBTags = countBJets_Useful(genjets,AnMhtJetPtCut)
    gMhtVec = mkmet(gMht,gMhtPhi)
    if doHybridMet: gMhtVec = getHybridMet(genjets,recojets,genMetVec,cutoff).Pt()
    gMetPt,gMetPhi = genMetVec.Pt(),genMetVec.Phi()
    gDPhi1,gDPhi2,gDPhi3,gDPhi4 = getDPhis(gMhtVec,genjets)
    gJet1Pt,gJet1Eta,gJet2Pt,gJet2Eta,gJet3Pt,gJet3Eta,gJet4Pt,gJet4Eta = getJetKinematics(genjets)
    jetPhis = getPhis(genjets,gMhtVec)
    fv = [gHt,gMht,gNJets,gBTags,gDPhi1,gDPhi2,gDPhi3,gDPhi4]
    binNumber = getBinNumber(fv)##for good measure, do some debugging here. it'd be nice to have an understand for why rebalance mht != generator-level mht
    fv.append(binNumber)
    fv.append(ientry%2==0)
    if PrintJets:                
        print 'GEN: nbtags =' , mBTags
        print fv
        for jet in genjets:
            print 'GEN: pt, csv', jet.Pt(), jet.Eta(), jet.csv        
    for regionkey in regionCuts:
        for ivar, varname in enumerate(varlist):
            hname = regionkey+'_'+varname
            if selectionFeatureVector(fv,regionkey,varname): 
                fillth1(histoStructDict[hname].Gen, fv[ivar],weight)
        for varpair in var_pairs:
            varY, varX = varpair
            hname = regionkey+'_'+varY+'Vs'+varX
            ivarX, ivarY = indexVar[varX], indexVar[varY]
            if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX): 
                fillth1(histo2dStructDict[hname].Gen, fv[ivarX],fv[ivarY],weight)

    #Gen-smearing
    continue
    ntries = 50
    if isdata: weight = 1.0*prescaleweight/ntries    
    else: weight = c.CrossSection/ntries
    for i in range(ntries):
        if not (gMht<150): continue
        smearedJets = smearJets_CC(genjets,9999)
        #smearedJets,csvSmearedJets = smearJets(genjets,matchedCsvVec,_Templates_.ResponseFunctions,_Templates_.hEtaTemplate,_Templates_.hPtTemplate,999)
        mHt = getHT(smearedJets,AnMhtJetPtCut)
        mMhtVec = getMHT(smearedJets,AnMhtJetPtCut)
        mMhtPt, mMhtPhi = mMhtVec.Pt(), mMhtVec.Phi()
        mNJets = countJets(smearedJets,AnMhtJetPtCut)
        mBTags = countBJets_Useful(smearedJets,AnMhtJetPtCut)
        redoneMET = redoMET(genMetVec, genjets, smearedJets)
        mMetPt, mMetPhi = redoneMET.Pt(), redoneMET.Phi()
        mDPhi1,mDPhi2,mDPhi3,mDPhi4 = getDPhis(mMhtVec,smearedJets)
        mJet1Pt,mJet1Eta,mJet2Pt,mJet2Eta,mJet3Pt,mJet3Eta,mJet4Pt,mJet4Eta = getJetKinematics(smearedJets)
        jetPhis = getPhis(smearedJets,mMhtVec)
        fv = [mHt,mMhtPt,mNJets,mBTags,mDPhi1,mDPhi2,mDPhi3,mDPhi4]
        binNumber = getBinNumber(fv)
        fv.append(binNumber)
        fv.append(ientry%2==0)
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist):
                hname = regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname): 
                    fillth1(histoStructDict[hname].GenSmeared, fv[ivar],weight)
            for varpair in var_pairs:
                varY, varX = varpair
                hname = regionkey+'_'+varY+'Vs'+varX
                ivarX, ivarY = indexVar[varX], indexVar[varY]
                if selectionFeatureVector(fv,regionkey,varY+'Vs'+varX):
                    fillth1(histo2dStructDict[hname].GenSmeared, fv[ivarX],fv[ivarY],weight)
        if PrintJets:                
            print 'GEN smeared: nbtags =' , mBTags   
            print fv  
            if fv[-2]!=-1:
                for jet in smearedJets:
                    print 'pt, csv', jet.Pt(), jet.Eta(), jet.csv

fnew.cd()
writeHistoStruct(histoStructDict)
writeHistoStruct(histo2dStructDict)
hHt.Write()
hHtWeighted.Write()
hMht.Write()
hMhtWeighted.Write()


hLeadJetEtaVsNeutralFraction_Blob.Write()
hLeadJetEtaVsNeutralFraction_NonBlob.Write()
hLeadJetEta_Blob.Write()
hLeadJetEta_NonBlob.Write()

for histo in harryhistosReco:
    histo.Write()
for histo in harryhistosReba:
    histo.Write()

hPassFit.Write()
hTotFit.Write()
hPassFar2big.Write()
hTotFar2big.Write()
print 'just created', fnew.GetName()
fnew.Close()

if mktree:
    treefile.cd()
    littletree.Write()
    treefile.Close()
