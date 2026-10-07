#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import os
import subprocess
import tarfile
from pathlib import Path
from common import BASE,root,configure_cleaning,vector,open_root,write_json,write_metadata,metadata

HT_LIMITS = [2., 1.8, 1.5, 1.3]
MET_LIMITS = [100., 80., 60., 40.]
CORE_FILES = ['NanoReader.h','EventCleaning.h','LegacyJetSelection.h','SearchBins2018.h',
    'Workflow.h','BayesRandSRun3.h','../src/UsefulJet.h','common.py']
MHT_EDGES = [0,30,60,90,120,160,200,250,300,400,500,700,1000,1500,2500]
FAMILIES = ['MHT_Inclusive','MHT_HighMinDPhi','MHT_LowMinDPhi',
    'MHT_jetOnlyHighDPhi','MHT_jetOnlyLowDPhi','MHT_jetOnlyHighDPhiSideband',
    'MHT_jetOnlyLowDPhiSideband','SearchBins_jetOnlyHighDPhi','SearchBins_jetOnlyLowDPhi']

def variants():
    def label(x): return str(x).rstrip('0').rstrip('.').replace('.','p') if '.' in str(x) else str(x)
    result = [dict(name='Baseline',ht_max=-1.,met_max=-1.,met_type=0)]
    for ht in HT_LIMITS:
        result.append(dict(name='HT'+label(ht),ht_max=ht,met_max=-1.,met_type=0))
    for met_type,collection in [(1,'PF'),(2,'Puppi')]:
        for met in MET_LIMITS:
            result.append(dict(name=collection+label(met),ht_max=-1.,met_max=met,met_type=met_type))
        for ht in HT_LIMITS:
            for met in MET_LIMITS:
                result.append(dict(name='HT'+label(ht)+'_'+collection+label(met),
                                   ht_max=ht,met_max=met,met_type=met_type))
    return result

def source_groups(record):
    normalization=record['production_normalization']
    if not normalization['complete'] or normalization['generator_weight_policy']!='ignore':
        raise ValueError('A complete uncut production normalization is required')
    groups={}
    for name,item in normalization['groups'].items():
        weight=item['cross_section_pb']*normalization['luminosity_pb_inverse']/item['ntot_uncut']
        if not math.isfinite(weight) or weight<=0: raise ValueError('Invalid event weight')
        for lfn in item['source_lfns']:
            if lfn in groups: raise ValueError('Duplicate normalization source')
            groups[lfn]=(name,weight)
    return groups

def scanner_identity():
    return {name:hashlib.sha256((BASE/name).read_bytes()).hexdigest()
            for name in CORE_FILES+['TargetCuts.h','TargetScan.h','targetCutScan.py']}

def worker(payload_path,output='result.root'):
    payload=json.loads(Path(payload_path).read_text());cfg=payload['config'];R=root(True)
    if payload['code_sha256']!=scanner_identity():raise ValueError('Target scanner source changed')
    configure_cleaning(R,cfg)
    if not R.gInterpreter.Declare('#include "run3/TargetScan.h"'):raise RuntimeError('Target scanner compilation failed')
    choices=R.std.vector('Run3TargetVariant')()
    for item in payload['variants']:
        v=R.Run3TargetVariant();v.name=item['name'];v.htMaximum=item['ht_max']
        v.metMaximum=item['met_max'];v.metType=item['met_type'];choices.push_back(v)
    stats=R.Run3TargetScan(payload['input']['url'],output,cfg['btag_branch'],cfg['btag_cut'],
        vector(R,'string',cfg['analysis_cleaning']['filters']),choices,payload['min_mht'],-1)
    if int(stats.scanned)!=payload['input']['nevents']: raise ValueError('Incomplete input scan')
    result=dict(payload,statistics={name:int(getattr(stats,name)) for name in ['scanned','candidates','selected']})
    f=R.TFile(output,'UPDATE');f.cd();write_metadata(R,result);f.Close();write_json(output+'.json',result)
    print(json.dumps(result['statistics']),flush=True)

