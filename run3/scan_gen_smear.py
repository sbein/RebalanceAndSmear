#!/usr/bin/env python3
"""Execute controlled seed-cut closures including gen-smear and dphi partitions."""
import argparse,json,subprocess
from pathlib import Path
from common import BASE,root,open_root,write_json
from validate_gen_smear import compare_existing,check_file

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',default='run3_work/gen_smear_dphi20261004')
    p.add_argument('--cuts',type=int,nargs='+',default=[90,95,100]);p.add_argument('--max-events',type=int,default=100000)
    p.add_argument('--smears',type=int,default=20);p.add_argument('--manifest',default='run3_work/cleaned2024/cached_manifest.json')
    p.add_argument('--templates',default='run3_work/verified2024/templates_pilot.root');args=p.parse_args()
    directory=Path(args.directory);directory.mkdir(parents=True,exist_ok=True);R=root();report=[];gen_reference=None
    for cut in args.cuts:
        output=directory/f'closure_rebalance{cut}.root'
        command=['python3',str(BASE/'closure.py'),'--manifest',args.manifest,'--templates',args.templates,'--output',str(output),
            '--max-events',str(args.max_events),'--smears',str(args.smears),'--allow-sparse','--rebalance-mht-max',str(cut),'--per-seed-random']
        with (directory/f'rebalance{cut}.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
        f=open_root(R,output);validation=check_file(R,f)
        old=Path(f'run3_work/legacy_review20261004/closure_rebalance{cut}.root')
        if old.exists() and args.max_events==100000 and args.smears==20:
            previous=open_root(R,old);validation['unchanged_previous_histograms']=compare_existing(previous,f);previous.Close()
        if gen_reference is None:gen_reference=output
        else:
            reference=open_root(R,gen_reference)
            for key in f.GetListOfKeys():
                name=key.GetName()
                if '_genSmear' not in name:continue
                x=f.Get(name);y=reference.Get(name)
                if not x.InheritsFrom('TH1'):continue
                for i in range(x.GetNbinsX()+2):
                    assert x.GetBinContent(i)==y.GetBinContent(i) and x.GetBinError(i)==y.GetBinError(i),(name,i)
            reference.Close();validation['gensmear_unchanged_across_seed_cuts']=True
        stats=json.loads(Path(str(output)+'.json').read_text())['statistics'];f.Close()
        report.append(dict(cut_GeV=cut,statistics=stats,validation=validation))
        write_json(directory/'scan_validation.json',report)
        print('Completed',cut,'GeV:',stats['accepted'],'R&S seeds;',stats['gen_seeds'],'gen seeds;',validation,flush=True)
if __name__=='__main__':main()
