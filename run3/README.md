# Run 3 NanoAODv15 Rebalance and Smear

This branch adds a NanoAOD input layer and a first 2024 QCD closure workflow. All pre-existing code and response files in src/, tools/, bashscripts/ and usefulthings/ remain unchanged. The Run 3 fitter is an explicitly maintained derivative of the legacy C++ header; inspect its differences with:

    diff -u src/BayesRandS.h run3/BayesRandSRun3.h

## Scope and provenance

- CMS R&S baseline: sbein/RebalanceAndSmear commit fd9821f (the repository's final journal version).
- Fixed-object precedent: sbein/SusyPhotons commit 0b79d87ff1a8a13168cb2ce37acf0fe2fbf683fb.
- Paper and independent implementation: [2206.09583](https://arxiv.org/abs/2206.09583), sbein/BayesQcd commit 1d3f0b7231766ddd9f04aa33e90de7441ade8ac0.
- TreeMaker definitions inspected at sbein/TreeMaker commit 29f75e937540127083d5c9c85ff506a0b1d1a5b1.
- Input datasets and cross sections: [Run 3 MC sheet, rows 15–24](https://docs.google.com/spreadsheets/d/1IVNGwR7Iwx5LRmniAmi9ShiL6DZV8mawkmre7q3Om3s/edit#gid=0), recorded in qcd_2024.json.
- Verified runtime: CMSSW_15_0_9, el9_amd64_gcc12, ROOT 6.32.13, on cmslpc342.fnal.gov.

The historical workflow consists of raw response/prior filling in ResponseMaker.py, smoothing and spline-graph creation in articulateSplines.py, the C++ Bayesian fit, and histogram sampling for smearing. The paper supplies the method description; the code's empirical choices are retained where possible. The likelihood uses the reco/true jet pT ratio with fixed jet directions, multiplied by generator-MHT magnitude and azimuthal priors in HT and b-tag categories. Each seed is unfolded once and smeared repeatedly with weight 1/nsmears.

## Physics choices for this pilot

config_2024.json is authoritative and is embedded in every output. It uses stored, JEC-corrected AK4 PUPPI Jet four-vectors without additional JER smearing or regression. Templates and closure therefore describe the same MC jet definition. These choices need review before predictions on data.

The initial pT grid is coarser than the legacy fine grid to obtain usable pilot statistics, and extends above 1 TeV. Its last bin extends to 10 TeV for lookup coverage, not as a claim of measured response at that scale. Reassess the binning, conditioning variables and high-pT support with a larger training sample.

Real v15 files lack Jet_jetId. The reader recomputes tight PUPPI ID using the energy fractions and multiplicities in [CMS DP-2024/028](https://twiki.cern.ch/twiki/bin/view/CMSPublic/PhysicsResultsDP24028). The constituent-count requirement uses Jet_chMultiplicity + Jet_neMultiplicity, following CMSSW PFJetIDSelectionFunctor, rather than the unweighted Jet_nConstituents. Events are rejected if a jet above 30 GeV and within |eta|<5 fails the ID. Lower-pT seed jets are retained. The current 2024 BTV JSON provides UParTAK4_wp_values:M=0.1272; this cut is used for both response and prior categories. B tagging is restricted to |eta|<2.4 to maintain the legacy acceptance, and scores are mapped to binary 0/1 internally.

Analysis HT and jet counts use pT>30 GeV and |eta|<2.4. Analysis MHT uses pT>30 and |eta|<5. The fit and generator prior use pT>15 and |eta|<5, retaining the legacy prior threshold. Priors require two central gen jets above 30 GeV, or three for the >=3 b-tag category, as in the CMS code. The fit retains its 12-jet parameter cap, initialization target min(120,HT/3), parameter bounds [0.3,3.5], step 0.05 and legacy negative absolute posterior objective. A converged fit must give rebalanced analysis MHT<160 GeV to be smeared.

This first closure has an inclusive QCD selection with the listed event-cleaning flags; it does not yet reproduce the Ra2/b electron, muon, photon, isolated-track, trigger, detector veto-map or search-bin selections. Its diagnostic baseline is HT>300 and NJets>=2, applied separately to reco and smeared events. There is no cut on seed MHT.

Response filling retains the legacy unit weighting of isolated matched jets. Matching uses nearest DeltaR<0.4; gen and reco isolation use a 0.7 cone and pT/sum-pT>0.98. The older CMS script allowed matching up to 0.5, with a break below 0.4, and mixed a CSV discriminator with a DeepCSV threshold in one response-filling path. The Nano port uses one consistent configured tagger and an explicit 0.4 matching requirement.

Priors are filled with raw genWeight, grouped across all shards of each dataset, then scaled once by sigma / processed-training-sumgenWeight. This normalization includes rejected events in the denominator and prevents a per-file normalization bias. Negative-weight training is rejected pending a positive density model. Closure spectra use sigma / processed-validation-sumgenWeight.

## Important template limitation

NanoAOD stores Jet_pt>15 GeV. Matched response distributions at low generator pT consequently miss jets that would have reconstructed below that storage threshold. Low-pT response tails and jet reconstruction inefficiency cannot be recovered by smoothing the stored jets. CorrT1METJet has reduced information and is not silently substituted as a complete jet collection. Before production use, measure this effect and choose a validated treatment, potentially deriving low-pT templates from MiniAOD or a dedicated jet table.

The default articulator fails when a reachable bin lacks the required effective entries. Tagged forward-jet slots are structurally unused because of the central b-tag acceptance; they are explicitly listed and populated with the corresponding untagged distribution only for file compatibility. --allow-sparse is an explicit pilot approximation: it borrows a populated distribution in the same flavour/observable category and records the donor for every substitution in the coverage JSON. No extrapolated bin should be mistaken for a measured density. Histograms retain the legacy smoothing count and ROOT cubic interpolation, including their possible spline overshoot.

## Reproduce the pilot on FNAL

From /uscms_data/d3/sbein/Ra2slashB2026/RebalanceAndSmear:

    source run3/setup.sh
    python3 run3/discover.py --out run3_work/manifest.json --files-per-bin 1
    python3 run3/cache.py --manifest run3_work/manifest.json --out run3_work/cached_manifest.json --max-events-per-file 100000
    python3 run3/response_maker.py --manifest run3_work/cached_manifest.json --max-events-per-file 100000
    python3 run3/articulate_splines.py --inputs 'run3_work/raw/*.root' --output run3_work/templates_pilot.root --allow-sparse
    python3 run3/validate.py --templates run3_work/templates_pilot.root --nano run3_work/cache/HT1200to1500_0.root
    python3 run3/closure.py --manifest run3_work/cached_manifest.json --templates run3_work/templates_pilot.root --bin 1200to1500 --max-events 100000 --smears 20 --allow-sparse
    python3 run3/plot_closure.py run3_work/closure_HT1200.root

Commands refuse to overwrite their main outputs. Use a fresh output name or directory for a new pass. Caches contain only the required branches and record their types and exact LFNs. The stored hashes split events deterministically into training (0) and validation (1), avoiding dependence on event ordering. Training and validation may use the same source file but have disjoint event keys. The closure command rejects overlapping training splits.

ROOT files preserve the histogram/graph names expected by GleanTemplatesFromFile. They also contain metadata, coverage, failed-fit information and one seeds TTree row per selected validation seed. Prediction errors are computed from per-seed contributions, treating repeated smears as correlated. The MHT ratio includes the covariance with the paired observed seeds. Other plotting ratios currently use an explicitly labelled uncorrelated approximation. These errors describe finite seed statistics and finite smearing, not template uncertainty; an independent-file closure and a bootstrap/template-uncertainty study are still needed for production.

## Scale up after validating the pilot

    python3 run3/discover.py --out run3_work/full/manifest.json --files-per-bin 0
    python3 run3/make_condor.py --manifest run3_work/full/manifest.json --outdir run3_work/full/condor
    condor_submit run3_work/full/condor/templates.jdl
    python3 run3/articulate_splines.py --inputs 'run3_work/full/condor/*/raw/*.root' --output run3_work/templates_production.root

The generated jobs target LPC's shared filesystem, use one CPU and the configured proxy, and preserve per-file provenance. Review their runtime environment and coverage before submitting all samples. The code does not submit jobs automatically.

## Core changes and speed checks

BayesRandSRun3.h differs from the baseline in these ways:

- Cache TSpline3 objects with the same construction as [ROOT TGraph::Eval(x,0,"S")](https://root.cern/doc/v632/TGraph_8cxx_source.html); --uncached-splines is the numerical reference path.
- Free Minuit and fit-parameter allocations after each event.
- Bound response lookup and interpolation to valid template bins.
- Include jets beyond the 12-parameter cap in recoil and HT as fixed jets.
- Apply central acceptance consistently when choosing the leading tagged jet.
- Support SetRun3FixedObjects for fixed photon/lepton recoil, following the photon extension's sign convention. This API is tested, but the all-hadronic Nano reader does not yet construct a photon control sample.

validate.py compares every cached density, paired cached/uncached fits on real jets, and fixed recoil with more than 12 jets. These checks establish the optimization's numerical behavior; they do not replace physics closure. Global Minuit/template state remains single-threaded. Scale across independent processes rather than sharing the fitter across threads. ML response modelling is left for a subsequent development.

Initial benchmark: on 2,000 scanned HT800–1000 events (986 validation events, 934 selected seeds, 5 smears per accepted seed), the cached C++ event loop took 0.802 seconds versus 57.112 seconds for the uncached path. Every closure histogram's bin contents and errors was identical. The separate regression checked 28,512 spline evaluations and 100 paired fits, also with zero observed difference. The approximately 71x timing improvement applies to this benchmark and excludes interpreter startup and remote I/O.

## First executed result (2026-10-03)

RESULTS.json records the first complete pilot. Each of the ten QCD HT datasets contributed a 100,000-event prefix from one DAS-selected file. The training split contained 499,532 events, of which 470,172 passed the inclusive pilot selection, yielding 1,350,924 isolated matched jet responses. The template audit found 76 deficient reachable bins and 20 structurally unused forward-tag slots. The pilot records all donors; strict mode rejected the deficient bins as intended.

For HT1200–1500, the disjoint validation split had 50,356 events and 47,781 selected seeds. 46,333 fits converged; 46,098 also passed the MHT<160 acceptance, generating 921,960 smears at 20 per accepted seed. The C++ closure event loop took 54.34 seconds.

This first model does not close throughout MHT: R&S/reco is 1.829 +/- 0.068 in 160–200 GeV and 1.662 +/- 0.100 in 200–250 GeV, where the quoted uncertainties cover seed statistics and finite smearing only. The 300–400 GeV bin gives 0.980 +/- 0.115. The remaining high tail has limited observed MC statistics. No nonclosure correction has been applied. Resolve the low-pT coverage, review template binning and donors, finalize analysis selections, and perform an independent-file closure before production use.
