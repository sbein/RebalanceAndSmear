import os, sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='Summer16.SMS-T1tttt_mGluino-1200_mLSP-800',help="file")
parser.add_argument("-jersf", "--JerUpDown", type=str, default='Nom',help="JER scale factor (Nom, Up, ...)")
parser.add_argument("-bootstrap", "--Bootstrap", type=str, default='0',help="boot strapping (0,1of5,2of5,3of5,...)")
parser.add_argument("-selection", "--selection", type=str, default='signal',help="signal, LDP")
parser.add_argument("-quickrun", "--quickrun", type=bool, default=False,help="Quick practice run (True, False)")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword.strip()
analyzer = args.analyzer
JerUpDown = args.JerUpDown
Bootstrap = args.Bootstrap
selection = args.selection
quickrun = args.quickrun

if Bootstrap=='0': 
    bootstrapmode = False
else: 
    bootstrapmode = True
    
istest = False
skipFilesWithErrorFile = False


try: 
	moreargs = ' '.join(sys.argv)
	moreargs = moreargs.split('--fnamekeyword')[-1]	
	moreargs = ' '.join((moreargs.split()[1:]))
except: moreargs = ''

moreargs = moreargs.strip()
print 'moreargs', moreargs



if 'Summer16' in fnamekeyword: 
    ntupleV = '16'
    isdata = False
elif 'V15a' in fnamekeyword or 'RelVal' in fnamekeyword:
    ntupleV = '15a'
    isdata = False
elif 'Fall17' in fnamekeyword:
	ntupleV = '16'
else: 
    ntupleV = '16'
    isdata = True
    
if 'Run2016' in fnamekeyword: ntupleV = '16'
if 'Run2017' in fnamekeyword: ntupleV = '16'
if 'Run2018' in fnamekeyword: ntupleV = '16'
    
cwd = os.getcwd()

fnamefilename = 'usefulthings/filelistSkim_'+selection+'V'+ntupleV+'.txt'
print 'fnamefilename', fnamefilename
fnamefile = open(fnamefilename)
fnamelines = fnamefile.readlines()
fnamefile.close()
import random
random.shuffle(fnamelines)

def main():
    counter = 0    
    for fname_ in fnamelines:
        if not (fnamekeyword in fname_): continue
        print 'made it'
        fname = fname_.strip()
        job = analyzer.split('/')[-1].replace('.py','').replace('.jdl','')+'-'+fname.strip()+''+selection

        #from utils import pause
        #pause()
        job = job.replace('.root','')
        job = job.replace('.root',Bootstrap+'.root')     
        #print 'creating jobs:',job
        newjdl = open('jobs/'+job+'.jdl','w')
        newjdl.write(jdltemplate.replace('CWD',cwd).replace('JOBKEY',job))
        newjdl.close()
        if skipFilesWithErrorFile:
            errfilename = 'jobs/'+job+'.err'
            if os.path.exists(errfilename):  
                continue
        newsh = open('jobs/'+job+'.sh','w')
        newshstr = shtemplate.replace('ANALYZER',analyzer).replace('FNAMEKEYWORD',fname).replace('MOREARGS',moreargs)
        newsh.write(newshstr)
        newsh.close()
        os.system('chmod +x '+'jobs/'+job+'.sh')
        if not os.path.exists('output/'+fnamekeyword.replace(' ','')): 
            os.system('mkdir output/'+fnamekeyword.replace(' ',''))
        os.chdir('output/'+fnamekeyword.replace(' ',''))
        cmd =  'condor_submit '+'../../jobs/'+job+'.jdl'        
        print cmd
        if not istest: os.system(cmd)
        counter+=1
        os.chdir('../../')

    print 'counter', counter
jdltemplate = '''
universe = vanilla
Executable = CWD/jobs/JOBKEY.sh
Output = CWD/jobs/JOBKEY.out
Error = CWD/jobs/JOBKEY.err
Log = CWD/jobs/JOBKEY.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files=CWD/tools, CWD/usefulthings, CWD/src
x509userproxy = /tmp/x509up_u100021
Queue 1
'''

shtemplate = '''#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo $PWD
ls
scram project CMSSW_10_1_0
cd CMSSW_10_1_0/src
eval `scramv1 runtime -sh`
cd ${_CONDOR_SCRATCH_DIR}
echo $PWD
ls
python ANALYZER --fnamekeyword FNAMEKEYWORD MOREARGS
'''

main()
print 'done'
