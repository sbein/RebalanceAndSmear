#!/usr/bin/env python3
"""Prepare an immutable full-statistics template -> prediction Condor DAG."""
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
    run.mkdir(parents=True,exist_ok=True);code=BASE.parent.resolve();write_json(run/'manifest.json',manifest)
    settings=dict(luminosity_pb_inverse=args.lumi_pb,nsmear=args.nsmear,rebalance_mht_max_GeV=args.rebalance_mht_max,
                  generator_weight_policy='ignore',training_split=2,prediction_split=2,source_commit=args.source_commit,
                  code_snapshot=str(code),max_parallel_jobs_per_category=args.max_jobs,template_overlap=True)
    write_json(run/'settings.json',settings);jobs=[];dag=[];tpl=[];clos=[]
    for sample in manifest['samples']:
        for source in sample['files']:
            i=len(jobs);job=run/'jobs'/f'{i:05d}';job.mkdir(parents=True)
            write_json(job/'manifest.json',dict(manifest,samples=[dict(sample,files=[source])]))
            jobs.append(dict(job=str(job),group=sample['normalization_group'],source=source))
            for stage,prefix in [('raw','T'),('closure','C')]:
                name=f'{prefix}{i:05d}';script=job/(stage+'.sh')
                script.write_text('#!/usr/bin/env bash\nset -eo pipefail\ncd '+shlex.quote(str(code))+'\nsource run3/setup.sh\npython3 -u run3/production_worker.py --run '+shlex.quote(str(run))+' --job '+shlex.quote(str(job))+' --stage '+stage+'\n')
                script.chmod(0o755);dag += [f'JOB {name} {run}/worker.jdl',f'VARS {name} script="{script}" memory="3500MB"',f'CATEGORY {name} {prefix}',f'RETRY {name} 3']
                (tpl if prefix=='T' else clos).append(name)
    write_json(run/'jobs.json',jobs)
    for stage,name in [('templates','MODEL'),('predictions','FINAL')]:
        script=run/(stage+'.sh');script.write_text('#!/usr/bin/env bash\nset -eo pipefail\ncd '+shlex.quote(str(code))+'\nsource run3/setup.sh\npython3 -u run3/production_reduce.py --run '+shlex.quote(str(run))+' --stage '+stage+'\n');script.chmod(0o755)
        dag += [f'JOB {name} {run}/worker.jdl',f'VARS {name} script="{script}" memory="6000MB"',f'RETRY {name} 1']
    dag += ['PARENT '+' '.join(tpl)+' CHILD MODEL','PARENT MODEL CHILD '+' '.join(clos),'PARENT '+' '.join(clos)+' CHILD FINAL',f'MAXJOBS T {args.max_jobs}',f'MAXJOBS C {args.max_jobs}']
    (run/'workflow.dag').write_text('\n'.join(dag)+'\n')
    (run/'worker.jdl').write_text('universe = vanilla\nexecutable = $(script)\ngetenv = True\nrequest_cpus = 1\nrequest_memory = $(memory)\nrequest_disk = 4GB\nshould_transfer_files = NO\nuse_x509userproxy = True\nx509userproxy = '+args.proxy+'\noutput = '+str(run)+'/$(Cluster).$(Process).out\nerror = '+str(run)+'/$(Cluster).$(Process).err\nlog = '+str(run)+'/workers.log\nqueue\n')
    print('Prepared',len(jobs),'full-file template jobs and',len(jobs),'prediction jobs; dependencies prevent prediction before complete counted templates.')
if __name__=='__main__':main()
