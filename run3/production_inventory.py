#!/usr/bin/env python3
"""Freeze complete DAS inventories; combine true extensions, not reprocessings."""
import argparse,json,re,subprocess
from pathlib import Path
from common import BASE,write_json

def extension_base(dataset):
    return re.sub(r'_ext[0-9]+(?=[/-])','',dataset)

def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',default=str(BASE/'qcd_2024.json'))
    p.add_argument('--datasets-query',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();target=Path(args.output)
    if target.exists():raise FileExistsError(target)
    source=json.loads(Path(args.samples).read_text());found=json.loads(Path(args.datasets_query).read_text())
    available={x['name'] for row in found for x in row.get('dataset',[]) if x.get('name')}
    samples=[];seen=set()
    for sample in source['samples']:
        datasets=sorted(d for d in available if extension_base(d)==sample['dataset'])
        if sample['dataset'] not in datasets:raise ValueError('Missing exact published dataset: '+sample['dataset'])
        files=[]
        for dataset in datasets:
            result=subprocess.run(['dasgoclient','-query','file dataset='+dataset,'-json','-limit=0'],check=True,capture_output=True,text=True,timeout=240)
            data=json.loads(result.stdout)
            write_json(target.parent/'das'/(sample['name']+'_'+str(datasets.index(dataset))+'.json'),data)
            rows={x['name']:x for row in data for x in row.get('file',[]) if x.get('name','').endswith('.root') and x.get('is_file_valid',1)==1}
            if not rows:raise ValueError('No valid files: '+dataset)
            for name,row in sorted(rows.items()):
                if name in seen:raise ValueError('Duplicate source LFN: '+name)
                seen.add(name)
                if int(row.get('nevents',0))<=0:raise ValueError('Missing uncut DAS event count: '+name)
                files.append(dict(lfn=name,url='root://cms-xrd-global.cern.ch/'+name,dataset=dataset,nevents=int(row['nevents']),size=row.get('size'),adler32=row.get('adler32')))
        samples.append(dict(sample,datasets=datasets,normalization_group=sample['name'],files=files,
                            available_files=len(files),expected_uncut_events=sum(f['nevents'] for f in files)))
        print(sample['name'],len(datasets),'datasets,',len(files),'files,',samples[-1]['expected_uncut_events'],'uncut events',flush=True)
    write_json(target,dict(source,samples=samples,inventory_complete=True,source_files=len(seen),
        expected_uncut_events=sum(s['expected_uncut_events'] for s in samples),generator_weight_policy='ignore',
        extension_policy='Exact processing version and generator sample; combine _extN only. Exclude JMENano/NoPU/reprocessing duplicates.'))
if __name__=='__main__':main()
