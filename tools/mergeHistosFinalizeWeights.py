#this module should work just like hadd
from ROOT import *
import glob, os, sys
import numpy as np
from utils import *

istest = False
try: folder = sys.argv[1]
except:
    print 'please give folder name as first argument'
    exit(0)
    
keywords = [\
            'QCD_HT200to300', \
            'QCD_HT300to500', \
            'QCD_HT500to700', \
            'QCD_HT700to1000', \
            'QCD_HT1000to1500', \
            'QCD_HT1500to2000', \
            'QCD_HT2000toInf'
            ]

for keyword in keywords:
    command = 'python tools/ahadd.py -f unwghtd'+keyword+'.root '+folder+'/RandS*'+keyword+'*.root'
    print command
    if not istest: os.system(command)    
    fuw = TFile('unwghtd'+keyword+'.root')
    fw = TFile('wghtd'+keyword+'.root', 'recreate')
    hHt = fuw.Get('hHt')
    nentries = hHt.GetEntries()
    keys = fuw.GetListOfKeys()
    for key in keys:
        name = key.GetName()
        if not len(name.split('/'))>0: continue
        hist = fuw.Get(name)
        hist.Scale(1.0/nentries)
        fw.cd()
        hist.Write()
    fuw.Close()
    command = 'rm unwghtd'+keyword+'.root'
    print command
    if not istest: os.system(command)
    fw.Close()

command = 'hadd -f '+keywords[0].split('_')[0]+ '.root wghtd'+keywords[0].split('_')[0]+'_*'
print command
if not istest: os.system(command)

command = 'rm wghtd'+keywords[0].split('_')[0]+'_*'
print command
if not istest: os.system(command)
