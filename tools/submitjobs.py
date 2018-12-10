import os, sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default='Summer16.SMS-T1tttt_mGluino-1200_mLSP-800',help="file")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
analyzer = args.analyzer

istest = False

try: 
	moreargs = ' '.join(sys.argv)
	moreargs = moreargs.split('--fnamekeyword')[-1]	
	moreargs = ' '.join((moreargs.split()[1:]))
except: moreargs = ''

print 'moreargs', moreargs

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
    
cwd = os.getcwd()

fnamefilename = 'usefulthings/filelistV'+ntupleV+'.txt'
print 'fnamefilename', fnamefilename
fnamefile = open(fnamefilename)
fnamelines = fnamefile.readlines()
fnamefile.close()

def main():
    for fname in fnamelines:
		if not (fnamekeyword in fname): continue
		job = analyzer.split('/')[-1].replace('.py','').replace('.jdl','')+'-'+fname.strip()
		#print 'creating jobs:',job
		newjdl = open('jobs/'+job+'.jdl','w')
		newjdl.write(jdltemplate.replace('CWD',cwd).replace('JOBKEY',job))
		newjdl.close()
		newsh = open('jobs/'+job+'.sh','w')
		newshstr = shtemplate.replace('ANALYZER',analyzer).replace('FNAMEKEYWORD',fname).replace('MOREARGS',moreargs)
		newsh.write(newshstr)
		newsh.close()
		if not os.path.exists('output/'+fnamekeyword.replace(' ','')): 
			os.system('mkdir output/'+fnamekeyword.replace(' ',''))
		os.chdir('output/'+fnamekeyword.replace(' ',''))
		cmd =  'condor_submit '+'../../jobs/'+job+'.jdl'        
		print cmd
		if not istest: os.system(cmd)
		os.chdir('../../')


jdltemplate = '''
universe = vanilla
Executable = CWD/jobs/JOBKEY.sh
Output = CWD/jobs/JOBKEY.out
Error = CWD/jobs/JOBKEY.err
Log = CWD/jobs/JOBKEY.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files=CWD/tools, CWD/usefulthings, CWD/src
x509userproxy = $ENV(X509_USER_PROXY)
Queue 1
'''

shtemplate = '''
#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
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
