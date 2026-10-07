* Rebalance and Smear
* * Rebalance and Smear is an old school, data-driven QCD background estimation method for high-MET BSM searches. It was established by the CMS collaboration back in 2011 for SUSY searches in the all-hadronic channel. It has been rebooted and revamped several times for jets+MET and photons+jets+MET final states, and its current form casts Rebalance as a posterior density maximization problem. 
* * Setup for Run 3 Rebalance and Smear 

This README walks through a full chain unit test for Run 3 R&S, focusing only on one bin of QCD HT1200–1500,
from the derivation and finalization of the response templates, to the rebalancing and smearing, to the
histogram construction (closure tests, validation tests, final prediction). Systematics need to be added.

```bash
git clone --branch run3 https://github.com/sbein/RebalanceAndSmear.git
cd RebalanceAndSmear
source run3/setup.sh
voms-proxy-init --voms cms
```

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

Full sample; submit responses first:

```bash
python3 run3/submitjobs.py --analyzer run3/ResponseMaker.py --fnamekeyword QCD_HT1200 --era 2024 --outdir run3_work/full/response_jobs
condor_submit run3_work/full/response_jobs/submit.jdl
```

After these jobs finish, run R&S:

```bash
python3 run3/mergeHistosFinalizeWeights.py run3_work/full/response_jobs --output run3_work/full/responses.root
python3 run3/articulateSplines.py --inputs run3_work/full/responses.root --output run3_work/full/templates.root --allow-sparse
python3 run3/plot_templates.py --templates run3_work/full/templates.root --out run3_work/full/plots/templates
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

Post from a host with SSH access to DESY; on DESY, omit `--host` for a local copy.

`SkimRandS.py` writes a `RandS` tree (`IsRandS`: 0 reco, 1 R&S, 2 gen-smear), closure histograms and uncut `tCount`. Counts and weighting are carried in the ROOT files. Defaults are one smear and 124.0 fb⁻¹; editable constants are in `inputs.py` and `config_2024.json`.

For fixed-photon studies, add `--fixed-photons` to `SkimRandS.py` or its submission command. This uses medium `Photon_cutBased`, pT >20 GeV and |eta| <2.4; it does not impose a diphoton analysis selection.

`--allow-sparse` records borrowed PDFs. The 174 bins remain jet-only; analysis object vetoes, triggers/pileup, additional JEC/JER and template uncertainties remain to be developed. Full-statistics production shares training and prediction events.

Analysis cleaning uses the legacy noise/high-MET cuts and PF/calo MET <5, with an event veto if any stored jet fails ID. Response making keeps its existing selection. Add `--histograms-only` to the R&S command or submission to omit event trees for large closure runs.
