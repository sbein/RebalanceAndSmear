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
```

Assuming you have a valid proxy, the following script will initiate a large submission 

```
python tools/submitjobs.py --analyzer tools/ResponseMaker.py --fnamekeyword Fall17MiniAODv2.TTJets #(for 2017)
python tools/submitjobs.py --analyzer tools/ResponseMaker.py --fnamekeyword Summer16.QCD_HT #(for 2016)
```

Output files will be put in the local output/<keyword> directory matching the specified keyword for the filename. The status of the jobs can be checked with

```
condor_q |grep <your user name>
```

Once the jobs are done, a wrapper for the hadd routine can be called which also fits a spline to each response function:

```
python tools/articulateSplines.py ResponseTemplates2017.root "output/Fall17MiniAODv2.TTJets/*Fall17MiniAODv2.TTJets*.root"
python tools/articulateSplines.py ResponseTemplates2016.root "output/Summer16.QCD_HT/*Summer16.QCD_HT*.root"
```



 


