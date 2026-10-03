# Legacy selection review, 4 October 2026

All tracked pre-existing files in src/, tools/, bashscripts/ and usefulthings/ remain byte-identical to CMS journal baseline fd9821f. The new Nano reader and event loop are a separate implementation; retaining the historical files and comments does not mean every outer selection is ported. The cached C++ derivative retains the fit structure and many original comments. Its explicit differences are documented in README.md.

## Rebalanced seed acceptance

`tools/RebalanceAndSmear.py:787` requires `fitsucceed and mMhtPt<160` **before** smearing. This is jet-based MHT at pT>30 GeV, |eta|<5, not Nano PuppiMET. The Nano default already had this exact threshold. The fit initialization target min(120,HT/3) is a distinct quantity.

The independent BayesQcd `MaximizePosteriorMakeTree.py` assigns 90 then immediately overrides it with 120 GeV; its effective cut is 120. The SusyPhotons version uses 150. These historical variants do not justify silently replacing the CMS journal default.

`tools/RebalanceAndSmear.py:856` also rejects an individual smear if MHT>2000 GeV, with the original comment "this is a safeguard against mystery". This outer safeguard was missing and is now restored. Exactly 2000 GeV is retained. The smear weight remains seed_weight/nsmears even when a smear is rejected. The literal `99+_Templates_.nparams` smearing argument is restored. The defaults reject nonfinite recoils explicitly.

## What is ported

- The legacy fit thresholds, 12-parameter cap, bounds, initialization, objective and fixed directions; histogram sampling, unchanged tag labels and reordering after fit/smear.
- Modern Run 3 noise filters, official AK4PUPPI TightLeptonVeto ID and Summer24Prompt24_RunBCDEFGHI_V1 event veto map. Additional JEC/JER remain deferred.
- New **jet-only** high/low-delta-phi regions use central jets above 30 GeV, limits 0.5/0.5/0.3/0.3, ignore nonexistent jets, require MHT<HT and apply the legacy Andrews HT-ratio filter. Low-delta-phi and 250–300 GeV sidebands also require HT5/HT<=2.
- Original 174-bin intervals from `loadSearchBins2018`; lower-exclusive/upper-inclusive boundaries and finite 99/9999 upper sentinels. Dummy 175/176 slots are omitted. Histograms are named `SearchBins_jetOnlyHighDPhi_*` and `SearchBins_jetOnlyLowDPhi_*`.
- Per-seed prediction second moments and paired observed/predicted covariance for each new region/bin; ratios remain dimensionless when normalizing spectra and covariances.

## Pending or deliberately changed

- Full analysis electron/muon and isolated electron/muon/pion-track vetoes, photon veto, trigger treatment and MC pileup weighting. Current reduced caches lack these object branches. Porting them requires expanded inputs, era-appropriate definitions and new response/prior derivation as well as closure.
- The exceptional QCD high-MET muon-energy/angle filters, PFCaloMETRatio<5, and unconditional leading-jet neutral-EM fraction>0.03 in the historical MC loop have not been assumed redundant with modern flags or copied blindly to PUPPI jets. Their Run 3 equivalents and effects need validation. The production selection is not complete while these are unresolved.
- Run 2 HEM and 2017 ECAL-era treatment stays in the historical scripts. The 2024 map replaces era-specific masking for the pilot.
- Nearest response matching is explicitly DeltaR<0.4; the old CMS loop allowed 0.5 with an early break below 0.4. Tagging is consistent UParTAK4 rather than the mixed discriminator path in legacy response filling.
- Pilot template binning is coarser. Of 352 slots, 255 are measured, 77 borrowed and 20 structurally unused. Borrowing is recorded, not a convergence claim. Nano's Jet_pt>15 storage threshold still biases low-pT response tails.
- Bounded nonnegative spline evaluation, lookup bounds, complete fixed recoil including jets above the parameter cap, allocation cleanup and caching are explicit derivative changes. `--legacy-pdf-evaluation` and `--uncached-splines` retain diagnostic reference paths.

## Executed validation and closure

The independent legacy-source test checks all 174 bin centers and 4,176 boundary cases, strict 90/100/120/160 seed cuts, the inclusive 2000 GeV smear boundary, central jet ordering, missing-jet handling, the exact Andrews arithmetic and paired seed moments. The numerical reference test checks 28,512 cubic evaluations and 100 real-event fit pairs: both differences are zero. Original legacy files remain unchanged.

The sequential-stream 160 GeV rerun scanned 100,000 cached HT1200–1500 events: 39,116 selected seeds, 37,997 successful fits, 37,863 accepted seeds and 757,260 attempted smears. There were 134 successful fits above the seed cut, 1,119 failed fits, no nonfinite recoils and no smears above 2000. All 13 existing closure histograms reproduce prior bin contents and errors exactly, including flows.

A separate controlled scan uses a deterministic event-key random seed so shared accepted events receive the same draws at every cut. Every seed and fit result is identical, and accepted sets are nested:

| Rebalanced MHT cut | Accepted seeds | Successful fits rejected by cut |
| --- | ---: | ---: |
| <90 GeV | 34,401 | 3,596 |
| <100 GeV | 35,515 | 2,482 |
| <120 GeV | 37,292 | 705 |
| <160 GeV | 37,863 | 134 |

The high-delta-phi MHT>=300 observed sample contains **one** seed in **one** of 174 bins. The low-delta-phi sample occupies 20 bins. The high-delta-phi sideband contains no observed seeds. These outputs demonstrate selection/binning plumbing and cut sensitivity, not statistical closure of every signal region. Individual plotted errors include paired seed statistics; template uncertainties and uncertainties of differences between correlated variants are not included. The scan has not been used to optimize the default on validation data.

Only closure was rerun: these seed/smear guards and supplemental regional histogram selections do not change the currently defined response/prior training. Once the pending universal/object filters are resolved, training and closure must both be rerun on a larger, preferably independent validation sample.

## Reproduction on FNAL

From `/uscms_data/d3/sbein/Ra2slashB2026/RebalanceAndSmear`:

    source run3/setup.sh
    python3 run3/validate_legacy.py
    python3 run3/closure.py --manifest run3_work/cleaned2024/cached_manifest.json --templates run3_work/verified2024/templates_pilot.root --output NEW_REFERENCE.root --max-events 100000 --smears 20 --allow-sparse

For each cut 90,100,120,160, use a fresh `closure_rebalance<CUT>.root` under a new review directory and add `--rebalance-mht-max CUT --per-seed-random`. Keep a `closure_reference160.root` sequential-stream run in that directory, then:

    python3 run3/review_seed_scan.py --directory NEW_REVIEW_DIRECTORY

`--smeared-mht-max` defaults to 2000; `--disable-smear-mht-guard` is an explicitly recorded diagnostic option. Cut overrides do not alter the pinned training metadata. All commands refuse to overwrite their main closure output.
