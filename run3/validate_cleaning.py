#!/usr/bin/env python3
"""Boundary, argument-order, masking and data-only certification checks."""
import argparse
import itertools
import tempfile
import subprocess
import sys
import correctionlib
from common import *


def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True);p.add_argument("--config")
    args=p.parse_args();cfg=config(args.config);R=root(True);configure_cleaning(R,cfg)
    ids=correctionlib.CorrectionSet.from_file(cfg["jet_id_payload"]["path"])
    veto=correctionlib.CorrectionSet.from_file(cfg["jet_veto_payload"]["path"])[cfg["jet_veto_payload"]["name"]]
    checked=0
    # Exact eta/fraction/multiplicity boundaries are where the old hand recipe differed.
    for eta,chf,nhf,cef,nef,muf,nch,nne in itertools.product(
            [-5.,-3.,-2.7,-2.6,0.,2.6,2.7,3.,5.], [0.,.005,.01,.5], [.1,.9,.99],
            [.1,.8], [.1,.4,.9,.99], [.1,.8], [0,1,2], [0,1,2]):
        for lep in [False,True]:
            expected=ids["AK4PUPPI_TightLeptonVeto" if lep else "AK4PUPPI_Tight"].evaluate(
                eta,chf,nhf,cef,nef,muf,nch,nne,nch+nne)>0.5
            actual=R.Run3JetID(eta,chf,nhf,cef,nef,muf,nch,nne,lep)
            if actual!=expected:raise AssertionError("Jet-ID argument/boundary mismatch")
            checked+=1
    masked=None;unmasked=None;maps=0
    for eta in [-4.9+0.1*i for i in range(99)]:
        for phi in [-3.1+0.1*i for i in range(63)]:
            expected=veto.evaluate("jetvetomap",eta,phi)!=0
            if R.Run3InVetoMap(eta,phi)!=expected:raise AssertionError("Veto-map mismatch")
            if expected and abs(eta)<2.6:masked=(eta,phi)
            if not expected:unmasked=(eta,phi)
            maps+=1
    if masked is None or unmasked is None: raise AssertionError("Map has no tested masked/unmasked cells")
    eta,phi=masked
    if not (R.Run3VetoEligible(20.,eta,.5,.1,.1,.1,.01,10,10) and R.Run3InVetoMap(eta,phi)):
        raise AssertionError("Good jet in masked cell must veto event")
    for pt,cef,muf in [(15.,.1,.01),(20.,.8,.01),(20.,.1,.8)]:
        if R.Run3VetoEligible(pt,eta,.5,.1,cef,.1,muf,10,10):
            raise AssertionError("Ineligible jet must not veto event")
    # Synthetic certification file tests inclusive boundaries and missing-run rejection.
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"cert.json";path.write_text('{"123": [[4, 6], [10, 10]]}')
        configure_cleaning(R,cfg,True,str(path))
        for run,lumi,expected in [(123,3,False),(123,4,True),(123,6,True),(123,7,False),(123,10,True),(124,4,False)]:
            if R.Run3PassLumi(run,lumi)!=expected:raise AssertionError("Golden JSON mismatch")
        configure_cleaning(R,cfg)
        if not R.Run3PassLumi(124,4):raise AssertionError("Certification must be bypassed in MC")
        for data,golden in [(True,None),(False,str(path))]:
            try: configure_cleaning(R,cfg,data,golden)
            except ValueError:pass
            else:raise AssertionError("Data/MC certification guard not enforced")
    configure_cleaning(R,cfg)
    # A muon-dominated central jet passes Tight and fails TightLeptonVeto.
    for wp,expected in [("AK4PUPPI_Tight",True),("AK4PUPPI_TightLeptonVeto",False)]:
        alternate=dict(cfg,analysis_jet_id_wp=wp);configure_cleaning(R,alternate)
        if R.Run3AnalysisJetID(0.,.5,.1,.1,.1,.8,10,10)!=expected:
            raise AssertionError("Analysis jet-ID working point was not applied")
    configure_cleaning(R,cfg)
    # Exercise the complete data-cleaning CLI on a toy Events tree with no gen branches.
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);nano=tmp/"data.root";golden=tmp/"golden.json";report=tmp/"report.json"
        golden.write_text('{"123": [[4, 6], [10, 10]]}')
        frame=R.RDataFrame(6).Define("run","unsigned(rdfentry_==5 ? 124 : 123)")
        frame=frame.Define("luminosityBlock","std::vector<unsigned>{1,4,6,7,10,4}.at(rdfentry_)")
        for name,expression in {
            "Jet_pt":"std::vector<float>{80.f,70.f}",
            "Jet_eta":f"std::vector<float>{{rdfentry_==4 ? {eta}f : 0.f,0.f}}",
            "Jet_phi":f"std::vector<float>{{rdfentry_==4 ? {phi}f : 0.f,0.f}}",
            "Jet_chHEF":"std::vector<float>{.5f,.5f}","Jet_neHEF":"std::vector<float>{.1f,.1f}",
            "Jet_chEmEF":"std::vector<float>{.1f,.1f}","Jet_neEmEF":"std::vector<float>{.1f,.1f}",
            "Jet_muEF":"std::vector<float>{.01f,.01f}",
            "Jet_chMultiplicity":"std::vector<unsigned char>{10,10}",
            "Jet_neMultiplicity":"std::vector<unsigned char>{10,10}"}.items():
            frame=frame.Define(name,expression)
        for flag in cfg["filters"]:
            frame=frame.Define(flag,"rdfentry_!=1" if flag=="Flag_BadPFMuonFilter" else "true")
        frame.Snapshot("Events",str(nano))
        command=[sys.executable,str(BASE/"audit_selection.py"),"--nano",str(nano),"--is-data",
                 "--golden-json",str(golden),"--output",str(report),"--snapshot",str(tmp/"cleaned.root"),
                 "--jet-map-dir",str(tmp/"jet_maps")]
        if args.config:command += ["--config",args.config]
        subprocess.run(command,check=True,capture_output=True,text=True)
        counts=json.loads(report.read_text())["cumulative"]
        assert counts["input"]==6 and counts["golden_json"]==3
        assert counts["Flag_ecalBadCalibFilter"]==2 and counts["jet_veto_map"]==1, counts
        jet_maps=json.loads(report.read_text())["jet_maps"]
        assert jet_maps["before_jets"]==4 and jet_maps["after_jets"]==2, jet_maps
        assert jet_maps["masked_before_jets"]==1 and jet_maps["masked_after_jets"]==0, jet_maps
        f=open_root(R,tmp/"cleaned.root")
        assert f.Get("Events").GetEntries()==1 and not f.Get("Events").GetBranch("genWeight")
        f.Close()
    result=dict(passed=True,jet_id_boundary_comparisons=checked,map_comparisons=maps,
                masked_point=masked,unmasked_point=unmasked,golden_json_boundary_and_mode_checks=True,
                data_cli_without_gen_branches=True,data_cli_cutflow=counts,
                analysis_jet_id_working_point_checks=True,jet_map_toy_checks=jet_maps,
                scope="Validates adapter and pinned payload evaluation; does not certify a physics analysis")
    write_json(args.output,result);print(result)


if __name__=="__main__":main()
