**Rebalance and Smear**
Rebalance and Smear is an old school, data-driven QCD background estimation method for high-MET BSM searches. It was established by the CMS collaboration back in 2011 for SUSY searches in the all-hadronic channel. It has been rebooted and revamped several times for jets+MET and photons+jets+MET final states, and its current form casts Rebalance as a posterior density maximization problem. 

**Setup for Run 3 Rebalance and Smear** 

This README walks through a full chain unit test for Run 3 R&S, focusing only on one bin of QCD HT1200–1500,
from the derivation and finalization of the response templates, to the rebalancing and smearing, to the
histogram construction (closure tests, validation tests, final prediction). Systematics need to be added.

```bash
git clone --branch run3 https://github.com/sbein/RebalanceAndSmear.git
cd RebalanceAndSmear
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_15_0_9
cd CMSSW_15_0_9/src
cmsenv
cd ../..
source run3/setup.sh
voms-proxy-init --voms cms
```

Create the release area once. In a new shell, run `source run3/setup.sh`; workers create their own area in scratch.

`--quickrun` specifies to run over  100,000 entries;

```bash
python3 run3/ResponseMaker.py --fnamekeyword QCD_HT1200 --era 2024 --quickrun --outdir run3_work/pilot/responses
python3 run3/articulateSplines.py --inputs "run3_work/pilot/responses/*.root" --output run3_work/pilot/templates.root --allow-sparse
python3 run3/plot_templates.py --templates run3_work/pilot/templates.root --out run3_work/pilot/plots/templates
python3 run3/SkimRandS.py --fnamekeyword QCD_HT1200 --era 2024 --quickrun --forcetemplates run3_work/pilot/templates.root --outdir run3_work/pilot/skims
python3 run3/mergeHistosFinalizeWeights.py run3_work/pilot/skims --output run3_work/pilot/prediction.root
python3 run3/closurePlotter.py run3_work/pilot/prediction.root --region Inclusive --outdir run3_work/pilot/plots/Inclusive
python3 run3/closurePlotter.py run3_work/pilot/prediction.root --region HighMinDPhi --outdir run3_work/pilot/plots/HighMinDPhi
python3 run3/closurePlotter.py run3_work/pilot/prediction.root --region LowMinDPhi --outdir run3_work/pilot/plots/LowMinDPhi
python3 run3/closurePlotter.py run3_work/pilot/prediction.root --region Legacy --outdir run3_work/pilot/plots/Legacy
```

Submit responses histogram dervivation jobs first:

```bash
python3 run3/submitjobs.py --analyzer run3/ResponseMaker.py --fnamekeyword QCD_HT1200 --era 2024 --outdir run3_work/full/response_jobs
condor_submit run3_work/full/response_jobs/submit.jdl
```

After these jobs finish, process the response histograms and smooth with splines:

```bash
python3 run3/mergeHistosFinalizeWeights.py run3_work/full/response_jobs --output run3_work/full/responses.root
python3 run3/articulateSplines.py --inputs run3_work/full/responses.root --output run3_work/full/templates.root --allow-sparse
python3 run3/plot_templates.py --templates run3_work/full/templates.root --out run3_work/full/plots/templates
```

Finally, you are ready to rebalance and smear. Warning: do not attempt to smear before rebalancing. It is not good to do, and you will regret i. 
```
python3 run3/submitjobs.py --analyzer run3/SkimRandS.py --fnamekeyword QCD_HT1200 --era 2024 --forcetemplates run3_work/full/templates.root --outdir run3_work/full/rands_jobs
condor_submit run3_work/full/rands_jobs/submit.jdl
```

After the R&S jobs finish:

```bash
python3 run3/mergeHistosFinalizeWeights.py run3_work/full/rands_jobs --output run3_work/full/prediction.root
python3 run3/closurePlotter.py run3_work/full/prediction.root --region Inclusive --outdir run3_work/full/plots/Inclusive
python3 run3/closurePlotter.py run3_work/full/prediction.root --region HighMinDPhi --outdir run3_work/full/plots/HighMinDPhi
python3 run3/closurePlotter.py run3_work/full/prediction.root --region LowMinDPhi --outdir run3_work/full/plots/LowMinDPhi
python3 run3/closurePlotter.py run3_work/full/prediction.root --region Legacy --outdir run3_work/full/plots/Legacy
python3 run3/publish.py --source run3_work/full/plots --host beinsam@naf-cms16.desy.de --destination /afs/desy.de/user/b/beinsam/www/Ra2slashB2026/run3-riley-ht1200
```

`--fnamekeyword` also accepts a NanoAOD ROOT file, ROOT glob, XRootD URL or text file list for this HT sample. `--nfiles 0` processes all files locally; Condor already defaults to all files. No input cache is made.
