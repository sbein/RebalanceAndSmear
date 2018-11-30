# RebalanceAndSmear
This is the package for running rebalance and smear on Ra2/b-style ntuples while on an LPC machine. 
## Set up code

```
cmsrel CMSSW_10_1_0
cd CMSSW_10_1_0/src
cmsenv
git clone https://github.com/sbein/RebalanceAndSmear/
cd RebalanceAndSmear/
```

## run a simple analyzer script

```
python tools/SimpleAnalyzer.py --fnamekeyword RunIIFall17MiniAODv2.TTJets
```

## generate jet the response templates and prior distributions

```
python tools/ResponseMaker.py --filenamekey TTJets_Tune
```

## submit large batch of response functions:

If the first time:
```
mkdir output
mkdir output/smallchunks
```

The following script will initiate a large submission 

```
python tools/submitjobs.py --analyzer tools/ResponseMaker.py --fnamekeyword Fall17MiniAODv2.TTJets
```

Output files will be put in the local output/smallchunks directory. The status of the jobs can be checked with

```
condor_q |grep <your user name>
```


 