def prepare(baseline,outdir,minimum,condor,nfiles):
    baseline=Path(baseline).resolve();record=json.loads(Path(str(baseline)+'.json').read_text())
    if record.get('fixed_objects')!='none':raise ValueError('This QCD diagnostic requires fixed_objects=none')
    if record['settings']['split']!=2:raise ValueError('This diagnostic requires the full, unsplit production')
    cfg=record['config'];groups=source_groups(record);inputs=record['inputs']
    original_archive=baseline.parent.parent/'code.tar.gz';core_verified=False
    if original_archive.exists():
        if hashlib.sha256(original_archive.read_bytes()).hexdigest()!=record['settings']['source_archive_sha256']:
            raise ValueError('Original production source archive changed')
        with tarfile.open(original_archive) as archive:
            for name in CORE_FILES:
                member=str(Path(os.path.normpath('run3/'+name)))
                if archive.extractfile(member).read()!=(BASE/name).read_bytes():
                    raise ValueError('Physics source differs from original production: '+name)
        core_verified=True
    if len({f['lfn'] for f in inputs})!=len(inputs):raise ValueError('Duplicate input file')
    if not set(f['lfn'] for f in inputs).issubset(groups):raise ValueError('Unnormalized input file')
    if not set(f['lfn'] for f in inputs)==set(groups):raise ValueError('Use the complete all-HT prediction')
    run=Path(outdir).resolve();run.mkdir(parents=True,exist_ok=False)
    original_jobs=baseline.parent.parent/'jobs.json';old={}
    if original_jobs.exists():
        old={j['source']['lfn']:Path(j['job'])/'rands.root' for j in json.loads(original_jobs.read_text())}
    R=root() if old else None;jobs=[];skipped=[];selected_inputs=inputs[:nfiles] if nfiles else inputs
    for source in selected_inputs:
        if source['lfn'] in old:
            f=open_root(R,old[source['lfn']]);prior=metadata(R,f);count=0
            if prior['input']['lfn']!=source['lfn'] or prior['config']!=cfg or prior['normalization']['event_weight']!=groups[source['lfn']][1]:
                raise ValueError('Original source selection or normalization differs')
            if int(f.Get('tCount').GetEntries())!=source['nevents']:
                raise ValueError('Original source was not completely scanned')
            for family in FAMILIES[:7]:
                h=f.Get(family+'_observed')
                if not h: raise ValueError('Missing original target histogram')
                count+=h.Integral(h.FindBin(minimum),h.GetNbinsX()+1)
            f.Close()
            if count==0:
                skipped.append(source);continue
        identity=hashlib.sha256(source['lfn'].encode()).hexdigest()[:16]
        folder=run/'jobs'/identity;folder.mkdir(parents=True)
        group,weight=groups[source['lfn']]
        payload=dict(input=source,group=group,event_weight=weight,config=cfg,min_mht=minimum,variants=variants(),code_sha256=scanner_identity())
        write_json(folder/'payload.json',payload);jobs.append(dict(job=str(folder),**payload))
    settings=dict(baseline=str(baseline),baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
        min_mht=minimum,variants=variants(),config=cfg,code_sha256=scanner_identity(),inputs=selected_inputs,skipped_empty_sources=skipped,
        complete_source_coverage=nfiles==0,core_matches_original_archive=core_verified,normalization=record['normalization'],
        production_normalization=record['production_normalization'],prediction_policy='Frozen baseline R&S and gen-smear')
    write_json(run/'settings.json',settings);write_json(run/'jobs.json',jobs)
    if condor:
        archive=run/'code.tar.gz'
        with tarfile.open(archive,'w:gz') as t:
            for folder in ['run3','src']:
                for file in sorted((BASE.parent/folder).rglob('*')):
                    if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.pyc':
                        t.add(file,arcname=str(file.relative_to(BASE.parent)))
        proxy=os.environ.get('X509_USER_PROXY') or subprocess.check_output(['voms-proxy-info','--path'],text=True).strip()
        if not Path(proxy).is_file():raise FileNotFoundError('Create a CMS proxy first')
        (run/'worker.sh').write_text('#!/usr/bin/env bash\nset -eo pipefail\nexport USER="$(whoami)"\ntar -xzf code.tar.gz\nsource run3/setup.sh\npython3 -u run3/targetCutScan.py --payload payload.json\n')
        (run/'worker.sh').chmod(0o755)
        jdl=f'''universe = vanilla
+DesiredOS = "EL9"
executable = {run}/worker.sh
getenv = False
request_cpus = 1
request_memory = 2500MB
request_disk = 4GB
max_materialize = 80
max_idle = 80
should_transfer_files = YES
when_to_transfer_output = ON_SUCCESS
success_exit_code = 0
transfer_input_files = {archive},$(jobdir)/payload.json
transfer_output_files = result.root,result.root.json
transfer_output_remaps = "result.root=$(jobdir)/target.root;result.root.json=$(jobdir)/target.root.json"
use_x509userproxy = True
x509userproxy = {Path(proxy).resolve()}
on_exit_hold = (ExitBySignal || (ExitCode != 0))
output = $(jobdir)/$(Cluster).$(Process).out
error = $(jobdir)/$(Cluster).$(Process).err
log = {run}/workers.log
queue jobdir from (
'''+''.join(j['job']+'\n' for j in jobs)+')\n'
        (run/'submit.jdl').write_text(jdl);print('condor_submit '+str(run/'submit.jdl'))
    else:
        for j in jobs:worker(Path(j['job'])/'payload.json',str(Path(j['job'])/'target.root'))
    print(f'{len(jobs)} readers; {len(skipped)} sources with no baseline targets above {minimum:g} GeV')
    return run

