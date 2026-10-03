#!/usr/bin/env python3
"""Compare new jet diagnostics to independent legacy definitions and guard boundaries."""
import argparse
import ast
import math
import re
import subprocess
from common import BASE,root,vector,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='run3_work/legacy_review20261004/legacy_validation.json')
    args=p.parse_args();R=root(True)
    changed=subprocess.check_output(['git','diff','fd9821f','--','src','tools','bashscripts','usefulthings'],cwd=BASE.parent,text=True)
    assert not changed,'Original legacy files changed'
    source=(BASE.parent/'tools/utils.py').read_text()
    body=source.split('def loadSearchBins2018():',1)[1].split('\ndef ',1)[0]
    definitions=[]
    for windows,number in re.findall(r'SearchBinNumbers\[(.*?)\]\s*=\s*(\d+)',body):
        number=int(number)
        if number<=174:definitions.append((ast.literal_eval(windows),number))
    assert len(definitions)==174 and {n for _,n in definitions}==set(range(1,175))
    def legacy(point):
        matches=[n for windows,n in definitions if all(a<x<=b for (a,b),x in zip(windows,point))]
        assert len(matches)<=1,'Overlapping legacy intervals'
        return matches[0] if matches else -1
    checks=0
    for windows,number in definitions:
        center=[(a+b)/2 if i<2 else int(a)+1 for i,(a,b) in enumerate(windows)]
        assert R.Run3SearchBinNumber2018(*center)==number
        for i,(a,b) in enumerate(windows):
            for edge in [a,b]:
                values=[math.nextafter(edge,-math.inf),edge,math.nextafter(edge,math.inf)] if i<2 else [int(edge)-1,int(edge),int(edge)+1]
                for value in values:
                    point=center[:];point[i]=value
                    assert R.Run3SearchBinNumber2018(*point)==legacy(point),(point,number)
                    checks+=1
    for cut in [90.,100.,120.,160.]:
        for fit,mht,expected in [(True,math.nextafter(cut,-math.inf),True),(True,cut,False),
                                 (True,math.nextafter(cut,math.inf),False),(False,0.,False),
                                 (True,math.nan,False),(True,math.inf,False)]:
            assert R.Run3AcceptRebalancedSeed(fit,mht,cut)==expected
    assert R.Run3AcceptSmearedMht(2000.,2000.)
    assert not R.Run3AcceptSmearedMht(math.nextafter(2000.,math.inf),2000.)
    assert not R.Run3AcceptSmearedMht(math.nan,2000.)
    for ratio in [1.,1.2,1.20001,1.5,2.,3.]:
        for dphi in [0.,.5,1.,math.pi,5.3*ratio-4.78]:
            ht5=ratio*100
            expected=not(ht5/100>1.2 and dphi<5.3*ht5/100-4.78)
            assert R.Run3PassAndrewsTightHtRatio(dphi,ratio*100,100)==expected
    assert R.Run3PassAndrewsTightHtRatio(0,0,0)
    assert R.gInterpreter.Declare('''
    bool Run3CheckLegacyJetsAndClusters() {
      vector<UsefulJet> jets;
      for(auto q:vector<std::array<double,3>>{{80,.1,2.5},{600,3.0,1.1},{150,.2,0.0}}) {
        TLorentzVector v;v.SetPtEtaPhiM(q[0],q[1],q[2],0);jets.emplace_back(v,0,q[0]);
      }
      Run3LegacyJetFeatures a(jets);auto m=getMHT(jets,30);
      if(a.nj!=2 || fabs(a.dphi[0]-fabs(jets[2].tlv.DeltaPhi(m)))>1e-12 ||
         fabs(a.dphi[1]-fabs(jets[0].tlv.DeltaPhi(m)))>1e-12) return false;
      a.dphi={{.5,.5,0,0}};if(!a.highDeltaPhi())return false;
      a.dphi[1]=.499999;if(a.highDeltaPhi())return false;
      a.ht=1000;a.ht5=1000;a.mht=300;a.dphi={{1,1,1,1}};
      if(!a.highRegion()||a.lowRegion()||!a.sideband(true))return false;
      a.mht=1000;if(a.common())return false;
      Run3ClosurePair pair("regression",{0,1,2});
      pair.beginSeed();pair.fillObserved(.5,2);pair.fillPrediction(.5,.5);pair.fillPrediction(.5,.5);pair.endSeed();
      pair.beginSeed();pair.fillObserved(1.5,3);pair.fillPrediction(.5,2);pair.endSeed();
      return pair.prediction.GetBinContent(1)==3 && pair.variance[1]==5 && pair.cross.GetBinContent(1)==2 &&
             pair.observed.GetBinError(1)==2 && pair.observed.GetBinError(2)==3;
    }
    ''')
    assert R.Run3CheckLegacyJetsAndClusters()
    result=dict(legacy_files_unchanged=True,baseline='fd9821f',search_bins=174,search_bin_boundary_checks=checks,
                strict_rebalanced_mht_boundaries=[90,100,120,160],inclusive_smeared_mht_guard=2000,
                central_jet_dphi=True,missing_jet_dphi_ignored=True,paired_seed_second_moments=True,
                andrews_filter_exact=True)
    write_json(args.output,result);print(result)
if __name__=='__main__':main()
