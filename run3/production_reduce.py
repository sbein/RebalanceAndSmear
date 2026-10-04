#!/usr/bin/env python3
"""Require every input once, derive ntot from tCount, and merge predictions."""
import argparse,json,math,subprocess
from pathlib import Path
from common import BASE,root,open_root,metadata,write_metadata,write_json
from production_worker import validate

def complete_inputs(run,stage):
    manifest=json.loads((run/'manifest.json').read_text());jobs=json.loads((run/'jobs.json').read_text());groups={};records=[];seen=set()
    for item in jobs:
        path=Path(item['job'])/(stage+'.root');source=item['source'];group=item['group']
        if source['lfn'] in seen:raise ValueError('Repeated source file')
        seen.add(source['lfn']);record=validate(path,source,stage);records.append((path,group,record))
        spec=next(s for s in manifest['samples'] if s['normalization_group']==group)
        total=groups.setdefault(group,dict(cross_section_pb=spec['cross_section_pb'],datasets=spec['datasets'],ntot_uncut=0,source_lfns=[]))
        R=root();f=open_root(R,path);total['ntot_uncut']+=int(f.Get('tCount').GetEntries());f.Close();total['source_lfns'].append(source['lfn'])
    if len(seen)!=manifest['source_files']:raise ValueError('Missing inputs')
    for spec in manifest['samples']:
        if groups[spec['normalization_group']]['ntot_uncut']!=spec['expected_uncut_events']:raise ValueError('Uncut counter disagrees with frozen DAS inventory')
    return groups,records

