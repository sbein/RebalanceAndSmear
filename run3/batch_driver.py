#!/usr/bin/env python3
"""Reconstruct portable worker state inside the Condor scratch directory."""
import argparse,json,os,shutil,subprocess,tarfile
from pathlib import Path
from common import BASE,root,open_root,metadata,write_metadata,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['raw','closure','rawmerge','templates','predictions'],required=True);p.add_argument('--payload',required=True);args=p.parse_args()
    scratch=Path.cwd();payload=json.loads(Path(args.payload).read_text());run=scratch/'work';run.mkdir()
    write_json(run/'settings.json',payload['settings'])
    if args.stage in ['raw','closure']:
        job=run/'job';job.mkdir();write_json(job/'manifest.json',payload['manifest'])
        if args.stage=='closure':
            for name in ['templates_full.root','normalization.json']:shutil.copy2(scratch/name,run/name)
        subprocess.run(['python3',str(BASE/'production_worker.py'),'--run',str(run),'--job',str(job),'--stage',args.stage],check=True)
        name=args.stage+'_'+payload['id'];source=job/(args.stage+'.root')
        R=root();f=R.TFile(str(source),'UPDATE');record=metadata(R,f);record['submitted_run']=payload['submitted_run'];record['source_commit']=payload['settings']['source_commit']
        if args.stage=='closure':record['template_file']=payload['submitted_run']+'/templates_full.root'
        f.cd();write_metadata(R,record);f.Close();write_json(str(source)+'.json',record)
        if args.stage=='closure':
            # Keep full-event seed records in held-out diagnostics; production transfers histograms/counters only.
            record['seed_tree_saved']=False;original=open_root(R,source);out=R.TFile(str(scratch/(name+'.root')),'RECREATE')
            for key in original.GetListOfKeys():
                if key.GetName() in ['seeds','tCount','run3_metadata']:continue
                out.cd();original.Get(key.GetName()).Write()
            out.cd();counter=R.TTree('tCount','Uncut encountered source events');counter.SetEntries(original.Get('tCount').GetEntries());counter.Write()
            write_metadata(R,record);out.Close();original.Close();write_json(scratch/(name+'.root.json'),record)
        else:
            shutil.copy2(source,scratch/(name+'.root'));shutil.copy2(str(source)+'.json',scratch/(name+'.root.json'))
    else:
        write_json(run/'manifest.json',payload['manifest']);jobs=[]
        for item in payload.get('jobs',[]):
            stage='raw' if args.stage in ['templates','rawmerge'] else 'closure';job=run/'jobs'/item['id'];job.mkdir(parents=True)
            (job/(stage+'.root')).symlink_to(scratch/(stage+'_'+item['id']+'.root'))
            jobs.append(dict(item,job=str(job)))
        write_json(run/'jobs.json',jobs)
        if args.stage=='rawmerge':
            from production_reduce import complete_inputs,merge_raw
            groups,records=complete_inputs(run,'raw');merge_raw(root(),records,scratch/('rawgroup_'+payload['group']+'.root'));return
        if args.stage=='templates' and payload.get('grouped'):
            grouped=run/'grouped_raw';grouped.mkdir()
            for s in payload['manifest']['samples']:
                name='rawgroup_'+s['normalization_group']+'.root';(grouped/name).symlink_to(scratch/name)
        if args.stage=='predictions':shutil.copy2(scratch/'normalization.json',run/'normalization.json')
        subprocess.run(['python3',str(BASE/'production_reduce.py'),'--run',str(run),'--stage',args.stage],check=True)
        if args.stage=='templates':
            for name in ['templates_full.root','templates_full.root.coverage.json','normalization.json','templates_complete.json']:shutil.copy2(run/name,scratch/name)
            with tarfile.open(scratch/'spline_audit.tar.gz','w:gz') as t:t.add(run/'spline_audit',arcname='spline_audit')
        else:
            shutil.copy2(run/'production_complete.json',scratch/'production_complete.json')
            with tarfile.open(scratch/'production_results.tar.gz','w:gz') as t:
                for name in ['predictions','plots','production_complete.json','settings.json','normalization.json']:t.add(run/name,arcname=name)
if __name__=='__main__':main()
