#!/usr/bin/env python3
"""Held-out NanoAOD closure using the legacy-derived C++ Bayesian fitter."""
import argparse
import json
import math
from pathlib import Path
from common import *

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--templates",required=True)
    p.add_argument("--config")
    p.add_argument("--bin",default="1200to1500")
    p.add_argument("--file-index",type=int,default=0)
    p.add_argument("--max-events",type=int,default=20000)
    p.add_argument("--smears",type=int,default=20)
    p.add_argument("--seed",type=int,default=12345)
    p.add_argument("--output",default="run3_work/closure_HT1200.root")
    p.add_argument("--allow-sparse",action="store_true")
    p.add_argument("--uncached-splines",action="store_true",help="Regression/reference execution")
    p.add_argument("--legacy-pdf-evaluation",action="store_true",help="Diagnostic only: permit negative cubic values and unbounded extrapolation")
    p.add_argument("--rebalance-mht-max",type=float,help="Closure-only seed cut after a successful fit; default is the configured 160 GeV")
    p.add_argument("--smeared-mht-max",type=float,default=2000,help="Legacy safeguard: discard individual smears with MHT above this value")
    p.add_argument("--disable-smear-mht-guard",action="store_true",help="Diagnostic comparison only")
    p.add_argument("--per-seed-random",action="store_true",help="Use common random draws per event for threshold comparisons")
    p.add_argument("--gen-mht-max",type=float,default=150,help="Legacy generator-smear seed cut, independent of rebalance acceptance")
    p.add_argument("--gen-smears",type=int,help="Generator smears per seed; defaults to --smears")
    p.add_argument("--skip-gen-smear",action="store_true",help="Diagnostic regression: disable the alternative prediction")
    p.add_argument("--min-dphi-cut",type=float,help="Use one common minimum-dphi cut for the three diagnostic views; default inverts legacy jet-dependent cuts")
    args=p.parse_args()
    if Path(args.output).exists(): raise FileExistsError(args.output)
    if args.smears<1 or args.seed<1: p.error("smears and random seed must be positive")
    cfg=config(args.config);ROOT=root(True)
    reb_max=cfg["rebalance_mht_max"] if args.rebalance_mht_max is None else args.rebalance_mht_max
    if not math.isfinite(reb_max) or reb_max<=0:p.error("Rebalanced-MHT maximum must be finite and positive")
    if not math.isfinite(args.smeared_mht_max) or args.smeared_mht_max<=0:p.error("Smeared-MHT maximum must be finite and positive")
    smear_max=float("inf") if args.disable_smear_mht_guard else args.smeared_mht_max
    gen_smears=args.smears if args.gen_smears is None else args.gen_smears
    if gen_smears<1:p.error("Generator smears must be positive")
    if not math.isfinite(args.gen_mht_max) or args.gen_mht_max<=0:p.error("Generator MHT maximum must be finite and positive")
    if args.min_dphi_cut is not None and (not math.isfinite(args.min_dphi_cut) or not 0<args.min_dphi_cut<=math.pi):p.error("Minimum dphi cut must be in (0, pi]")
    configure_cleaning(ROOT,cfg)
    if args.legacy_pdf_evaluation: ROOT.Run3BoundedPdf=False
    f=open_root(ROOT,args.templates);record=metadata(ROOT,f);require_compatible(record,cfg)
    if record["sparse_pilot"] and not args.allow_sparse:
        raise ValueError("Pilot borrowed templates require --allow-sparse")
    manifest=json.loads(Path(args.manifest).read_text())
    sample=next(s for s in manifest["samples"] if s["name"]==args.bin)
    file=sample["files"][args.file_index]
    for training in record["training_records"]:
        trained={x["lfn"] for x in training["files"]}
        if file["lfn"] in trained and training["split"]!=0:
            raise ValueError("Closure validation split overlaps template training")
    ROOT.GleanTemplatesFromFile(f)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    stats=ROOT.Run3Closure(file.get("cached_path",file["url"]),cfg["btag_branch"],cfg["btag_cut"],
       vector(ROOT,"string",cfg["filters"]),args.output,args.max_events,args.smears,reb_max,
       args.seed,not args.uncached_splines,1,smear_max,args.per_seed_random,args.gen_mht_max,
       0 if args.skip_gen_smear else gen_smears,-1 if args.min_dphi_cut is None else args.min_dphi_cut)
    values=summary(stats,["scanned","validation","selected","fitted","accepted","smears","sumw","seconds",
                         "rejected_rebalanced_mht","nonfinite_rebalanced","rejected_smeared_mht","nonfinite_smears",
                         "gen_seeds","gen_rejected_mht","gen_smears","gen_nonfinite","gen_above_2000"])
    values["cleaning"]=cleaning_summary(stats,cfg)
    if values["selected"]==0 or values["sumw"]<=0: raise ValueError("No usable validation seeds")
    norm=sample["cross_section_pb"]/values["sumw"]
    result=dict(config=cfg,template_file=str(Path(args.templates).resolve()),input=file,sample=sample,
                statistics=values,smears_per_seed=args.smears,random_seed=args.seed,
                cached_splines=not args.uncached_splines,split=1,normalization_pb_per_genweight=norm,
                bounded_nonnegative_pdf=bool(ROOT.Run3BoundedPdf),
                sparse_pilot=record["sparse_pilot"],borrowed_template_count=len(record["borrowed"]),
                statistical_errors="Seed-cluster second moments; MHT ratio includes paired observed/prediction covariance",
                baseline="HT>300, NJets>=2, applied independently to observed and every smeared event")
    result["closure_selection"]=dict(rebalanced_mht_max_GeV=reb_max,smeared_mht_max_GeV=None if args.disable_smear_mht_guard else smear_max,
        random_draws="per event key" if args.per_seed_random else "legacy sequential stream",
        jet_only_regions="Legacy central-jet delta-phi, MHT<HT, Andrews HT-ratio filter, 174-bin mapping and 250-300 sidebands; no lepton/photon/track veto")
    result["diagnostic_views"]=dict(baseline="HT>300, NJets>=2; no MHT or HT-ratio cut",
        names=["Inclusive","High Min Dphi","Low Min Dphi"],
        dphi_definition="High: all available first four central jets meet 0.5/0.5/0.3/0.3; Low: logical complement" if args.min_dphi_cut is None else f"High: minimum dphi >= {args.min_dphi_cut}; Low: minimum dphi < {args.min_dphi_cut}",
        min_dphi_cut=args.min_dphi_cut,partition="Inclusive = High Min Dphi + Low Min Dphi")
    result["gen_smearing"]=dict(enabled=not args.skip_gen_smear,seed_mht_max_GeV=args.gen_mht_max,
        smears_per_seed=gen_smears,requires_rebalance_acceptance=False,individual_smear_mht_max_GeV=None,
        random_draws="Separate deterministic event-key stream",tags="Current Nano genJetIdx/DR<0.4 reco-tag mapping, identical to template training")
    out=ROOT.TFile(args.output,"UPDATE");out.cd()
    for key in list(out.GetListOfKeys()):
        name=key.GetName();h=out.Get(name)
        if h.InheritsFrom("TH1") and not name.endswith("_ratio"):
            h.Scale(norm*norm if name.endswith("_cross_covariance") else norm)
            h.Write(name,ROOT.TObject.kOverwrite)
    write_metadata(ROOT,result);out.Close();f.Close()
    write_json(args.output+".json",result)
    print(json.dumps(result["statistics"],indent=2))
    print("Wrote",args.output)

if __name__=="__main__": main()
