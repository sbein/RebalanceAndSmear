#!/usr/bin/env python3
"""End-to-end unit-weight, extension-denominator, tCount and merge regression."""
import argparse,json,shutil,subprocess
from pathlib import Path
from common import BASE,config,root,open_root,metadata,write_json
from production_reduce import complete_inputs,merged_histograms

def main():
    p=argparse.ArgumentParser();p.add_argument('--nano',required=True);p.add_argument('--templates',required=True);p.add_argument('--directory',required=True);args=p.parse_args()
    run=Path(args.directory).resolve()
    if run.exists():raise FileExistsError(run)
    run.mkdir();R=root();samples=[];jobs=[];files=[]
    for i,(begin,end) in enumerate([(0,200),(200,1000)]):
        nano=run/f'source{i}.root'
        R.RDataFrame('Events',args.nano).Range(begin,end).Redefine('genWeight','float(event % 2 ? -7.0 : 11.0)').Snapshot('Events',str(nano))
        source=dict(lfn=str(nano),url=str(nano),nevents=end-begin,dataset='original' if i==0 else 'extension1')
        files.append(source);job=run/'jobs'/f'{i:05d}';job.mkdir(parents=True);jobs.append(dict(job=str(job),group='test',source=source))
    sample=dict(name='test',normalization_group='test',dataset='original',datasets=['original','extension1'],cross_section_pb=10.,expected_uncut_events=1000,files=files)
    manifest=dict(samples=[sample],source_files=2,inventory_complete=True,expected_uncut_events=1000)
    write_json(run/'manifest.json',manifest);write_json(run/'jobs.json',jobs)
    write_json(run/'settings.json',dict(luminosity_pb_inverse=2.,nsmear=1,rebalance_mht_max_GeV=90,source_commit='validation'))
    shutil.copy2(args.templates,run/'templates_full.root')
    for item in jobs:
        job=Path(item['job']);write_json(job/'manifest.json',dict(manifest,samples=[dict(sample,files=[item['source']])]))
        subprocess.run(['python3',str(BASE/'production_worker.py'),'--run',str(run),'--job',str(job),'--stage','raw'],check=True)
    groups,records=complete_inputs(run,'raw')
    assert groups['test']['ntot_uncut']==1000
    chain=R.TChain('tCount')
    for path,_,m in records:
        chain.Add(str(path));assert m['files'][0]['statistics']['sumw']==m['files'][0]['statistics']['scanned']
    assert chain.GetEntries()==1000
    subprocess.run(['hadd','-f',str(run/'hadd_counts.root')]+[str(p) for p,_,_ in records],check=True)
    f=open_root(R,run/'hadd_counts.root');assert f.Get('tCount').GetEntries()==1000;f.Close()
    write_json(run/'normalization.json',dict(complete=True,groups=groups,luminosity_pb_inverse=2.))
    for item in jobs:subprocess.run(['python3',str(BASE/'production_worker.py'),'--run',str(run),'--job',item['job'],'--stage','closure'],check=True)
    closure_groups,closed=complete_inputs(run,'closure');assert closure_groups==groups
    for path,_,m in closed:
        assert m['normalization']['event_weight']==.02 and m['normalization']['smear_weight']==.02
        assert m['statistics']['sumw']==m['statistics']['scanned']
        f=open_root(R,path)
        for prefix in ['MHT_Inclusive','MHT_HighMinDPhi','MHT_LowMinDPhi']:
            h=f.Get(prefix+'_observed')
            for i in range(h.GetNbinsX()+2):assert abs(h.GetBinContent(i)/.02-round(h.GetBinContent(i)/.02))<1.e-9
        weights=R.RDataFrame(f.Get('seeds')).AsNumpy(['genWeight'])['genWeight'];assert (weights==1.).all();f.Close()
    merged=run/'merged.root';merged_histograms(R,[p for p,_,_ in closed],merged,dict(validation=True))
    f=open_root(R,merged);assert f.Get('tCount').GetEntries()==1000
    # Sum independent file contributions, then recompute ratios/covariance rather than sum ratios.
    checks=0
    for name in ['MHT_Inclusive_observed','MHT_Inclusive_prediction','MHT_Inclusive_cross_covariance','MHT_Inclusive_genSmear_prediction']:
        h=f.Get(name);inputs=[open_root(R,p) for p,_,_ in closed]
        for i in range(h.GetNbinsX()+2):
            assert abs(h.GetBinContent(i)-sum(x.Get(name).GetBinContent(i) for x in inputs))<1.e-12
            assert abs(h.GetBinError(i)**2-sum(x.Get(name).GetBinError(i)**2 for x in inputs))<1.e-12;checks+=1
        for x in inputs:x.Close()
    f.Close();report=dict(unit_weights_ignore_signed_generator_weights=True,extension_combined_ntot=1000,event_weight=.02,smear_weight=.02,nsmear=1,
        uncut_counts_before_selection=True,branchless_tCount_chain_and_hadd=True,merged_bin_checks=checks,per_file_counters=[200,800])
    write_json(run/'validation.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
