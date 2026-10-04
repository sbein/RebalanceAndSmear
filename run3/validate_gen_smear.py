#!/usr/bin/env python3
"""Test RNG independence, strict generator acceptance, paired errors and dphi partitions."""
import argparse,math
from common import root,open_root,metadata,write_json
OBSERVABLES=['MHT','HT','NJets','BTags','DPhi1','MinDPhi']
def compare_existing(a,b):
    checked=0
    for key in a.GetListOfKeys():
        name=key.GetName();x=a.Get(name)
        if '_genSmear' in name or not x.InheritsFrom('TH1'):continue
        y=b.Get(name);assert y and x.GetNbinsX()==y.GetNbinsX(),name
        for i in range(x.GetNbinsX()+2):
            assert x.GetBinContent(i)==y.GetBinContent(i),(name,i,'content')
            assert x.GetBinError(i)==y.GetBinError(i),(name,i,'error')
        checked+=1
    return checked

def check_file(R,f):
    meta=metadata(R,f);stats=meta['statistics'];t=f.Get('seeds')
    data=R.RDataFrame(t).AsNumpy(['fit','accepted','GenMHT','genAccepted'])
    expected=(data['GenMHT']<meta['gen_smearing']['seed_mht_max_GeV'])
    assert (expected==data['genAccepted']).all()
    assert stats['gen_seeds']==int(expected.sum())
    assert stats['gen_seeds']+stats['gen_rejected_mht']==stats['selected']
    assert stats['gen_smears']==stats['gen_seeds']*meta['gen_smearing']['smears_per_seed']
    partition_checks=0;covariance_checks=0
    for observable in OBSERVABLES:
        for method in ['_observed','_prediction','_genSmear_prediction']:
            inclusive=f.Get(observable+'_Inclusive'+method);high=f.Get(observable+'_HighMinDPhi'+method);low=f.Get(observable+'_LowMinDPhi'+method)
            for i in range(inclusive.GetNbinsX()+2):
                assert math.isclose(inclusive.GetBinContent(i),high.GetBinContent(i)+low.GetBinContent(i),rel_tol=2e-12,abs_tol=1e-12),(observable,method,i)
                partition_checks+=1
    for key in f.GetListOfKeys():
        name=key.GetName()
        if not name.endswith('_genSmear_prediction'):continue
        prefix=name[:-len('_prediction')];p=f.Get(name);o=f.Get(prefix+'_observed');c=f.Get(prefix+'_cross_covariance');r=f.Get(prefix+'_ratio')
        counterpart=f.Get(prefix[:-len('_genSmear')]+'_observed')
        if counterpart:
            for i in range(o.GetNbinsX()+2):
                assert o.GetBinContent(i)==counterpart.GetBinContent(i),(name,'observed mismatch',i)
                assert o.GetBinError(i)==counterpart.GetBinError(i)
        for i in range(1,o.GetNbinsX()+1):
            if o.GetBinContent(i)==0:continue
            value=p.GetBinContent(i)/o.GetBinContent(i)
            variance=p.GetBinError(i)**2+value**2*o.GetBinError(i)**2-2*value*c.GetBinContent(i)
            error=math.sqrt(max(0,variance))/abs(o.GetBinContent(i))
            assert math.isclose(r.GetBinContent(i),value,rel_tol=2e-12,abs_tol=1e-12)
            assert math.isclose(r.GetBinError(i),error,rel_tol=2e-12,abs_tol=1e-12),(name,i)
            covariance_checks+=1
    return dict(partition_bin_checks=partition_checks,gensmear_covariance_checks=covariance_checks,
        gen_seed_acceptance_strict=True,generator_seeds_rejected_by_rebalance=int((expected & (data['accepted']==0)).sum()),
        generator_seeds_with_failed_rebalance=int((expected & (data['fit']==0)).sum()))

def main():
    p=argparse.ArgumentParser();p.add_argument('--enabled',required=True);p.add_argument('--disabled',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();R=root();a=open_root(R,args.enabled);b=open_root(R,args.disabled)
    report=check_file(R,a);report['unchanged_rands_histograms']=compare_existing(a,b);report['rands_rng_independent']=True
    write_json(args.output,report);print(report);a.Close();b.Close()
if __name__=='__main__':main()
