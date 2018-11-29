from ROOT import *
from utils import *
from array import array
from glob import glob
import os, sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=0,help="increase output verbosity")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='RunIIFall17MiniAODv2.TTJets',help="file")
parser.add_argument("-nprint", "--printevery", type=int, default=100,help="print every n(events)")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
printevery = args.printevery
nametag = ''


'''some random useful directories/filenames:
/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV
Fall17MiniAODv2.TTJets_DiLept_TuneCP5
Run2017B-31Mar2018-v1.JetHT
'''


if 'Summer16' in fnamekeyword: 
    ntupleV = '14'
    isdata = False
elif 'V15a' in fnamekeyword or 'RelVal' in fnamekeyword:
    ntupleV = '15a'
    isdata = False
elif 'Fall17' in fnamekeyword:
	ntupleV = '15'
else: 
    ntupleV = '15'
    isdata = True
if 'Run2016' in fnamekeyword: ntupleV = '14'
if 'Run2017' in fnamekeyword: ntupleV = '15'
if 'Run2018' in fnamekeyword: ntupleV = '15'

    
BTAG_CSV = 0.8484
BTAG_CSV = 0.8838# new with CMSSW_9


hHt = TH1F('hHt','hHt',120,0,2500)
hHt.Sumw2()
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',120,0,2500)
hHtWeighted.Sumw2()


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
    fname = '/eos/uscms//store/user/lpcsusyhad/SusyRA2Analysis2015/Run2ProductionV'+ntupleV+'/'+line
    fname = fname.strip().replace('/eos/uscms/','root://cmsxrootd.fnal.gov//')
    print 'adding', fname
    c.Add(fname)
    filelist.append(fname)
    break

nevents = c.GetEntries()
c.Show(0)
print "nevents=", nevents


newFileName = 'AnalyzerOutput_'+fnamekeyword+'.root'
newFileName = newFileName.replace('.root',nametag+'.root')
fnew = TFile(newFileName,'recreate')

for ientry in range(nevents):
    if ientry%printevery==0:
        print "processing event", ientry, '/', nevents
        
    c.GetEntry(ientry)


    weight = 0.3
    hHt.Fill(c.HT,1)
    hHtWeighted.Fill(c.HT,weight)


    
hHt.Write()
hHtWeighted.Write()

print 'just created file', fnew.GetName()
fnew.Close()
