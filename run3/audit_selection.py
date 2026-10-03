#!/usr/bin/env python3
"""Apply and report the shared cleaning to MC or certified data without requiring gen branches."""
import argparse
import hashlib
import math
from pathlib import Path
from common import *


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--nano",required=True)
    p.add_argument("--config")
    p.add_argument("--max-events",type=int,default=-1)
    p.add_argument("--is-data",action="store_true")
    p.add_argument("--golden-json")
    p.add_argument("--output",required=True)
    p.add_argument("--snapshot",help="Optional Events-only cleaned ROOT file; input is preserved")
    p.add_argument("--jet-map-dir",help="Save unweighted eligible-jet eta/phi maps before and after event veto")
    args=p.parse_args()
    if Path(args.output).exists(): raise FileExistsError(args.output)
    if args.jet_map_dir:
        for name in ["jet_veto_maps.root","jet_veto_maps.png","jet_veto_maps.pdf"]:
            if (Path(args.jet_map_dir)/name).exists(): raise FileExistsError(Path(args.jet_map_dir)/name)
    cfg=config(args.config); R=root(True)
    configure_cleaning(R,cfg,args.is_data,args.golden_json)
    frame=R.RDataFrame("Events",args.nano)
    original_columns=[str(c) for c in frame.GetColumnNames()]
    required=cfg["filters"]+["run","luminosityBlock","Jet_pt","Jet_eta","Jet_phi","Jet_chHEF","Jet_neHEF",
              "Jet_chEmEF","Jet_neEmEF","Jet_muEF","Jet_chMultiplicity","Jet_neMultiplicity"]
    missing=set(required)-set(original_columns)
    if missing: raise ValueError("Missing required branches: "+str(sorted(missing)))
    if args.max_events>0: frame=frame.Range(args.max_events)
    results=[("input",frame.Count())]
    current=frame.Filter("Run3PassLumi(run,luminosityBlock)","certified lumis (data only)")
    results.append(("golden_json",current.Count()))
    independent=[]
    for flag in cfg["filters"]:
        independent.append((flag,current.Filter("!"+flag).Count()))
    for flag in cfg["filters"]:
        current=current.Filter(flag,flag)
        results.append((flag,current.Count()))
    shared="Jet_pt,Jet_eta,Jet_chHEF,Jet_neHEF,Jet_chEmEF,Jet_neEmEF,Jet_muEF,Jet_chMultiplicity,Jet_neMultiplicity"
    current=current.Filter("Run3PassAnalysisJetID("+shared+")","analysis jet ID")
    results.append(("jet_id",current.Count()))
    shared=shared.replace("Jet_eta,","Jet_eta,Jet_phi,")
    if args.jet_map_dir:
        current=current.Define("run3_veto_eta","Run3VetoJetCoordinates(false,"+shared+")")
        current=current.Define("run3_veto_phi","Run3VetoJetCoordinates(true,"+shared+")")
        current=current.Define("run3_masked_veto_jets","Run3CountMaskedVetoJets("+shared+")")
        before=current.Histo2D(("before_veto","Eligible jets before event veto;Jet #eta;Jet #phi",100,-5.,5.,128,-math.pi,math.pi),"run3_veto_eta","run3_veto_phi")
        masked_before=current.Sum("run3_masked_veto_jets")
    current=current.Filter("Run3PassVetoMap("+shared+")","jet-veto map")
    results.append(("jet_veto_map",current.Count()))
    if args.jet_map_dir:
        after=current.Histo2D(("after_veto","Eligible jets after event veto;Jet #eta;Jet #phi",100,-5.,5.,128,-math.pi,math.pi),"run3_veto_eta","run3_veto_phi")
        masked_after=current.Sum("run3_masked_veto_jets")
    report=dict(config=cfg,nano=args.nano,is_data=args.is_data,
                golden_json=args.golden_json,golden_json_sha256=hashlib.sha256(Path(args.golden_json).read_bytes()).hexdigest() if args.golden_json else None,
                cumulative={name:int(count.GetValue()) for name,count in results},
                flag_failures_independent={name:int(count.GetValue()) for name,count in independent},
                scope="Shared event cleaning only; no trigger or analysis lepton/photon/track veto; no additional JEC or JER")
    if args.jet_map_dir:
        directory=Path(args.jet_map_dir);directory.mkdir(parents=True,exist_ok=True)
        before=before.GetValue();after=after.GetValue()
        masked_before=int(masked_before.GetValue());masked_after=int(masked_after.GetValue())
        if masked_after!=0: raise AssertionError("Accepted events contain veto-eligible masked jets")
        survival=after.Clone("jet_survival");survival.Divide(before)
        survival.SetTitle("Jet survival (event veto);Jet #eta;Jet #phi")
        report["jet_maps"]=dict(directory=str(directory),before_jets=int(before.GetEntries()),after_jets=int(after.GetEntries()),
            masked_before_jets=masked_before,masked_after_jets=masked_after,
            definition="Unweighted eligible reconstructed jets after noise filters and analysis jet ID, before/after whole-event veto. Empty denominator bins display zero; survival is not a per-jet efficiency.")
        f=R.TFile(str(directory/"jet_veto_maps.root"),"CREATE");f.cd()
        for histogram in [before,after,survival]: histogram.Write()
        write_metadata(R,dict(config=cfg,jet_maps=report["jet_maps"],cumulative=report["cumulative"]))
        f.Close()
        R.gStyle.SetOptStat(0);R.gStyle.SetPalette(R.kViridis)
        canvas=R.TCanvas("jet_veto_maps","Jet veto validation",1500,560);canvas.Divide(3,1)
        labels=[]
        for i,histogram in enumerate([before,after,survival],1):
            pad=canvas.cd(i);pad.SetRightMargin(.16);pad.SetLeftMargin(.13);pad.SetBottomMargin(.12)
            if i<3:
                pad.SetLogz();histogram.SetMinimum(1.);histogram.SetMaximum(max(2.,before.GetMaximum()))
            else: histogram.SetMinimum(0.);histogram.SetMaximum(1.)
            histogram.Draw("COLZ")
            label=R.TLatex();label.SetNDC();label.SetTextSize(.027)
            label.DrawLatex(.13,.94,"Summer24Prompt24_RunBCDEFGHI_V1")
            if i<3: label.DrawLatex(.13,.025,f"Eligible jets: {int(histogram.GetEntries())}; masked: {masked_before if i==1 else masked_after}")
            else: label.DrawLatex(.13,.025,"Empty denominator cells shown as 0")
            labels.append(label)
        R.gStyle.SetPaperSize(28.,10.5)
        for suffix in ["png","pdf"]:
            canvas.cd();canvas.Print(str(directory/("jet_veto_maps."+suffix)))
    if args.snapshot:
        if Path(args.snapshot).exists(): raise FileExistsError(args.snapshot)
        current.Snapshot("Events",args.snapshot,vector(R,"string",original_columns))
        report["snapshot"]=args.snapshot
        report["snapshot_scope"]="Events tree only; does not copy Runs/LuminosityBlocks or renormalize MC weights"
    write_json(args.output,report)
    print(report["cumulative"])


if __name__=="__main__": main()
