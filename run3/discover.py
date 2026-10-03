#!/usr/bin/env python3
"""Resolve exact datasets from the sample sheet; save DAS provenance and file lists."""
import argparse
import json
import subprocess
from pathlib import Path
from common import BASE, write_json

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--samples",default=str(BASE/"qcd_2024.json"))
    p.add_argument("--out",default="run3_work/manifest.json")
    p.add_argument("--files-per-bin",type=int,default=1,help="0 selects every valid DAS file")
    p.add_argument("--bins",nargs="*")
    p.add_argument("--redirector",default="root://cms-xrd-global.cern.ch/")
    args=p.parse_args()
    if args.files_per_bin<0: p.error("--files-per-bin must be nonnegative")
    source=json.loads(Path(args.samples).read_text())
    records=[]
    for sample in source["samples"]:
        if args.bins and sample["name"] not in args.bins: continue
        result=subprocess.run(["dasgoclient","-query",f'file dataset={sample["dataset"]}',"-json","-limit=0"],
                              check=True,capture_output=True,text=True,timeout=180)
        data=json.loads(result.stdout)
        files={f["name"]:f for entry in data for f in entry.get("file",[])
               if f.get("name","").endswith(".root") and f.get("is_file_valid",1)==1}
        ranked=sorted(files.values(),key=lambda f:(-f.get("nevents",0),f["name"]))
        if not ranked: raise RuntimeError(f'No valid files for {sample["dataset"]}')
        write_json(Path(args.out).parent/"das"/f'{sample["name"]}.json',data)
        chosen=ranked[:args.files_per_bin] if args.files_per_bin else ranked
        records.append(dict(sample,available_files=len(ranked),
          files=[{"lfn":f["name"],"url":args.redirector.rstrip("/")+"/"+f["name"],
                  "nevents":f.get("nevents"),"size":f.get("size"),"adler32":f.get("adler32")} for f in chosen]))
        print(sample["name"],len(ranked),"DAS files;",len(chosen),"selected",flush=True)
    if not records: raise RuntimeError("No matching bins")
    write_json(args.out,dict(source,samples=records))
    print("Wrote",args.out)

if __name__=="__main__": main()
