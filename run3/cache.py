#!/usr/bin/env python3
"""Cache only needed branches and a bounded event prefix, using compiled ROOT I/O."""
import argparse
import json
from pathlib import Path
from common import config, root, vector, open_root, write_json

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--config")
    p.add_argument("--out",default="run3_work/cached_manifest.json")
    p.add_argument("--max-events-per-file",type=int,default=100000)
    args=p.parse_args()
    cfg=config(args.config); ROOT=root()
    manifest=json.loads(Path(args.manifest).read_text())
    branches=["run","luminosityBlock","event","genWeight","Jet_pt","Jet_eta","Jet_phi","Jet_mass",
      cfg["btag_branch"],"Jet_neHEF","Jet_neEmEF","Jet_chHEF","Jet_chMultiplicity",
      "Jet_neMultiplicity","Jet_nConstituents","Jet_genJetIdx","GenJet_pt","GenJet_eta","GenJet_phi","GenJet_mass"]+cfg["filters"]
    cache=Path(args.out).resolve().parent/"cache";cache.mkdir(parents=True,exist_ok=True)
    for s in manifest["samples"]:
        for i,record in enumerate(s["files"]):
            target=cache/f'HT{s["name"]}_{i}.root'
            if target.exists(): raise FileExistsError(f"Cache already exists: {target}")
            print("Caching",s["name"],record["url"],flush=True)
            f=open_root(ROOT,record["url"]);t=f.Get("Events")
            missing=[b for b in branches if not t.GetBranch(b)]
            if missing: raise ValueError(f"Missing branches: {missing}")
            leaf_types={b:t.GetLeaf(b).GetTypeName() for b in branches}
            f.Close()
            frame=ROOT.RDataFrame("Events",record["url"])
            if args.max_events_per_file>0: frame=frame.Range(args.max_events_per_file)
            frame.Snapshot("Events",str(target),vector(ROOT,"string",branches))
            cached=open_root(ROOT,target);count=cached.Get("Events").GetEntries();cached.Close()
            record.update(cached_path=str(target),cached_entries=count,branch_types=leaf_types)
            write_json(args.out,dict(manifest,cache_max_events=args.max_events_per_file))
            print("Cached",count,"events",flush=True)

if __name__=="__main__": main()
