#!/usr/bin/env python3
"""Physics-relevant regression checks for spline caching, fixed recoil and fit boundaries."""
import argparse
import math
from common import *

def main():
    p=argparse.ArgumentParser();p.add_argument("--templates",required=True)
    p.add_argument("--nano",required=True);p.add_argument("--config");p.add_argument("--events",type=int,default=100)
    p.add_argument("--output",default="run3_work/validation.json");args=p.parse_args()
    cfg=config(args.config);R=root(True);f=open_root(R,args.templates);R.GleanTemplatesFromFile(f)
    configure_cleaning(R,cfg)
    assert R.Run3PdfDomains.size()==f.Get("splines").GetListOfKeys().GetSize(), "Incomplete PDF loading"
    # Compare every cached spline to ROOT's original path, including tails/extrapolation.
    maxdiff=0;count=0
    directory=f.Get("splines")
    for key in directory.GetListOfKeys():
        g=R.Run3LoadPdfGraph(f,"splines/"+key.GetName())
        for i in range(81):
            low,high=(g.GetX()[0],g.GetX()[g.GetN()-1])
            x=low+(high-low)*(i-2)/76
            a=g.Eval(x,0,"S");b=R.Run3EvalCubic(g,x)
            maxdiff=max(maxdiff,abs(a-b)/max(1,abs(a)))
            if not math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-12):
                raise AssertionError(f"Spline mismatch for {g.GetName()} at {x}: {a}, {b}")
            count+=1
            R.Run3UseCachedSplines=False; safe_a=R.Run3Eval(g,x)
            R.Run3UseCachedSplines=True; safe_b=R.Run3Eval(g,x)
            assert safe_a==safe_b and math.isfinite(safe_b) and safe_b>=0, "Bounded density regression"
    # Directly test the posterior's recoil against every jet + fixed object.
    R.gInterpreter.Declare("""
    bool Run3CheckFixedRecoil() {
      auto saved=_Templates_.dynamicJets;
      auto fixed=Run3FixedObjects;
      _Templates_.dynamicJets.clear();
      for (int i=0;i<13;++i) {
        TLorentzVector v;v.SetPtEtaPhiM(250-i*10,0.2,0.47*i,5);
        _Templates_.dynamicJets.emplace_back(v,0, v.Pt());
      }
      _Templates_.nparams=12;
      TLorentzVector photon; photon.SetPtEtaPhiM(100,0.3,1.1,0);
      SetRun3FixedObjects(photon);
      auto expected=getMHT(_Templates_.dynamicJets,15)-photon;
      std::vector<double> parameters(12,1);_par_=parameters.data();
      Int_t npar=12;double objective=0;fcn(npar,nullptr,objective,parameters.data(),0);
      bool ok=fabs(expected.Px()-_ActiveMht_.Px())<1e-9 &&
              fabs(expected.Py()-_ActiveMht_.Py())<1e-9 &&
              fabs(Run3FixedObjects.Pt()-100)<1e-9;
      _Templates_.dynamicJets=saved;SetRun3FixedObjects(fixed);return ok;
    }
    """)
    assert R.Run3CheckFixedRecoil(), "Fixed objects or jets beyond the 12-parameter cap are missing from recoil"
    n=R.Run3NanoReader(args.nano,cfg["btag_branch"],cfg["btag_cut"],vector(R,"string",cfg["filters"]))
    fits=0;maxptdiff=0
    while fits<args.events and n.next():
        if not n.selected(): continue
        R.Run3UseCachedSplines=False
        success_a=R.RebalanceJets_BayesFitter(n.jets)
        a=[j.Pt() for j in R._Templates_.dynamicJets]
        R.Run3UseCachedSplines=True
        success_b=R.RebalanceJets_BayesFitter(n.jets)
        b=[j.Pt() for j in R._Templates_.dynamicJets]
        assert success_a==success_b, "Caching changed fit success"
        for pa,pb in zip(a,b):
            maxptdiff=max(maxptdiff,abs(pa-pb))
            assert math.isclose(pa,pb,rel_tol=1e-8,abs_tol=1e-6), "Caching changed fitted jet momenta"
        fits+=1
    if fits!=args.events: raise AssertionError("Insufficient regression events")
    result=dict(spline_evaluations=count,max_spline_relative_difference=maxdiff,
                fit_pairs=fits,max_fitted_pt_difference=maxptdiff,fixed_recoil=True)
    write_json(args.output,result);print(result)

if __name__=="__main__":main()
