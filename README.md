# Rebalance and Smear

Run 3 HT1200–1500 commands: [run3/README.md](run3/README.md).

Create the pinned ROOT environment once from this directory:

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_15_0_9
cd CMSSW_15_0_9/src
cmsenv
cd ../..
source run3/setup.sh
```

For later sessions, run `source run3/setup.sh`.
