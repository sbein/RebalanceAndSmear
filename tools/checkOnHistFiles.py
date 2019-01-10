from ROOT import *
from glob import glob
import os

istest = True
flist = glob('output/Fall17MiniAODv2.QCD_HT/*.root')
#flist = glob('/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/*.root')

timelist = []
for fname in flist:
    created= os.stat(fname).st_ctime
    timelist.append(created)
    #print created, fname
    continue

    '''
    f = TFile(fname)
    h = f.Get('hLowMhtBaseline_MaxDPhiBranch')
    try:
        print h.GetEntries()
        print 'yes', fname		
    except:
        print 'no', fname
        print 'rm '+fname
        if not istest: os.system('rm '+fname)
    f.Close()
    '''

timelist = sorted(timelist)
for t in timelist: print t 
