import os
from glob import glob
from ROOT import *

TestMode = False

uniquestems = [ 'ZJetsToNuNu_HT-100To200',\
                'ZJetsToNuNu_HT-200To400',\
                'ZJetsToNuNu_HT-400To600',\
				'ZJetsToNuNu_HT-600To800',\
				'ZJetsToNuNu_HT-800To1200',\
				'ZJetsToNuNu_HT-1200To2500',\
				'ZJetsToNuNu_HT-2500ToInf',\
                'WJetsToLNu_HT-100To200',\
                'WJetsToLNu_HT-200To400',\
                'WJetsToLNu_HT-400To600',\
                'WJetsToLNu_HT-600To800',\
                'WJetsToLNu_HT-800To1200',\
                'WJetsToLNu_HT-1200To2500',\
                'WJetsToLNu_HT-2500ToInf',\
                'TTJets_TuneCUETP8M1',\
                'TTJets_HT-600to800',\
                'TTJets_HT-800to1200',\
                'TTJets_HT-1200to2500',\
                'TTJets_HT-2500toInf',\
                'QCD_HT200to300',\
                'QCD_HT300to500',\
                'QCD_HT500to700',\
                'QCD_HT700to1000',\
                'QCD_HT1000to1500',\
                'QCD_HT1500to2000',\
                'QCD_HT2000toInf',\
                'SMS-T2tt_mStop-225_mLSP-50_TuneCUETP8M1',\
                'SMS-T2tt_mStop-250_mLSP-150_TuneCUETP8M1',\
                'SMS-T2tt_mStop-250_mLSP-50_TuneCUETP8M1',\
                'SMS-T2tt_mStop-300_mLSP-150_TuneCUETP8M1',\
                'SMS-T2tt_mStop-425_mLSP-325_TuneCUETP8M1',\
                'SMS-T2tt_mStop-500_mLSP-325_TuneCUETP8M1',\
                'SMS-T2tt_mStop-650_mLSP-350_TuneCUETP8M1',\
                'SMS-T2tt_mStop-850_mLSP-100_TuneCUETP8M1',\
                'SMS-T5qqqqWW_mGluino-1900_mLSP-100',\
                'SMS-T5qqqqZH-mGluino1000_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1300_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1400_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1500_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1600_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1700_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1800_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino1900_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino2000_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino2100_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino2200_TuneCUETP8M1',\
                'SMS-T5qqqqZH-mGluino750_TuneCUETP8M1',\
                'SMS-T1qqqq_mGluino-1000_mLSP-800_TuneCUETP8M1',\
                'SMS-T1qqqq_mGluino-1400_mLSP-100_TuneCUETP8M1',\
                'SMS-T1tttt_mGluino-1200_mLSP-800_TuneCUETP8M1',\
                'SMS-T1tttt_mGluino-1500_mLSP-100_TuneCUETP8M1',\
                'SMS-T1tttt_mGluino-2000_mLSP-100_TuneCUETP8M1',\
                'SMS-T1bbbb_mGluino-1000_mLSP-900_TuneCUETP8M1',\
                'SMS-T1bbbb_mGluino-1500_mLSP-100_TuneCUETP8M1'                
                ]
#sourcedir = '/eos/uscms//store/user/sbein/StealthSusy/Production/ntuple/*'
#sourcedir = '/nfs/dust/cms/user/beinsam/LongLiveTheChi/ntuple_sidecar/smallchunks/*'


#Get signal cross section information
sourcedir = 'trees/smallchunks/skim*'
verbosity = 10000

xsecDictSignalsPb = {}
sigfilenames = glob('/nfs/dust/cms/user/beinsam/LongLiveTheChi/xsecs/own_output_nice_*')
for fname in sigfilenames:
	print 'processing', fname
	fxsec = open(fname)
	lines = fxsec.readlines()
	fxsec.close()
	row1 = lines[1].split()
	idx = row1.index('tot')
	row2 = lines[2].split()
	shortname = fname.split('/')[-1].replace('own_output_nice_','').replace('.txt','')
	xsecDictSignalsPb[shortname] = float(row2[idx])    
    
import numpy as np
for stem in uniquestems:
	targetname = stem.replace('SIM','').replace('step3','').replace('___','_').replace('__','_')
	targetnamewithpath = (sourcedir.replace('*','_')+targetname).replace('/smallchunks','/unweighted')+'.root'
	command = 'hadd -f '+ targetnamewithpath + ' ' + sourcedir+stem+'*.root'
	print command
	if not TestMode: os.system(command)
	fjustcombined = TFile(targetnamewithpath)
	hHt = fjustcombined.Get('hHt')
	try: hHt.SetDirectory(0)
	except: continue
	nsimulated = hHt.GetEntries()
	fjustcombined.Close()
	chain_in = TChain('tEvent')
	chain_in.Add(targetnamewithpath)
	if chain_in.GetEntries()==0: continue
	fileout = TFile(targetnamewithpath.replace('unweighted','weighted'),'recreate')
	tree_out = chain_in.CloneTree(0)
	weight = np.zeros(1, dtype=float)
	b_weight = tree_out.Branch('weight', weight, 'weight/D')
	nentries = chain_in.GetEntries()
	for ientry in range(nentries):
		if ientry % verbosity == 0:
			print 'Processing entry %d of %d' % (ientry, nentries),'('+'{:.1%}'.format(1.0*ientry/nentries)+')'    
		chain_in.GetEntry(ientry)
		if 'pMSSM' in targetname:
			weight[0]=xsecDictSignalsPb[targetname]/nsimulated
		else:
			weight[0] = chain_in.CrossSection*1.0/nsimulated
		if ientry==0: print stem, 'event weight', 100000*weight[0]
		if chain_in.MhtJet2p4>250 or chain_in.MhtJet5p0>250:
			tree_out.Fill()	

	fileout.cd()
	tree_out.Write()
	hHt.Write()		
	print 'just created', fileout.GetName()
	fileout.Close()
os.system('mv trees/weighted/skim_SMS-*.root trees/signal/')
os.system('mv trees/weighted/*.root trees/background/')
print '''
scp trees/background/*.root ${DESY}:/nfs/dust/cms/user/beinsam/Ra2b/Run2Legacy/25Sept2018/CMSSW_10_1_0/src/trees_idealjets/optimization/background/individuals/
scp trees/signal/*.root ${DESY}:/nfs/dust/cms/user/beinsam/Ra2b/Run2Legacy/25Sept2018/CMSSW_10_1_0/src/trees_idealjets/optimization/signal/
'''
