#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
from common import config,root,open_root,metadata,write_metadata,write_json

def merge(R,paths,output,record,raw=False):
    if output.exists():raise FileExistsError(output)
    combined={};count=0
    for path in paths:
        f=open_root(R,path);count+=int(f.Get('tCount').GetEntries())
        for key in f.GetListOfKeys():
            name=key.GetName();obj=f.Get(name)
            if not obj.InheritsFrom('TH1') or name.endswith('_ratio'):continue
            if name not in combined:combined[name]=obj.Clone(name);combined[name].SetDirectory(0)
            elif not raw or name not in ['hPtTemplate','hEtaTemplate','hHtTemplate']:combined[name].Add(obj)
        f.Close()
    out=R.TFile(str(output),'RECREATE');out.cd()
    for h in combined.values():h.Write()
    if not raw:
        for name,prediction in combined.items():
            if not name.endswith('_prediction') or name[:-len('_prediction')]+'_cross_covariance' not in combined:continue
            prefix=name[:-len('_prediction')];observed=combined[prefix+'_observed'];cov=combined[prefix+'_cross_covariance']
            ratio=prediction.Clone(prefix+'_ratio');ratio.Reset()
            for i in range(1,ratio.GetNbinsX()+1):
                a=observed.GetBinContent(i)
                if not a:continue
                r=prediction.GetBinContent(i)/a
                variance=prediction.GetBinError(i)**2+r*r*observed.GetBinError(i)**2-2*r*cov.GetBinContent(i)
                ratio.SetBinContent(i,r);ratio.SetBinError(i,math.sqrt(max(0.,variance))/abs(a))
            ratio.Write()
    counter=R.TTree('tCount','Uncut encountered source events');counter.SetEntries(count);counter.Write()
    if not raw and record.get('trees_written',True):
        for name in ['RandS','seeds']:
            chain=R.TChain(name)
            for path in paths:chain.Add(str(path))
            if chain.GetEntries():
                out.cd();tree=chain.CloneTree(-1,'fast');tree.Write(name)
    write_metadata(R,record);out.Close();write_json(str(output)+'.json',record)

def merge_files(paths,output,expected=None):
    R=root(True);records=[];seen=set();raw=None
    for path in paths:
        f=open_root(R,path);r=metadata(R,f);is_raw=r.get('format_version')==1
        if raw is not None and raw!=is_raw:raise ValueError('Mixed response and prediction files')
        raw=is_raw
        if r['config']!=config():raise ValueError('Configuration mismatch')
        count=f.Get('tCount')
        if not count or count.GetListOfBranches().GetEntries():raise ValueError('Missing branchless tCount')
        files=r['files'] if raw else [dict(r['input'],statistics=r['statistics'])]
        if int(count.GetEntries())!=sum(x['statistics']['scanned'] for x in files):raise ValueError('Uncut count mismatch')
        for file in files:
            if file['lfn'] in seen:raise ValueError('Duplicate input file')
            seen.add(file['lfn'])
        if records and (r['split']!=records[0]['split'] or (not raw and (r['normalization']!=records[0]['normalization'] or r['fixed_objects']!=records[0]['fixed_objects'] or r['template_sha256']!=records[0]['template_sha256'] or r.get('trees_written',True)!=records[0].get('trees_written',True)))):
            raise ValueError('Incompatible prediction shards')
        records.append(r);f.Close()
    if not records:raise ValueError('No ROOT inputs')
    if expected is not None and seen!=expected:raise ValueError('Returned files differ from submitted inputs')
    record=dict(records[0])
    if raw:record['files']=[f for r in records for f in r['files']]
    else:
        stats={key:sum(r['statistics'][key] for r in records) for key,value in record['statistics'].items() if isinstance(value,(int,float))}
        clean=records[0]['statistics']['cleaning']
        stats['cleaning']={key:sum(r['statistics']['cleaning'][key] for r in records) for key in clean if key!='flags'}
        stats['cleaning']['flags']=[dict(name=f['name'],**{key:sum(r['statistics']['cleaning']['flags'][i][key] for r in records) for key in ['failed_independently','passed_cumulative']}) for i,f in enumerate(clean['flags'])]
        record.update(statistics=stats,source_files=len(records),inputs=[r['input'] for r in records]);record.pop('input',None)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    merge(R,paths,output,record,raw)
    return str(output)

def main():
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--output',default=None);a=p.parse_args()
    folder=Path(a.folder).resolve();output=Path(a.output or folder/'merged.root').resolve();expected=None
    if (folder/'jobs.json').exists():
        jobs=json.loads((folder/'jobs.json').read_text());stage=json.loads((folder/'settings.json').read_text())['stage']
        paths=[str(Path(j['job'])/(stage+'.root')) for j in jobs]
        expected={j['source']['lfn'] for j in jobs}
        if any(not Path(x).is_file() for x in paths):raise ValueError('Wait for all Condor jobs to finish')
    else:paths=sorted(str(x) for x in folder.glob('*.root') if x.resolve()!=output)
    print(merge_files(paths,output,expected))

if __name__=='__main__':main()
