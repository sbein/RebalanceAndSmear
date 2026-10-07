import glob,json,re,subprocess
from pathlib import Path
from common import BASE,root,open_root

LUMINOSITY_PB=124000.0
MAX_EVENTS_QUICK=100000

def das(query):
    r=subprocess.run(['dasgoclient','-query',query,'-json','-limit=0'],check=True,capture_output=True,text=True,timeout=240)
    return json.loads(r.stdout)

def resolve(fnamekeyword='QCD_HT1200',era='2024',nfiles=1):
    if era!='2024':raise ValueError('Only 2024 is configured')
    if nfiles<0:raise ValueError('nfiles=0 means all files')
    spec=json.loads((BASE/'qcd_2024.json').read_text())['samples'][0]
    aliases={'QCD_HT1200','HT1200','QCD_HT1200to1500',spec['dataset']}
    files=[];datasets=[spec['dataset']]
    if fnamekeyword in aliases:
        _,primary,processing,tier=spec['dataset'].split('/')
        datasets=sorted({d['name'] for row in das(f'dataset dataset=/{primary}*/{processing.split("-")[0]}*/{tier}')
            for d in row.get('dataset',[]) if re.sub(r'_ext[0-9]+(?=[/-])','',d.get('name',''))==spec['dataset']})
        if spec['dataset'] not in datasets:raise ValueError('Missing original dataset')
        for dataset in datasets:
            for row in das('file dataset='+dataset):
                for f in row.get('file',[]):
                    if not f.get('name','').endswith('.root') or f.get('is_file_valid',1)!=1:continue
                    files.append(dict(lfn=f['name'],url='root://cms-xrd-global.cern.ch/'+f['name'],dataset=dataset,nevents=int(f['nevents'])))
        files.sort(key=lambda f:(-f['nevents'],f['lfn']))
    else:
        names=[fnamekeyword] if fnamekeyword.startswith(('root://','/store/')) else sorted(glob.glob(fnamekeyword))
        if fnamekeyword.endswith('.txt') and Path(fnamekeyword).is_file():
            names=[line.strip() for line in Path(fnamekeyword).read_text().splitlines() if line.strip() and not line.startswith('#')]
        R=root()
        for name in names:
            url='root://cms-xrd-global.cern.ch/'+name if name.startswith('/store/') else name
            f=open_root(R,url);tree=f.Get('Events')
            if not tree:raise ValueError('Missing NanoAOD Events: '+url)
            files.append(dict(lfn=name,url=url,dataset=spec['dataset'],nevents=int(tree.GetEntries())));f.Close()
    if not files or len({f['lfn'] for f in files})!=len(files):raise ValueError('Empty or duplicated input files')
    if any(f['nevents']<=0 for f in files):raise ValueError('Missing uncut source counts')
    chosen=files[:nfiles] if nfiles else files
    sample=dict(spec,datasets=datasets,normalization_group=spec['name'],files=chosen,
        inventory_complete=len(chosen)==len(files),source_lfns=[f['lfn'] for f in files],
        expected_uncut_events=sum(f['nevents'] for f in files))
    return dict(samples=[sample],source_files=len(chosen),inventory_complete=sample['inventory_complete'],
        expected_uncut_events=sample['expected_uncut_events'])

def production_normalization(records):
    groups={};expected={}
    for r in records:
        s=r['sample'];name=s['normalization_group']
        if 'inventory_complete' not in s:
            if 'available_files' not in s or 'expected_uncut_events' not in s:return None
            s=dict(s,inventory_complete=len(r['files'])==s['available_files'],
                source_lfns=[f['lfn'] for f in r['files']])
        if r['split']!=2 or not s['inventory_complete']:return None
        signature=(s['cross_section_pb'],s['expected_uncut_events'],tuple(sorted(s['source_lfns'])))
        if name in expected and expected[name]!=signature:raise ValueError('Conflicting dataset inventories')
        expected[name]=signature
        g=groups.setdefault(name,dict(cross_section_pb=s['cross_section_pb'],datasets=s['datasets'],ntot_uncut=0,source_lfns=[]))
        for f in r['files']:
            if f['lfn'] in g['source_lfns']:raise ValueError('Duplicate source file')
            if f['statistics']['scanned']!=f['nevents']:return None
            g['ntot_uncut']+=f['statistics']['scanned'];g['source_lfns'].append(f['lfn'])
    for name,g in groups.items():
        if g['ntot_uncut']!=expected[name][1] or set(g['source_lfns'])!=set(expected[name][2]):return None
        g['source_lfns'].sort()
    return dict(complete=True,groups=groups,luminosity_pb_inverse=LUMINOSITY_PB,generator_weight_policy='ignore')
