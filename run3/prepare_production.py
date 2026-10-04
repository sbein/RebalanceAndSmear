#!/usr/bin/env python3
"""Portable full-statistics template -> prediction Condor DAG for LPC."""
import argparse,json,shlex
from pathlib import Path
from common import BASE,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--manifest',required=True)
    p.add_argument('--lumi-pb',type=float,default=1.);p.add_argument('--nsmear',type=int,default=1);p.add_argument('--rebalance-mht-max',type=float,default=90)
    p.add_argument('--source-commit',required=True);p.add_argument('--proxy',required=True);p.add_argument('--max-jobs',type=int,default=80)
    args=p.parse_args();run=Path(args.run).resolve();manifest=json.loads(Path(args.manifest).read_text())
    if not manifest.get('inventory_complete') or args.nsmear<1 or args.lumi_pb<=0:raise ValueError('Require complete inventory, positive luminosity and nsmear')
    if (run/'workflow.dag').exists():raise FileExistsError(run/'workflow.dag')
    run.mkdir(parents=True,exist_ok=True);code=BASE.parent.resolve();archive=run/'production-source.tar.gz'
    if not archive.exists():raise ValueError('Place the frozen run3/src source archive in the run directory first')
    settings=dict(luminosity_pb_inverse=args.lumi_pb,nsmear=args.nsmear,rebalance_mht_max_GeV=args.rebalance_mht_max,
                  generator_weight_policy='ignore',training_split=2,prediction_split=2,source_commit=args.source_commit,
                  max_parallel_jobs_per_category=args.max_jobs,template_overlap=True,worker_io='Condor transfers; local scratch; no NFS access')
    write_json(run/'manifest.json',manifest);write_json(run/'settings.json',settings);jobs=[];dag=[];tpl=[];clos=[]
    worker=run/'worker.sh'
    worker.write_text('#!/usr/bin/env bash\nset -eo pipefail\nexport USER="$(whoami)"\ntar -xzf production-source.tar.gz\nsource run3/setup.sh\npython3 -u run3/batch_driver.py --stage "$1" --payload "$2"\n')
    worker.chmod(0o755)
    def jdl(path,stage,payload,inputs,outputs,memory):
        remaps=';'.join(name+'='+str(destination) for name,destination in outputs)
        path.write_text('universe = vanilla\nexecutable = '+str(worker)+'\narguments = '+stage+' '+payload.name+'\ngetenv = False\nrequest_cpus = 1\nrequest_memory = '+memory+'\nrequest_disk = 4GB\nshould_transfer_files = YES\nwhen_to_transfer_output = ON_SUCCESS\nsuccess_exit_code = 0\ntransfer_input_files = '+','.join(str(p) for p in [archive,payload]+inputs)+'\ntransfer_output_files = '+','.join(name for name,_ in outputs)+'\ntransfer_output_remaps = "'+remaps+'"\nuse_x509userproxy = True\nx509userproxy = '+args.proxy+'\noutput = '+str(path)+'.$(Cluster).out\nerror = '+str(path)+'.$(Cluster).err\nlog = '+str(run)+'/workers.log\nqueue\n')
    for sample in manifest['samples']:
        for source in sample['files']:
            i=len(jobs);identity=f'{i:05d}';job=run/'jobs'/f'{i//500:03d}'/identity;job.mkdir(parents=True)
            single=dict(manifest,samples=[dict(sample,files=[source])]);payload=job/('payload_'+identity+'.json')
            write_json(payload,dict(manifest=single,settings=settings,id=identity,submitted_run=str(run)))
            jobs.append(dict(id=identity,job=str(job),group=sample['normalization_group'],source=source))
            for stage,prefix in [('raw','T'),('closure','C')]:
                name=prefix+identity;path=job/(stage+'.jdl');inputs=[] if stage=='raw' else [run/'templates_full.root',run/'normalization.json']
                outputs=[(stage+'_'+identity+'.root',job/(stage+'.root')),(stage+'_'+identity+'.root.json',job/(stage+'.root.json'))]
                jdl(path,stage,payload,inputs,outputs,'3500MB');dag += [f'JOB {name} {path}',f'CATEGORY {name} {prefix}',f'RETRY {name} 3']
                (tpl if prefix=='T' else clos).append(name)
    write_json(run/'jobs.json',jobs);payload=run/'reduce_payload.json';write_json(payload,dict(manifest=manifest,settings=settings,jobs=[],grouped=True,submitted_run=str(run)))
    final_payload=run/'final_payload.json';write_json(final_payload,dict(manifest=manifest,settings=settings,jobs=jobs,submitted_run=str(run)))
    # Unique transferred basenames avoid collisions among the 2,055 raw.root shards.
    # Input remaps are unavailable, so create unique symlinks for transfer on the submit side.
    inputs=run/'transfer_inputs';inputs.mkdir()
    for stage in ['raw','closure']:
        for item in jobs:
            folder=inputs/f"{int(item['id'])//500:03d}";folder.mkdir(exist_ok=True)
            (folder/(stage+'_'+item['id']+'.root')).symlink_to(Path(item['job'])/(stage+'.root'))
    merges=[];groupfiles=[]
    for index,sample in enumerate(manifest['samples']):
        group=sample['normalization_group'];members=[x for x in jobs if x['group']==group];gp=run/('group_'+group+'.json')
        single=dict(manifest,samples=[sample],source_files=len(members),expected_uncut_events=sample['expected_uncut_events'])
        write_json(gp,dict(manifest=single,settings=settings,jobs=members,group=group,submitted_run=str(run)))
        files=[inputs/f"{int(x['id'])//500:03d}"/('raw_'+x['id']+'.root') for x in members]
        output='rawgroup_'+group+'.root';path=run/('group_'+group+'.jdl');jdl(path,'rawmerge',gp,files,[(output,run/output),(output+'.json',run/(output+'.json'))],'6000MB')
        name='G'+str(index);merges.append(name);groupfiles.append(run/output)
        dag += [f'JOB {name} {path}',f'RETRY {name} 1','PARENT '+' '.join('T'+x['id'] for x in members)+' CHILD '+name]
    for stage,name in [('templates','MODEL'),('predictions','FINAL')]:
        shard_stage='raw' if stage=='templates' else 'closure';files=groupfiles if stage=='templates' else [inputs/f"{int(x['id'])//500:03d}"/(shard_stage+'_'+x['id']+'.root') for x in jobs]
        if stage=='predictions':files.append(run/'normalization.json')
        outputs=[(n,run/n) for n in (['templates_full.root','templates_full.root.coverage.json','normalization.json','templates_complete.json','spline_audit.tar.gz'] if stage=='templates' else ['production_results.tar.gz','production_complete.json'])]
        path=run/(stage+'.jdl');jdl(path,stage,payload if stage=='templates' else final_payload,files,outputs,'6000MB');dag += [f'JOB {name} {path}',f'RETRY {name} 1']
    dag += ['PARENT '+' '.join(merges)+' CHILD MODEL','PARENT MODEL CHILD '+' '.join(clos),'PARENT '+' '.join(clos)+' CHILD FINAL',f'MAXJOBS T {args.max_jobs}',f'MAXJOBS C {args.max_jobs}']
    (run/'workflow.dag').write_text('\n'.join(dag)+'\n')
    print('Prepared',len(jobs),'template jobs and',len(jobs),'prediction jobs; all worker I/O uses transferred scratch files.')
if __name__=='__main__':main()
