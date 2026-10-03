# Run 3 cleaning sources and scope

The implementation is for the Summer24 NanoAODv15 QCD MC campaign in `qcd_2024.json`, with the existing NanoAOD jet corrections. Additional JEC/JER processing is deferred at the analysis author's request. Do not use these MC response templates as data-calibrated templates.

## Documentation checked on 2026-10-03

- [CMS NanoAOD workbook](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD): explains branch self-documentation, PUPPI jets, stored corrections and absent MC JER smearing. Its jet-ID discussion stops at v12 and is not a v15 branch inventory.
- [NanoAOD content auto-documentation](https://cms-xpog.docs.cern.ch/autoDoc/): authenticated access verified. Its v15/2024 MC table uses the same `RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2` campaign as our QCD samples. All eight required flags are `Bool_t`; jet fractions are `Float_t`, and charged/neutral multiplicities are `UChar_t`. `Jet_jetId` and the aggregate `Flag_METFilters` are absent. The actual QCD file's self-documentation remains the precise inventory for this study.
- [PdmV Run 3 analysis guidance](https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVRun3Analysis), revision 224, dated 2026-10-02: authenticated and read. The 2024 golden JSON matches the filename recorded below. Its 2024 POG/MC sections are still TBD and the NanoAOD discussion includes older productions. Follow current object-group documentation for the v15 prescription.
- [Current JME index](https://cms-jme.docs.cern.ch/recommendations/): the JetMET TWiki now directs readers here. The linked [noise-filter recipe](https://cms-jme-jmar.docs.cern.ch/recommendations/met/noise_filters/) confirms exactly the eight flags below for Run 3, applied to both data and MC. For 2024 use the stored ECAL calibration flag; the 2022/2023 prompt-reco special handling does not apply. HBHE filters are explicitly unnecessary in Run 3; the aggregate METFilters flag is deprecated.
- [Current JMAR Jet ID](https://cms-jme-jmar.docs.cern.ch/recommendations/jet-identification/): v15 requires the matching `jetid.json.gz`; the documented correction inputs and summed multiplicity match the implementation. Fractions use raw jet energy and are kept fixed under JEC/JER. TightLeptonVeto is recommended unless dedicated jet-lepton cleaning already applies. Selection version 3 uses it for this inclusive pilot, which has no dedicated cleaning. Configurations without `analysis_jet_id_wp` retain version 2's Tight behavior for reproduction.
- [Current JERC veto-map recipe](https://cms-jme-jerc.docs.cern.ch/recommendations/jet-veto-maps/): confirms the mandatory whole-event veto and the pT>15 GeV, TightLeptonVeto, EM-fraction<0.9 minimum. The 2024 accordion recommends Summer24Prompt24_V1 and links the same CAT campaign payload we pinned. Its full-period correction key is `Summer24Prompt24_RunBCDEFGHI_V1`, also confirmed by the analysis author. Apply identically to data and matching MC. Run 3's listed minimum has no separate muon-overlap requirement. Check eligible-jet eta/phi maps before and after the event veto and document acceptance losses.
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

All are present in the actual Summer24 v15 files and match the authenticated current POG recipe. Missing required flags are fatal. Legacy HBHE/CSC flags are not added. `eeBadSc` is applied also in MC, as the Run 3 recipe specifies; its measured failure count is reported explicitly.

Events fail jet ID if any stored jet with pT>30 GeV and |eta|<5 fails the configured `AK4PUPPI_TightLeptonVeto`. This replaces Tight for the inclusive pilot; its event-veto threshold and retained 15-30 GeV seed jets are analysis choices. The official correction uses the charged plus neutral multiplicities with its exact fraction and eta boundaries. In the central region it requires chHEF>=0.01, whereas the first hand-coded recipe used chHEF>0.

Veto-map candidates use the verified JERC minimum: pT>15 GeV, `AK4PUPPI_TightLeptonVeto`, and chEmEF+neEmEF<0.9, within the reader's |eta|<5 acceptance. The event is rejected if any eligible jet is masked. Both training and observed/seed closure receive identical cleaning. Jet directions stay fixed during R&S; smears are conditional on accepted reconstructed seeds, without reclassifying ID or veto eligibility using smeared pT. `audit_selection.py --jet-map-dir DIR` saves eligible-jet maps after noise/analysis-ID cuts, before and after the whole-event veto, and checks that no masked eligible jets survive. Maps use unit jet counts, not cross-section weighting; the survival map reflects event rejection and is not a single-jet efficiency.

## Certified data

`audit_selection.py --is-data --golden-json PATH` applies the supplied run/lumisection certification before cleaning, with inclusive lumi-range endpoints. Unknown runs fail. Data mode without a JSON fails; MC mode with a JSON fails to prevent accidental MC certification. The default is MC and certification is bypassed.

The official 2024 file is available under `/cvmfs/cms-griddata.cern.ch/cat/metadata/DC/Collisions24/2026-08-04/Cert_Collisions2024_378981_386951_Golden.json`. Choose and record the certification release appropriate to the final data campaign. The existing template/closure programs remain MC-only; the separate cleaning program does not need generator branches and can optionally produce an Events-only snapshot. It does not replace a complete data analysis.

## Spline audit and numerical corrections

`inspect_schema.py` exports built-in branch documentation and types from an actual file; the checked Summer24 file contains 2,007 branches and no `Jet_jetId`. This complements the now-accessible web inventory and current POG recommendations.

`audit_splines.py` examines all 352 PDF slots, including raw statistical support, sparse donors, cubic sign, integral and the fitter's response domain. These are smoothed histograms and cubic interpolation, rather than fitted splines with a convergence test.

The original pilot showed small negative cubic tails, serious extrapolation in a few response bins, and normalization changes after smoothing. This update renormalizes densities **after** smoothing and normalizes the bounded positive cubic curve with deterministic 16,384-step trapezoidal integration over the histogram support. The configured `bounded_nonnegative` evaluator returns zero outside that support, uses constant values across the outer half-bins, and clips negative cubic undershoots to zero. The cubic graph can still be negative; the evaluator never uses a negative probability. The audit independently checks the bounded integral on a 4,096-step grid. This is a numerical repair, not a statistically validated tail model.

`articulate_splines.py --legacy-density-normalization` and `closure.py --legacy-pdf-evaluation` together reproduce the initial pilot's numerical treatment on the cleaned sample, allowing a cleaning-only comparison. The closure switch alone compares signed/unbounded and bounded evaluation on the same newly normalized templates. Cached and uncached execution use the same selected policy. The old `src/` implementation and original pilot products remain unchanged.
