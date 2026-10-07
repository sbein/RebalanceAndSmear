#!/usr/bin/env python3
"""NanoAOD replacement for ResponseMaker.py; raw histograms, no legacy edits."""
import argparse
import json
from pathlib import Path
from common import *

def make_responses(inputs,output_dir,max_events=-1,split=2):
    cfg=config();ROOT=root(True);configure_cleaning(ROOT,cfg)
    outdir=Path(output_dir);outdir.mkdir(parents=True,exist_ok=True)
    for sample in inputs["samples"]:
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
            path=file["url"]
            stats=ROOT.Run3BuildRaw(path,cfg["btag_branch"],cfg["btag_cut"],vector(ROOT,"string",cfg["filters"]),
                hp,he,hh,vector(ROOT,"TH1F*",responses),vector(ROOT,"TH1F*",priors),max_events,split,True)
            record=summary(stats,["scanned","training","selected","responses","negative","sumw","seconds"])
            record["cleaning"]=cleaning_summary(stats,cfg)
            records.append(dict(file,statistics=record))
            print(sample["name"],record,flush=True)
        sumw=sum(r["statistics"]["sumw"] for r in records)
        if sumw<=0: raise ValueError("Nonpositive processed training sum of weights")
        if any(r["statistics"]["negative"] for r in records):
            raise ValueError("Signed training sample requires validated positive density estimation")


        target=outdir/f'raw_HT{sample["name"]}.root'
        if target.exists(): raise FileExistsError(target)
        f=ROOT.TFile(str(target),"RECREATE");f.cd()
        for h in [hp,he,hh]+responses+priors: h.Write()
        counter=ROOT.TTree("tCount","Uncut source events successfully encountered before any split or selection")
        counter.SetEntries(sum(r["statistics"]["scanned"] for r in records));counter.Write()
        record=dict(stage="response",format_version=1,config=cfg,sample=sample,files=records,split=split,
                    response_weight="unit per isolated matched jet",
                    prior_weight="unit per event; grouped xsec/uncut processed split count",
                    generator_weight_policy="ignore",normalization_group=sample.get("normalization_group",sample["dataset"]))
        write_metadata(ROOT,record);f.Close();write_json(str(target)+".json",record)
        print("Wrote",target,flush=True)

def main():
    from inputs import resolve,MAX_EVENTS_QUICK
    p=argparse.ArgumentParser()
    p.add_argument('--fnamekeyword',default='QCD_HT1200')
    p.add_argument('--era',default='2024')
    p.add_argument('--outdir',default='run3_work/responses')
    p.add_argument('--nfiles',type=int,default=1,help='0: all files')
    p.add_argument('--maxevents',type=int,default=-1)
    p.add_argument('--quickrun',action='store_true')
    a=p.parse_args()
    if a.maxevents==0 or a.maxevents<-1:p.error('maxevents must be -1 or positive')
    make_responses(resolve(a.fnamekeyword,a.era,a.nfiles),a.outdir,
        MAX_EVENTS_QUICK if a.quickrun and a.maxevents==-1 else a.maxevents,0 if a.quickrun else 2)

if __name__=='__main__':main()
