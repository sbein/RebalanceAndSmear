# Full-statistics QCD workflow and revised seed diagnostic

The active seed-cut diagnostic is 90/95/100 GeV. The requested production uses a 90 GeV rebalanced-MHT cut and one independent smear per seed. The historical training configuration remains untouched; these are recorded run settings. Reco remains black points, R&S is one opaque blue filled histogram, and generator smearing is an unfilled green line. No overlapping filled alternatives or alpha colors are used.

## Input coverage

The previous model used ten 100,000-event file prefixes and the training split only. The new production inventory freezes every valid file in the ten published 2024 Summer24 NanoAODv15 HT datasets listed in qcd_2024.json: 2,055 files and 1,131,646,098 uncut events. Original processing versions are kept separate from JMENano and NoPU alternatives. Matching extensions share the same normalization group, cross section and combined uncut count. No matching extensions exist for the selected processing campaign in this inventory. Files are unique across all groups.

## Counting and weights

Every raw-template worker reads a whole original NanoAOD file. Its C++ loop increments `scanned` before any event split, noise filter, jet ID, detector veto or jet requirement. Raw outputs store this encountered count in a branchless `tCount`, using TTree.SetEntries to avoid a billion empty Fill calls. The same counter is written to reduced caches and prediction shards. TChain and hadd behavior is tested explicitly. Counters describe uncut source events, never accepted seeds or smears.

The template reducer requires every frozen file exactly once, validates each counter against the source file's DAS count, sums counters per dataset group and writes normalization.json. Missing or truncated files stop the dependency graph; they never trigger a reduced denominator. Extensions add events to the denominator without adding a second copy of the cross section.

QCD generator weights are ignored. Each observed/rebalanced seed contributes `xsec_pb * luminosity_pb_inverse / ntot_uncut`. Each independent R&S or generator smear contributes that seed weight divided by nsmear. The full-dataset denominator is constant across all shards in the group and is never recomputed from selected events or one file. Current production nsmear=1. Failed fits, rejected seeds and rejected smears keep their original denominator. Each smear starts from the unvarnished rebalanced jets. Raw jet responses retain legacy unit-per-matched-jet filling; the generator priors are stitched with group xsec/ntot before density normalization.

The requested luminosity is 124.0 fb^-1 = 124,000 pb^-1, recorded explicitly. To rescale later, multiply yields and their errors by the luminosity ratio, and covariance bins by its square. Ratios do not change. The seeds tree retains the unnormalized unit seed weight; the shard metadata records its physical normalization and smear weight.

All events are used both for full-statistics template filling and this MC production (split=2). This is explicitly recorded as training overlap and is not an independent closure measurement. The held-out pilot diagnostics remain separate.

## Batch execution and completion

prepare_production.py creates 2,055 raw-template jobs, ten raw group reducers, one model/counting reducer, 2,055 prediction jobs and one final reducer. Prediction depends on successful completion of the entire counted template model. Each phase permits at most 80 simultaneous jobs, uses one CPU per worker, retries I/O failures, and writes shard outputs atomically. A frozen code snapshot preserves the submitted implementation. Code, payloads and outputs are transferred through Condor; every worker uses only its scratch directory and CVMFS, with no NFS access. Group reducers keep model transfer sizes small. Random smearing streams are deterministic per LFN and event, independently salted for generator smearing.

The final reducer requires all prediction shards and identical per-group counters. It merges histograms and independent seed variances/covariances, then recomputes ratios from their sums. Ratios are not added together. Per-HT and all-HT ROOT outputs retain tCount and the full group normalization table. Production transfers histogram and counter shards, including cutflows and normalization metadata; detailed seed records remain in the held-out diagnostics. The final output is production_results.tar.gz with per-HT and all-HT ROOT histograms and plots.

The model still records sparse donors and audits every spline. Nano GenJet>10 and Jet>15 storage limitations cannot be cured by using more events; deficient PDFs remain explicit in the coverage report. No additional JEC/JER, analysis object vetoes or trigger/pileup treatment are introduced by this scale-up. Full signal-region validation remains pending.

Validation includes signed artificial generator weights, two unequal original/extension shards, dynamically counted branchless tCount trees through TChain and hadd, exact dataset-level weights at nsmear=1, and summed prediction variances. A complete real-file batch canary checks the worker runtime before submission of the full DAG. The initial shared-filesystem canary was removed after detecting that LPC worker nodes do not mount /uscms_data. The portable launcher follows [LPC worker I/O guidance](https://www.uscms.org/uscms_at_work/computing/setup/condor_worker_node.shtml).
