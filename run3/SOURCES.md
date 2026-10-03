# Run 3 cleaning sources and scope

The implementation is for the Summer24 NanoAODv15 QCD MC campaign in `qcd_2024.json`, with the existing NanoAOD jet corrections. Additional JEC/JER processing is deferred at the analysis author's request. Do not use these MC response templates as data-calibrated templates.

## Documentation checked on 2026-10-03

- [CMS NanoAOD workbook](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD): explains branch self-documentation, PUPPI jets, stored corrections and absent MC JER smearing. Its jet-ID discussion stops at v12 and is not a v15 branch inventory.
- [NanoAOD campaign documentation](https://gitlab.cern.ch/cms-nanoAOD/nanoaod-doc/-/wikis/home) and [content auto-documentation](https://cms-nanoaod-integration.web.cern.ch/autoDoc/): linked by the workbook; CERN authentication was required in this session.
- [PdmV Run 3 analysis guidance](https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVRun3Analysis): the supplied reference requires CERN sign-in; its contents have **not** been verified in this session.
- The exact installed `CMSSW_15_0_9` sources were inspected on CVMFS: `PhysicsTools/NanoAOD/python/jetsAK4_Puppi_cff.py`, `nano_cff.py`, `extraflags_cff.py`, and `PhysicsTools/SelectorUtils/interface/PFJetIDSelectionFunctor.h`. Actual v15 files contain no `Jet_jetId`. Jet ID is reconstructed from constituent fractions and multiplicities, using the official payload instead of assuming that branch exists.
- [CMS JetMET recommendations, J. H. Lee, July 2025](https://indico.cern.ch/event/1546228/contributions/6567938/attachments/3095763/5484272/JetMET_01July2025_JhLee%20.pdf), slides 4-5: AND the noisy-event flags; Run 3 jet maps veto the entire event; tight jet ID may be used with or without lepton veto. The talk explicitly says veto-map phase-space choices should be tuned to the analysis.
- Official CAT campaign payloads: `/cvmfs/cms-griddata.cern.ch/cat/metadata/JME/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/2026-07-16/`. Upstream [campaign repository](https://gitlab.cern.ch/cms-analysis-corrections/JME/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15). The config pins the file SHA256 values. `jetvetomaps.json.gz` explicitly recommends `jetvetomap` for both data and MC, with nonzero values indicating vetoed regions. The correction name is `Summer24Prompt24_RunBCDEFGHI_V1`.

## Applied selection

The first pilot already required these eight flags. This update retains them and adds independent failure counts and cumulative cutflows:

```
Flag_goodVertices
Flag_globalSuperTightHalo2016Filter
Flag_EcalDeadCellTriggerPrimitiveFilter
Flag_BadPFMuonFilter
Flag_BadPFMuonDzFilter
Flag_hfNoisyHitsFilter
Flag_eeBadScFilter
Flag_ecalBadCalibFilter
```

All are present in the actual Summer24 v15 files. Missing required flags are fatal, rather than treated as passing. Existence alone does not establish the current POG prescription: the detailed private MET-filter recommendation still requires authenticated verification. Legacy HBHE/CSC flags are not added just because they appear in the tree. The `eeBadSc` flag is retained also in this MC pilot; its measured failure count is reported explicitly.

Events fail jet ID if any stored jet with pT>30 GeV and |eta|<5 fails `AK4PUPPI_Tight`. Low-pT 15-30 GeV seed jets remain available for R&S migrations. The official correction uses the charged plus neutral multiplicities, including its exact fraction and eta boundary semantics. In the central region it requires chHEF>=0.01, whereas the first hand-coded recipe used chHEF>0.

Veto-map candidate jets use pT>15 GeV, |eta|<5, `AK4PUPPI_TightLeptonVeto`, and chEmEF+neEmEF<0.9. This is an explicit **working analysis phase-space choice**, not a claim to have read the private current prescription. There is no separate muon-overlap removal in this inclusive QCD study. The event is rejected if any eligible jet is in the recommended map. Removing only the jet would corrupt the recoil, so no masked jets are dropped from an otherwise accepted event. Both training and observed/seed closure samples receive identical cleaning. Jet directions are fixed during R&S, and smears are conditional on the accepted reconstructed seed; veto eligibility is not reclassified using smeared pT or unavailable smeared constituent fractions.

## Certified data

`audit_selection.py --is-data --golden-json PATH` applies the supplied run/lumisection certification before cleaning, with inclusive lumi-range endpoints. Unknown runs fail. Data mode without a JSON fails; MC mode with a JSON fails to prevent accidental MC certification. The default is MC and certification is bypassed.

The official 2024 file is available under `/cvmfs/cms-griddata.cern.ch/cat/metadata/DC/Collisions24/2026-08-04/Cert_Collisions2024_378981_386951_Golden.json`. Choose and record the certification release appropriate to the final data campaign. The existing template/closure programs remain MC-only; the separate cleaning program does not need generator branches and can optionally produce an Events-only snapshot. It does not replace a complete data analysis.

## Spline audit and numerical corrections

`inspect_schema.py` exports the built-in branch documentation and types from an actual file; the checked Summer24 file contains 2,007 branches and no `Jet_jetId`. This provides a precise v15 content inventory while the web index is inaccessible. It does not establish POG selection recommendations.

`audit_splines.py` examines all 352 PDF slots, including raw statistical support, sparse donors, cubic sign, integral and the fitter's response domain. These are smoothed histograms and cubic interpolation, rather than fitted splines with a convergence test.

The original pilot showed small negative cubic tails, serious extrapolation in a few response bins, and normalization changes after smoothing. This update renormalizes densities **after** smoothing and normalizes the bounded positive cubic curve with deterministic 16,384-step trapezoidal integration over the histogram support. The configured `bounded_nonnegative` evaluator returns zero outside that support, uses constant values across the outer half-bins, and clips negative cubic undershoots to zero. The cubic graph can still be negative; the evaluator never uses a negative probability. The audit independently checks the bounded integral on a 4,096-step grid. This is a numerical repair, not a statistically validated tail model.

`articulate_splines.py --legacy-density-normalization` and `closure.py --legacy-pdf-evaluation` together reproduce the initial pilot's numerical treatment on the cleaned sample, allowing a cleaning-only comparison. The closure switch alone compares signed/unbounded and bounded evaluation on the same newly normalized templates. Cached and uncached execution use the same selected policy. The old `src/` implementation and original pilot products remain unchanged.