def merge(outdir):
    run=Path(outdir);settings=json.loads((run/'settings.json').read_text());jobs=json.loads((run/'jobs.json').read_text())
    if not settings['complete_source_coverage']:raise ValueError('Pilot outputs cannot validate full-production closure')
    baseline=Path(settings['baseline'])
    if hashlib.sha256(baseline.read_bytes()).hexdigest()!=settings['baseline_sha256']:raise ValueError('Baseline file changed')
    R=root();sums={};scanned=0;selected=0
    for j in jobs:
        path=Path(j['job'])/'target.root';d=json.loads(Path(str(path)+'.json').read_text())
        expected={k:j[k] for k in ['input','group','event_weight','config','min_mht','variants','code_sha256']}
        if any(d.get(k)!=v for k,v in expected.items()):raise ValueError('Worker settings differ')
        if d['statistics']['scanned']!=j['input']['nevents']:raise ValueError('Incomplete source')
        f=open_root(R,path)
        if int(f.Get('tCount').GetEntries())!=j['input']['nevents']:raise ValueError('Uncut tCount differs')
        scanned+=d['statistics']['scanned'];selected+=d['statistics']['selected']
        for variant in settings['variants']:
            for family in FAMILIES:
                name=variant['name']+'__'+family;h=f.Get(name)
                if not h:raise ValueError('Missing target histogram '+name)
                for b in range(h.GetNbinsX()+2):
                    if not math.isfinite(h.GetBinContent(b)) or not math.isfinite(h.GetBinError(b)) or h.GetBinContent(b)<0 or h.GetBinError(b)<0:
                        raise ValueError('Invalid target histogram '+name)
                if name not in sums:
                    sums[name]=h.Clone(name);sums[name].SetDirectory(0);sums[name].Reset()
                sums[name].Add(h,j['event_weight'])
        f.Close()
    count=scanned+sum(x['nevents'] for x in settings['skipped_empty_sources'])
    if count!=sum(x['nevents'] for x in settings['inputs']):raise ValueError('Incomplete source coverage')
    f=open_root(R,baseline);checks=[]
    for family in FAMILIES:
        if family.startswith('SearchBins') and settings['min_mht']>300:continue
        h=sums['Baseline__'+family];old=f.Get(family+'_observed')
        first=old.FindBin(settings['min_mht']) if family.startswith('MHT') else 1
        for b in range(first,old.GetNbinsX()+2):
            for a,z in [(h.GetBinContent(b),old.GetBinContent(b)),(h.GetBinError(b),old.GetBinError(b))]:
                if not math.isclose(a,z,rel_tol=1.e-9,abs_tol=1.e-8):
                    raise ValueError(f'Uncut target differs from frozen baseline: {family}, bin {b}: {a} vs {z}')
        checks.append(family)
    for family in FAMILIES:
        h=sums['Baseline__'+family]
        for variant in settings['variants'][1:]:
            alternative=sums[variant['name']+'__'+family]
            for b in range(h.GetNbinsX()+2):
                if alternative.GetBinContent(b)>h.GetBinContent(b)+max(1.e-8,abs(h.GetBinContent(b))*1.e-12):
                    raise ValueError('A target cut increased a yield')
    for family in FAMILIES:
        for tight in settings['variants']:
            for loose in settings['variants']:
                if tight['name']==loose['name']:continue
                if loose['ht_max']>0 and (tight['ht_max']<=0 or tight['ht_max']>loose['ht_max']):continue
                if loose['met_max']>0 and (tight['met_type']!=loose['met_type'] or tight['met_max']<=0 or tight['met_max']>loose['met_max']):continue
                h=sums[tight['name']+'__'+family];other=sums[loose['name']+'__'+family]
                for b in range(h.GetNbinsX()+2):
                    if h.GetBinContent(b)>other.GetBinContent(b)+max(1.e-8,abs(other.GetBinContent(b))*1.e-12):
                        raise ValueError('Tightening a target cut increased a yield')
    output=run/'target_scan.root'
    if output.exists():raise FileExistsError(output)
    out=R.TFile(str(output),'RECREATE');out.cd()
    for h in sums.values():h.Write()
    frozen=[]
    for family in FAMILIES:
        for suffix in ['_prediction','_genSmear_prediction']:
            name=family+suffix;h=f.Get(name);clone=h.Clone(name);clone.SetDirectory(0);clone.Write()
            for b in range(h.GetNbinsX()+2):
                if clone.GetBinContent(b)!=h.GetBinContent(b) or clone.GetBinError(b)!=h.GetBinError(b):
                    raise ValueError('Prediction changed')
            frozen.append(name)
    report=dict(settings,scanned=scanned,source_events_covered=count,selected_targets=selected,
        baseline_target_checks=checks,frozen_histograms=frozen,
        ratio_error_policy='No paired covariance available for new targets; use uncorrelated diagnostic errors')
    write_metadata(R,report);out.Close();f.Close();write_json(str(output)+'.json',report);print(output)

def main():
    p=argparse.ArgumentParser(description='Scan final reconstructed-target cuts with predictions frozen')
    p.add_argument('prediction',nargs='?');p.add_argument('--outdir',default='run3_work/target_cuts')
    p.add_argument('--min-mht',type=float,default=250.);p.add_argument('--condor',action='store_true')
    p.add_argument('--merge',action='store_true');p.add_argument('--nfiles',type=int,default=0)
    p.add_argument('--payload',help=argparse.SUPPRESS)
    a=p.parse_args()
    if a.payload:worker(a.payload);return
    if a.merge:merge(a.outdir);return
    if not a.prediction:p.error('Give the completed all-HT prediction ROOT file')
    if a.min_mht not in MHT_EDGES or a.min_mht<250:p.error('--min-mht must be a histogram edge >=250 GeV')
    if a.nfiles<0:p.error('--nfiles must be nonnegative')
    run=prepare(a.prediction,a.outdir,a.min_mht,a.condor,a.nfiles)
    if not a.condor and a.nfiles==0:merge(run)

if __name__=='__main__':main()
