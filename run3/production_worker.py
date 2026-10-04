#!/usr/bin/env python3
"""Atomic, retry-safe full-file template or prediction worker."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from common import BASE,root,open_root,metadata

def validate(path,source,stage):
    R=root();f=open_root(R,path);m=metadata(R,f);counter=f.Get('tCount')
    if not counter or counter.GetEntries()!=source['nevents'] or counter.GetListOfBranches().GetEntries()!=0:raise ValueError('Incomplete or branched tCount: '+str(path))
    if stage=='raw':
        if len(m['files'])!=1 or m['files'][0]['lfn']!=source['lfn']:raise ValueError('Wrong input identity')
        stats=m['files'][0]['statistics']
        if m['generator_weight_policy']!='ignore' or m['split']!=2:raise ValueError('Wrong full-statistics weight/split policy')
    else:
        if m['input']['lfn']!=source['lfn'] or m['normalization']['generator_weight_policy']!='ignore' or m['split']!=2:raise ValueError('Wrong production input/policy')
        stats=m['statistics']
    if stats['scanned']!=source['nevents']:raise ValueError('Source file was not read completely')
    f.Close();return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--job',required=True);p.add_argument('--stage',choices=['raw','closure'],required=True)
    args=p.parse_args();run=Path(args.run).resolve();job=Path(args.job).resolve();manifest=json.loads((job/'manifest.json').read_text())
    source=manifest['samples'][0]['files'][0];settings=json.loads((run/'settings.json').read_text())
    output=job/(args.stage+'.root')
    if output.exists():validate(output,source,args.stage);print('Already complete:',output);return
    attempt=Path(tempfile.mkdtemp(prefix=args.stage+'_attempt_',dir=job))
    if args.stage=='raw':
        subprocess.run(['python3',str(BASE/'response_maker.py'),'--manifest',str(job/'manifest.json'),'--output-dir',str(attempt),'--split','2','--unit-weights','--max-events-per-file','-1'],check=True)
        temporary=attempt/('raw_HT'+manifest['samples'][0]['name']+'.root')
    else:
        temporary=attempt/'closure.root';seed=(int(hashlib.sha256(source['lfn'].encode()).hexdigest()[:8],16)^12345) or 1
        subprocess.run(['python3',str(BASE/'closure.py'),'--manifest',str(job/'manifest.json'),'--bin',manifest['samples'][0]['name'],'--templates',str(run/'templates_full.root'),'--output',str(temporary),
            '--max-events','-1','--split','2','--unit-weights','--normalization',str(run/'normalization.json'),'--allow-training-overlap',
            '--smears',str(settings['nsmear']),'--gen-smears',str(settings['nsmear']),'--rebalance-mht-max',str(settings['rebalance_mht_max_GeV']),
            '--seed',str(seed),'--per-seed-random','--allow-sparse'],check=True)
    validate(temporary,source,args.stage)
    os.replace(str(temporary)+'.json',str(output)+'.json');os.replace(temporary,output)
    print('Completed:',output,flush=True)
if __name__=='__main__':main()