def merged_histograms(R,paths,output,record):
    if output.exists():raise FileExistsError(output)
    combined={};count=0
    for path in paths:
        f=open_root(R,path);count+=int(f.Get('tCount').GetEntries())
        for key in f.GetListOfKeys():
            name=key.GetName();obj=f.Get(name)
            if not obj.InheritsFrom('TH1') or name.endswith('_ratio'):continue
            if name in combined:combined[name].Add(obj)
            else:combined[name]=obj.Clone(name);combined[name].SetDirectory(0)
        f.Close()
    out=R.TFile(str(output),'RECREATE');out.cd()
    for name,h in combined.items():h.Write()
    for name,prediction in combined.items():
        if not name.endswith('_prediction'):continue
        prefix=name[:-len('_prediction')];observed=combined[prefix+'_observed'];cov=combined.get(prefix+'_cross_covariance')
        ratio=prediction.Clone(prefix+'_ratio');ratio.Reset();ratio.SetTitle('Prediction / reco;'+observed.GetXaxis().GetTitle()+';ratio')
        for i in range(1,ratio.GetNbinsX()+1):
            a=observed.GetBinContent(i);b=prediction.GetBinContent(i)
            if not a:continue
            r=b/a;variance=prediction.GetBinError(i)**2+r*r*observed.GetBinError(i)**2-2*r*(cov.GetBinContent(i) if cov else 0.)
            ratio.SetBinContent(i,r);ratio.SetBinError(i,math.sqrt(max(0.,variance))/abs(a))
        ratio.Write()
    counter=R.TTree('tCount','Uncut input events; use group-specific ntot from metadata for normalization');counter.SetEntries(count);counter.Write()
    write_metadata(R,record);out.Close();write_json(str(output)+'.json',record)

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--stage',choices=['templates','predictions'],required=True);args=p.parse_args()
    run=Path(args.run).resolve();settings=json.loads((run/'settings.json').read_text())
    if args.stage=='templates':
        groups,records=complete_inputs(run,'raw')
        norm=dict(complete=True,groups=groups,luminosity_pb_inverse=settings['luminosity_pb_inverse'],generator_weight_policy='ignore',
            denominator='Sum of dynamically encountered uncut tCount entries in all original and extension files; no selection/split/genWeight denominator')
        write_json(run/'normalization.json',norm)
        if not (run/'templates_full.root').exists():
            subprocess.run(['python3',str(BASE/'articulate_splines.py'),'--inputs']+[str(p) for p,_,_ in records]+['--output',str(run/'templates_full.root'),'--allow-sparse'],check=True)
        subprocess.run(['python3',str(BASE/'audit_splines.py'),'--templates',str(run/'templates_full.root'),'--out',str(run/'spline_audit')],check=True)
        write_json(run/'templates_complete.json',dict(complete=True,files=len(records),uncut_events=sum(g['ntot_uncut'] for g in groups.values()),settings=settings,
            strict_coverage_report=str(run/'templates_full.root.coverage.json'),remaining_storage_limitations='GenJet>10 and Jet>15 cannot be remedied by additional statistics'))
    else:
        groups,records=complete_inputs(run,'closure');norm=json.loads((run/'normalization.json').read_text())
        if groups!=norm['groups']:raise ValueError('Closure event totals differ from template counters')
        for _,group,m in records:
            expected=groups[group]['cross_section_pb']*settings['luminosity_pb_inverse']/groups[group]['ntot_uncut']
            n=m['normalization']
            if n['event_weight']!=expected or n['luminosity_pb_inverse']!=settings['luminosity_pb_inverse'] or n['ntot_uncut']!=groups[group]['ntot_uncut']:raise ValueError('Shard normalization differs from frozen group settings')
            if m['smears_per_seed']!=settings['nsmear'] or m['closure_selection']['rebalanced_mht_max_GeV']!=settings['rebalance_mht_max_GeV']:raise ValueError('Shard smear count or rebalance cut differs from production settings')
        outdir=run/'predictions';outdir.mkdir(exist_ok=True);R=root();last=records[-1][2]
        for group in list(groups)+['allHT']:
            selected=[x for x in records if group=='allHT' or x[1]==group]
            stats={}
            for _,_,m in selected:
                for k,v in m['statistics'].items():
                    if isinstance(v,(int,float)):stats[k]=stats.get(k,0)+v
            cleaning=dict(after_filters=0,after_jet_id=0,after_jet_veto=0,flags=[])
            flags=selected[0][2]['statistics']['cleaning']['flags']
            for key in ['after_filters','after_jet_id','after_jet_veto']:cleaning[key]=sum(m['statistics']['cleaning'][key] for _,_,m in selected)
            for i,flag in enumerate(flags):cleaning['flags'].append(dict(name=flag['name'],failed_independently=sum(m['statistics']['cleaning']['flags'][i]['failed_independently'] for _,_,m in selected),passed_cumulative=sum(m['statistics']['cleaning']['flags'][i]['passed_cumulative'] for _,_,m in selected)))
            stats['cleaning']=cleaning
            record=dict(selected[0][2],statistics=stats,production_normalization=norm,settings=settings,source_files=len(selected),
                validation_scope='Full-statistics MC production with training overlap; not independent closure',source_commit=settings['source_commit'])
            record.pop('input',None)
            record['sample']=dict(name=group,normalization_groups=list(groups) if group=='allHT' else [group])
            record['normalization']=dict(mode='full-dataset uncut count',generator_weight_policy='ignore',luminosity_pb_inverse=settings['luminosity_pb_inverse'],
                group_weights={g:groups[g]['cross_section_pb']*settings['luminosity_pb_inverse']/groups[g]['ntot_uncut'] for g in (groups if group=='allHT' else [group])},nsmear=settings['nsmear'],template_overlap_allowed=True)
            target=outdir/('prediction_'+group+'.root')
            if not target.exists():merged_histograms(R,[p for p,_,_ in selected],target,record)
        write_json(run/'production_complete.json',dict(complete=True,files=len(records),uncut_events=sum(g['ntot_uncut'] for g in groups.values()),settings=settings))
        for region,folder in [('Inclusive','inclusive'),('HighMinDPhi','high-min-dphi'),('LowMinDPhi','low-min-dphi'),('Legacy','legacy-jet-regions')]:
            subprocess.run(['python3',str(BASE/'plot_three_method_closure.py'),str(outdir/'prediction_allHT.root'),'--outdir',str(run/'plots'/folder),'--region',region],check=True)
if __name__=='__main__':main()
