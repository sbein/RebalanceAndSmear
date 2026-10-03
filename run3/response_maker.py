#!/usr/bin/env python3
"""NanoAOD replacement for ResponseMaker.py; raw histograms, no legacy edits."""
import argparse
import json
from pathlib import Path
from common import *

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--config")
    p.add_argument("--output-dir",default="run3_work/raw")
    p.add_argument("--max-events-per-file",type=int,default=-1)
    p.add_argument("--bins",nargs="*")
    p.add_argument("--split",type=int,choices=[0,1,2],default=0,help="0 training, 1 validation, 2 all")
    args=p.parse_args()
    cfg=config(args.config); ROOT=root(True)
    manifest=json.loads(Path(args.manifest).read_text())
    outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True)
    for sample in manifest["samples"]:
        if args.bins and sample["name"] not in args.bins: continue
        hp=axis(ROOT,"hPtTemplate",cfg["pt_edges"])
        he=axis(ROOT,"hEtaTemplate",cfg["eta_edges"])
        hh=axis(ROOT,"hHtTemplate",cfg["ht_edges"])
        responses=[]
        for tag in range(2):
            for ie in range(he.GetNbinsX()):
                for ip in range(hp.GetNbinsX()):
                    upper,nbin=(4.0,650) if cfg["pt_edges"][ip]<17 else (3.0,350)
                    h=ROOT.TH1F(response_name(cfg["pt_edges"],cfg["eta_edges"],ip,ie,tag),"Response",nbin,0,upper)
                    h.Sumw2();responses.append(h)
        priors=[]
        mht_edges=list(range(0,101))+list(range(102,151,2))+list(range(155,201,5))+[220,240,260,280,300,400,500,800]
        for tag in range(4):
            for ih in range(hh.GetNbinsX()+1):
                h=axis(ROOT,prior_name(cfg["ht_edges"],ih,tag,"Pt"),mht_edges);h.Sumw2();priors.append(h)
                h=ROOT.TH1F(prior_name(cfg["ht_edges"],ih,tag,"Phi"),"MHT azimuthal prior",126,0,3.15)
                h.Sumw2();priors.append(h)
        records=[]
        for file in sample["files"]:
            path=file.get("cached_path",file["url"])
            stats=ROOT.Run3BuildRaw(path,cfg["btag_branch"],cfg["btag_cut"],vector(ROOT,"string",cfg["filters"]),
                hp,he,hh,vector(ROOT,"TH1F*",responses),vector(ROOT,"TH1F*",priors),args.max_events_per_file,args.split)
            record=summary(stats,["scanned","training","selected","responses","negative","sumw","seconds"])
            records.append(dict(file,statistics=record))
            print(sample["name"],record,flush=True)
        sumw=sum(r["statistics"]["sumw"] for r in records)
        if sumw<=0: raise ValueError("Nonpositive processed training sum of weights")
        if any(r["statistics"]["negative"] for r in records):
            raise ValueError("Signed training sample requires validated positive density estimation")
        # Keep priors unnormalized in shards. The articulator groups by dataset and
        # normalizes once using the full processed training sum, avoiding per-file bias.
        target=outdir/f'raw_HT{sample["name"]}.root'
        if target.exists(): raise FileExistsError(target)
        f=ROOT.TFile(str(target),"RECREATE");f.cd()
        for h in [hp,he,hh]+responses+priors: h.Write()
        record=dict(format_version=1,config=cfg,sample=sample,files=records,split=args.split,
                    response_weight="unit per isolated matched jet",
                    prior_weight="raw genWeight; articulator normalizes each dataset after merging shards")
        write_metadata(ROOT,record);f.Close();write_json(str(target)+".json",record)
        print("Wrote",target,flush=True)

if __name__=="__main__": main()
