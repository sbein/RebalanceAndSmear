#!/usr/bin/env python3
import argparse,hashlib,json,tarfile,os,subprocess
from pathlib import Path
from common import BASE,config,write_json
from inputs import resolve,MAX_EVENTS_QUICK

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--analyzer',choices=['run3/ResponseMaker.py','run3/SkimRandS.py'],required=True)
    p.add_argument('--fnamekeyword',default='QCD_HT1200');p.add_argument('--era',default='2024')
    p.add_argument('--outdir',required=True);p.add_argument('--forcetemplates')
    p.add_argument('--nfiles',type=int,default=None);p.add_argument('--smears',type=int,default=1)
    p.add_argument('--quickrun',action='store_true');p.add_argument('--fixed-photons',action='store_true')
    p.add_argument('--histograms-only',action='store_true')
    args=p.parse_args()
    if args.smears<1:p.error('smears must be positive')
    stage='response' if args.analyzer.endswith('ResponseMaker.py') else 'rands'
    if stage=='rands' and not args.forcetemplates:p.error('Give --forcetemplates for SkimRandS.py')
    nfiles=(1 if args.quickrun else 0) if args.nfiles is None else args.nfiles
    if args.quickrun and nfiles!=1:p.error('Condor quickrun uses one file')
    inventory=resolve(args.fnamekeyword,args.era,nfiles)
    inputs=[f for s in inventory['samples'] for f in s['files']]
    local=all(not f['url'].startswith('root://') for f in inputs)
    if any(not f['url'].startswith('root://') for f in inputs) and not local:raise ValueError('Mixed local and remote sources')
    proxy=os.environ.get('X509_USER_PROXY') or subprocess.check_output(['voms-proxy-info','--path'],text=True).strip()
    if not Path(proxy).is_file():raise FileNotFoundError('Create your CMS proxy first')
    cfg=config();run=Path(args.outdir).resolve();run.mkdir(parents=True,exist_ok=False)
    settings=dict(config=cfg,stage=stage,split=(0 if stage=="response" else 1) if args.quickrun else 2,
        max_events=MAX_EVENTS_QUICK if args.quickrun else -1,nsmear=args.smears,quickrun=args.quickrun,fixed_photons=args.fixed_photons,
        rebalance_mht_max_GeV=95,histograms_only=args.histograms_only)
    archive=run/'code.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for folder in ['run3','src']:
            for file in sorted((BASE.parent/folder).rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.pyc':t.add(file,arcname=str(file.relative_to(BASE.parent)))
    settings['source_archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
    jobs=[]
    for sample in inventory['samples']:
        for source in sample['files']:
            identity=f'{len(jobs):05d}';job=run/'jobs'/identity;job.mkdir(parents=True)
            payload=dict(settings=settings,sample=dict(sample,files=[source]),source=source)
            write_json(job/'payload.json',payload)
            if local:(job/'input.root').symlink_to(Path(source['url']).resolve())
            jobs.append(dict(id=identity,job=str(job),group=sample['normalization_group'],source=source))
    write_json(run/'input_files.json',inventory);write_json(run/'settings.json',settings);write_json(run/'jobs.json',jobs)
    (run/'worker.sh').write_text('#!/usr/bin/env bash\nset -eo pipefail\nexport USER="$(whoami)"\ntar -xzf code.tar.gz\nsource run3/setup.sh\npython3 -u run3/condor_worker.py --payload payload.json\n')
    (run/'worker.sh').chmod(0o755)
    extra=',$(jobdir)/input.root' if local else ''
    if stage=='rands':
        (run/'templates.root').symlink_to(Path(args.forcetemplates).resolve());extra+=','+str(run/'templates.root')
    jdl=f'''universe = vanilla
+DesiredOS = "EL9"
executable = {run}/worker.sh
getenv = False
request_cpus = 1
request_memory = 3500MB
request_disk = 4GB
max_materialize = 80
max_idle = 80
should_transfer_files = YES
when_to_transfer_output = ON_SUCCESS
success_exit_code = 0
transfer_input_files = {archive},$(jobdir)/payload.json{extra}
transfer_output_files = result.root,result.root.json
transfer_output_remaps = "result.root=$(jobdir)/{stage}.root;result.root.json=$(jobdir)/{stage}.root.json"
use_x509userproxy = True
x509userproxy = {Path(proxy).resolve()}
on_exit_hold = (ExitBySignal || (ExitCode != 0))
output = $(jobdir)/$(Cluster).$(Process).out
error = $(jobdir)/$(Cluster).$(Process).err
log = {run}/workers.log
queue jobdir from (
'''+''.join(item['job']+'\n' for item in jobs)+')\n'
    (run/'submit.jdl').write_text(jdl);print('condor_submit '+str(run/'submit.jdl'))

if __name__=='__main__':main()
