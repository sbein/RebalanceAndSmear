# Generator smearing and complementary delta-phi diagnostics

The diagnostic scan now includes rebalanced MHT<110 GeV alongside 90,100,120,160. The configured historical default remains 160; this request adds a diagnostic rather than retuning the training configuration.

## Three method overlays

Every new closure plot shows held-out reconstructed QCD, rebalance+smear and generator+smear. Blue and green ratio points each compare their prediction to the same observed seeds. Both ratios include per-seed prediction second moments and observed-predicted covariance. Template uncertainty and uncertainty on differences between correlated methods/cut variants remain outside this pilot.

Generator smearing follows the journal script's separate MC loop: use selected reco events, require generator jet MHT<150 GeV, smear all stored generator jets with `smearJets_CC(genjets,9999)`, retain matched reco tag labels, fixed directions and the legacy pT<8 non-smearing behavior. The existing Nano genJetIdx/DeltaR<0.4 tag association is reused exactly as in training. There is no rebalance-fit or rebalanced-MHT requirement. The legacy gen-smear loop has no 2000 GeV individual-smear veto; large and nonfinite generator-smear recoils are counted explicitly. Nonfinite values are rejected.

Each generator seed uses an independent event-key random stream with a fixed salt. The R&S RNG pointer and state are restored before fitting/smearing. Shared R&S seeds retain the previous deterministic draws; shared generator seeds receive identical draws across all rebalance cuts. Generator acceptance and prediction therefore do not change when the rebalance threshold changes. Each method retains seed_weight/nsmears without renormalizing after selection.

## Inclusive, High Min Dphi and Low Min Dphi

All three new diagnostic views have the same HT>300 GeV and at least two central jets above 30 GeV baseline. They apply no MHT threshold, HT-ratio selection or MHT<HT selection, so the complete spectra remain visible. Existing legacy jet-region plots, including those additional cuts, sidebands and 174-bin histograms, are kept separately and receive gen-smear overlays too.

High Min Dphi requires all available first four pT-ordered central jets to satisfy |DeltaPhi(j_i,MHT)| >=0.5,0.5,0.3,0.3. Low Min Dphi is its exact logical complement: at least one jet fails its own cut. Nonexistent jets are ignored. This is the user-selected legacy inversion, not a common 0.5 cut on every jet. The MinDPhi observable itself is the ordinary minimum absolute angle among these jets.

Observed, R&S and generator-smear bin contents obey Inclusive = High + Low, including flows. Individual prediction variances do not obey this sum because the same seed's smears can populate both regions; per-seed second moments retain those correlations in each view.

Histograms use `<observable>_Inclusive_*`, `<observable>_HighMinDPhi_*`, `<observable>_LowMinDPhi_*`. R&S uses `_prediction` and `_ratio`; gen-smear uses `_genSmear_prediction` and `_genSmear_ratio`, with its own observed clone and covariance. Observables include MHT, HT, NJets, BTags, DPhi1 and MinDPhi. Metadata records the actual cut definitions and independent generator seed cut.

## Validation and reproduction

`validate_gen_smear.py` compares gen-smearing on/off, checks all histogram contents and errors for R&S invariance, checks complementary-region bin sums, generator acceptance independently from seed records, observed clones and paired covariance formulas. The scan additionally compares every existing histogram against the preceding pilot at the original four cuts and checks all generator histograms are unchanged across thresholds.

The original files in src/, tools/, bashscripts/ and usefulthings/ stay unchanged. Template training is reused because these additions change closure diagnostics only. Full analysis object vetoes, exceptional QCD MET filters, trigger/pileup treatment, low-pT Nano storage effects and sparse-template coverage still require production validation.

On FNAL from the repository root:

    source run3/setup.sh
    python3 run3/scan_gen_smear.py --directory NEW_DIRECTORY
    python3 run3/review_gen_smear.py --directory NEW_DIRECTORY

The scan defaults to 100,000 scanned HT1200–1500 events, 20 smears per method per accepted seed and cuts 90/100/110/120/160. Commands refuse to overwrite ROOT outputs. `closure.py --gen-mht-max` and `--gen-smears` permit explicit, recorded generator studies; `--skip-gen-smear` is a regression option. `--min-dphi-cut` supports an explicitly recorded common-angle alternative; the default is the approved legacy inversion.
