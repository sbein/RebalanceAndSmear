#!/usr/bin/env python3
import argparse,hashlib,json,shutil
from pathlib import Path
from common import write_json,root,open_root,metadata,write_metadata
from ResponseMaker import make_responses
from SkimRandS import make_skims

def main():
    p=argparse.ArgumentParser();p.add_argument('--payload',required=True);a=p.parse_args()
    payload=json.loads(Path(a.payload).read_text());settings=payload['settings'];source=dict(payload['source'])
    if Path('input.root').exists():source['url']=str(Path('input.root').resolve())
    sample=dict(payload['sample'],files=[source]);inputs=dict(samples=[sample])
    if settings['stage']=='response':
        make_responses(inputs,'raw',settings['max_events'],settings['split'])
        result=Path('raw')/('raw_HT'+sample['name']+'.root')
    else:
        seed=(int(hashlib.sha256(source['lfn'].encode()).hexdigest()[:8],16)^12345) or 1
        result=Path(make_skims(inputs,'templates.root','skims',settings['max_events'],
            settings['nsmear'],settings['quickrun'],settings['fixed_photons'],seed,
            settings.get('histograms_only',False))[0])
    shutil.copy2(result,'result.root')
    R=root();f=open_root(R,'result.root');r=metadata(R,f);f.Close()
    r['source_archive_sha256']=settings['source_archive_sha256']
    f=R.TFile('result.root','UPDATE');f.cd();write_metadata(R,r);f.Close();write_json('result.root.json',r)

if __name__=='__main__':main()
