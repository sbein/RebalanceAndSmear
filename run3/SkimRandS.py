#!/usr/bin/env python3
#Welcome to the industrial age of Sam's rebalance and smear code. You're going to have a lot of fun!
"""Rebalance and smear NanoAOD events; write skims and closure histograms."""
import argparse
import json
import hashlib
from inputs import resolve,production_normalization,LUMINOSITY_PB,MAX_EVENTS_QUICK
from pathlib import Path
from common import *

def make_skims(inputs,templates,outdir,maxevents=-1,smears=1,quickrun=False,fixed_photons=False,seed=12345,histograms_only=False):
    outputs=[];targets=[]
    cfg=config();ROOT=root(True);configure_cleaning(ROOT,cfg)
    f=open_root(ROOT,templates);record=metadata(ROOT,f);require_compatible(record,cfg,analysis=True)
    template_sha=hashlib.sha256(Path(templates).read_bytes()).hexdigest()
    production_norm=None if quickrun else (
        record.get('production_normalization') or production_normalization(record['training_records']))
    if not quickrun and not production_norm:
        raise ValueError('Complete response counts are required; use --quickrun for a held-out pilot')
    split=1 if quickrun else 2
    ROOT.GleanTemplatesFromFile(f)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    for sample in inputs['samples']:
      for file in sample['files']:
        name=hashlib.sha256(file['lfn'].encode()).hexdigest()[:12]
        output=str(outdir/('RandS_HT'+sample['name']+'_'+name+'.root'))
        if Path(output).exists():raise FileExistsError(output)
        for training in record['training_records']:
            if quickrun and file['lfn'] in {x['lfn'] for x in training['files']} and training['split']!=0:
                raise ValueError('Pilot validation overlaps template training')
        stats=ROOT.Run3Closure(file['url'],cfg['btag_branch'],cfg['btag_cut'],
            vector(ROOT,'string',cfg['analysis_cleaning']['filters']),output,maxevents,smears,cfg['rebalance_mht_max'],
            seed,True,split,2000.,True,150.,smears,-1,True,fixed_photons,not histograms_only)
        values=summary(stats,['scanned','validation','selected','fitted','accepted','smears','sumw','seconds',
            'rejected_rebalanced_mht','nonfinite_rebalanced','rejected_smeared_mht','nonfinite_smears',
            'gen_seeds','gen_rejected_mht','gen_smears','gen_nonfinite','gen_above_2000'])
        values['cleaning']=cleaning_summary(stats,cfg,analysis=True)
        if values['sumw']<=0:raise ValueError('No usable uncut input events')
        targets.append((output,sample,file,values));outputs.append(output)
    for output,sample,file,values in targets:
        if production_norm:
            if maxevents!=-1:raise ValueError('Production needs complete input scans')
            group=production_norm['groups'][sample['normalization_group']]
            if group['cross_section_pb']!=sample['cross_section_pb'] or file['lfn'] not in group['source_lfns']:
                raise ValueError('Prediction input differs from completed response counts')
            if values['scanned']!=file['nevents']:raise ValueError('Incomplete prediction input scan')
            ntot=group['ntot_uncut'];lumi=production_norm['luminosity_pb_inverse']
        else:
            ntot=sum(v['sumw'] for _,s,_,v in targets if s['normalization_group']==sample['normalization_group'])
            lumi=LUMINOSITY_PB
        norm=sample['cross_section_pb']*lumi/ntot
        result=dict(config=cfg,template_file=str(Path(templates).resolve()),input=file,sample=sample,
                    statistics=values,smears_per_seed=smears,random_seed=seed,
                    cached_splines=True,split=split,
                    bounded_nonnegative_pdf=bool(ROOT.Run3BoundedPdf),
                    sparse_pilot=record["sparse_pilot"],borrowed_template_count=len(record["borrowed"]),
                    statistical_errors="Seed-cluster second moments; MHT ratio includes paired observed/prediction covariance",
                    baseline="HT>300, NJets>=2, applied independently to observed and every smeared event")
        result["normalization"]=dict(mode="full-dataset uncut count" if production_norm else "processed split sum of weights",generator_weight_policy="ignore",
            luminosity_pb_inverse=lumi,ntot_uncut=ntot,
            event_weight=norm,smear_weight=norm/smears,template_overlap_allowed=not quickrun)
        result["closure_selection"]=dict(rebalanced_mht_max_GeV=cfg["rebalance_mht_max"],smeared_mht_max_GeV=2000.,
            random_draws="per event key",
            jet_only_regions="Legacy central-jet delta-phi, MHT<HT, Andrews HT-ratio filter, 174-bin mapping and 250-300 sidebands; no lepton/photon/track veto")
        result["diagnostic_views"]=dict(baseline="HT>300, NJets>=2; no MHT or HT-ratio cut",
            names=["Inclusive","High Min Dphi","Low Min Dphi"],
            dphi_definition="High: all available first four central jets meet 0.5/0.5/0.3/0.3; Low: logical complement",
            min_dphi_cut=None,partition="Inclusive = High Min Dphi + Low Min Dphi")
        result["gen_smearing"]=dict(enabled=True,seed_mht_max_GeV=150.,
            smears_per_seed=smears,requires_rebalance_acceptance=False,individual_smear_mht_max_GeV=None,
            random_draws="Separate deterministic event-key stream",tags="Current Nano genJetIdx/DR<0.4 reco-tag mapping, identical to template training")
        result['stage']='rands';result['production_normalization']=production_norm
        result['template_sha256']=template_sha
        result['template_training_config']=record['config']
        result['analysis_cleaning']=cfg['analysis_cleaning']
        result['trees_written']=not histograms_only
        result['fixed_objects']='photons' if fixed_photons else 'none'
        result['photon_selection']=dict(pt_min=20,eta_max=2.4,cutBased_min=2,jet_match_inner=.4,jet_match_outer=.5,gen_overlap=.1) if fixed_photons else None
        out=ROOT.TFile(output,"UPDATE");out.cd()
        for key in list(out.GetListOfKeys()):
            name=key.GetName();h=out.Get(name)
            if h.InheritsFrom("TH1") and not name.endswith("_ratio"):
                h.Scale(norm*norm if name.endswith("_cross_covariance") else norm)
                h.Write(name,ROOT.TObject.kOverwrite)
        if not histograms_only:ROOT.Run3WeightSkim(out.Get('RandS'),norm)
        write_metadata(ROOT,result);out.Close()
        write_json(output+".json",result)
        print(json.dumps(result["statistics"],indent=2))
        print("Wrote",output)
    f.Close();return outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--fnamekeyword',default='QCD_HT1200')
    p.add_argument('--era',default='2024')
    p.add_argument('--forcetemplates',default='run3_work/templates.root')
    p.add_argument('--outdir',default='run3_work/skims')
    p.add_argument('--nfiles',type=int,default=1,help='0: all files')
    p.add_argument('--maxevents',type=int,default=-1)
    p.add_argument('--smears',type=int,default=1)
    p.add_argument('--quickrun',action='store_true')
    p.add_argument('--fixed-photons',action='store_true')
    p.add_argument('--histograms-only',action='store_true')
    a=p.parse_args()
    if a.smears<1 or a.maxevents==0 or a.maxevents<-1:p.error('Invalid event/smear count')
    make_skims(resolve(a.fnamekeyword,a.era,a.nfiles),a.forcetemplates,a.outdir,
        MAX_EVENTS_QUICK if a.quickrun and a.maxevents==-1 else a.maxevents,a.smears,a.quickrun,a.fixed_photons,
        histograms_only=a.histograms_only)

if __name__=='__main__':main()
