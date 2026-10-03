#!/usr/bin/env python3
"""Apply and report the shared cleaning to MC or certified data without requiring gen branches."""
import argparse
import hashlib
from pathlib import Path
from common import *


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--nano",required=True)
    p.add_argument("--config")
    p.add_argument("--max-events",type=int,default=-1)
    p.add_argument("--is-data",action="store_true")
    p.add_argument("--golden-json")
    p.add_argument("--output",required=True)
    p.add_argument("--snapshot",help="Optional Events-only cleaned ROOT file; input is preserved")
    args=p.parse_args()
    cfg=config(args.config); R=root(True)
    configure_cleaning(R,cfg,args.is_data,args.golden_json)
    frame=R.RDataFrame("Events",args.nano)
    original_columns=[str(c) for c in frame.GetColumnNames()]
    required=cfg["filters"]+["run","luminosityBlock","Jet_pt","Jet_eta","Jet_phi","Jet_chHEF","Jet_neHEF",
              "Jet_chEmEF","Jet_neEmEF","Jet_muEF","Jet_chMultiplicity","Jet_neMultiplicity"]
    missing=set(required)-set(original_columns)
    if missing: raise ValueError("Missing required branches: "+str(sorted(missing)))
    if args.max_events>0: frame=frame.Range(args.max_events)
    results=[("input",frame.Count())]
    current=frame.Filter("Run3PassLumi(run,luminosityBlock)","certified lumis (data only)")
    results.append(("golden_json",current.Count()))
    independent=[]
    for flag in cfg["filters"]:
        independent.append((flag,current.Filter("!"+flag).Count()))
    for flag in cfg["filters"]:
        current=current.Filter(flag,flag)
        results.append((flag,current.Count()))
    shared="Jet_pt,Jet_eta,Jet_chHEF,Jet_neHEF,Jet_chEmEF,Jet_neEmEF,Jet_muEF,Jet_chMultiplicity,Jet_neMultiplicity"
    current=current.Filter("Run3PassAnalysisJetID("+shared+")","analysis jet ID")
    results.append(("jet_id",current.Count()))
    shared=shared.replace("Jet_eta,","Jet_eta,Jet_phi,")
    current=current.Filter("Run3PassVetoMap("+shared+")","jet-veto map")
    results.append(("jet_veto_map",current.Count()))
    report=dict(config=cfg,nano=args.nano,is_data=args.is_data,
                golden_json=args.golden_json,golden_json_sha256=hashlib.sha256(Path(args.golden_json).read_bytes()).hexdigest() if args.golden_json else None,
                cumulative={name:int(count.GetValue()) for name,count in results},
                flag_failures_independent={name:int(count.GetValue()) for name,count in independent},
                scope="Shared event cleaning only; no trigger or analysis lepton/photon/track veto; no additional JEC or JER")
    if args.snapshot:
        if Path(args.snapshot).exists(): raise FileExistsError(args.snapshot)
        current.Snapshot("Events",args.snapshot,vector(R,"string",original_columns))
        report["snapshot"]=args.snapshot
        report["snapshot_scope"]="Events tree only; does not copy Runs/LuminosityBlocks or renormalize MC weights"
    write_json(args.output,report)
    print(report["cumulative"])


if __name__=="__main__": main()
