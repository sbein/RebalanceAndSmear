import os, sys
import argparse
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='Summer16.SMS-T1tttt_mGluino-1200_mLSP-800',help="file")
parser.add_argument("-jersf", "--JerUpDown", type=str, default='Nom',help="JER scale factor (Nom, Up, ...)")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword.strip()
analyzer = args.analyzer
JerUpDown = args.JerUpDown

istest = False


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
    ntupleV = '15'
    isdata = True
    
if 'Run2016' in fnamekeyword: ntupleV = '16'
if 'Run2017' in fnamekeyword: ntupleV = '16'
if 'Run2018' in fnamekeyword: ntupleV = '16'
    
cwd = os.getcwd()
outdir = 'output/'+fnamekeyword.replace(' ','')
if not os.path.exists(outdir):
    os.system('mkdir '+outdir)
            
fnamefilename = 'usefulthings/filelistV'+ntupleV+'.txt'
print 'fnamefilename', fnamefilename
fnamefile = open(fnamefilename)
fnamelines = fnamefile.readlines()
fnamefile.close()
import random
random.shuffle(fnamelines)

os.system('cp /tmp/x509up_u27836  .')
def main():
    for fname_ in fnamelines:
        if not (fnamekeyword in fname_): continue
        fname = fname_.strip()
        job = analyzer.split('/')[-1].replace('.py','').replace('.jdl','')+'-'+fname.strip()+'Jer'+JerUpDown
        job = job.replace('.root','')
        #print 'creating jobs:',job
        '''
        newjdl = open('jobs/'+job+'.jdl','w')
        newjdl.write(jdltemplate.replace('CWD',cwd).replace('JOBKEY',job))
        newjdl.close()
        '''
        newsh = open('jobs/'+job+'.sh','w')
        newshstr = shtemplate.replace('ANALYZER',analyzer).replace('FNAMEKEYWORD',fname).replace('MOREARGS',moreargs).replace('OUTDIR',outdir).replace('CWD',cwd)
        newsh.write(newshstr)
        newsh.close()
        os.chdir('jobs/')
        command = 'condor_qsub -cwd '+job+'.sh &'
        print command
        if not istest: 
        	print 'doing this command', command
        	os.system(command)
        os.chdir('..')
        #cmd =  'condor_submit '+'../../jobs/'+job+'.jdl'  
        sleep(0.18)      


jdltemplate = '''
universe = vanilla
Executable = CWD/jobs/JOBKEY.sh
Output = CWD/jobs/JOBKEY.out
Error = CWD/jobs/JOBKEY.err
Log = CWD/jobs/JOBKEY.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files=CWD/tools, CWD/usefulthings, CWD/src
x509userproxy = x509up_u27836 
Queue 1
'''

shtemplate = '''
#!/bin/zsh
export X509_USER_PROXY=x509up_u27836
source /etc/profile.d/modules.sh
source /afs/desy.de/user/b/beinsam/.bash_profile
module use -a /afs/desy.de/group/cms/modulefiles/
module load cmssw
export THISDIR=$PWD
echo "$QUEUE $JOB $HOST"
source /afs/desy.de/user/b/beinsam/.bash_profile
cd CWD
cmsenv
cd $THISDIR
export timestamp=$(date +%Y%m%d_%H%M%S%N)
mkdir $timestamp
cd $timestamp
cp -r CWD/tools .
cp -r CWD/usefulthings .
cp -r CWD/src .
cp CWD/x509up_u27836 .
python ANALYZER --fnamekeyword FNAMEKEYWORD MOREARGS
mv *.root CWD/OUTDIR/
cd ../
rm -rf $timestamp
'''

main()
print 'done'


