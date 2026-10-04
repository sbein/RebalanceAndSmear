#!/usr/bin/env python3
"""Merge raw templates, audit coverage, and write legacy-compatible spline graphs."""
import argparse
import glob
import math
from pathlib import Path
from common import *

def effective_entries(h):
    total=h.Integral()
    variance=sum(h.GetBinError(i)**2 for i in range(1,h.GetNbinsX()+1))
    return total*total/variance if variance else 0

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs",nargs="+",required=True,help="Raw ROOT files or glob patterns")
    p.add_argument("--output",required=True)
    p.add_argument("--min-entries",type=float,default=50)
    p.add_argument("--allow-sparse",action="store_true",help="Pilot only: explicitly record every borrowed distribution")
    p.add_argument("--smooth",type=int,default=5)
    p.add_argument("--legacy-density-normalization",action="store_true",help="Diagnostic only: reproduce the initial pilot's normalization before smoothing")
    args=p.parse_args()
    if Path(args.output).exists(): raise FileExistsError(args.output)
    ROOT=root()
    files=sorted(set(path for pattern in args.inputs for path in glob.glob(pattern)))
    if not files: raise ValueError("No raw input files")
    combined={};records=[];cfg=None;totals={};cross_sections={};seen=set();policies=set()
    for path in files:
        f=open_root(ROOT,path);record=metadata(ROOT,f);f.Close()
        if record.get("format_version")!=1: raise ValueError("Unsupported raw template normalization")
        dataset=record.get("normalization_group",record["sample"]["dataset"])
        cross_section=record["sample"]["cross_section_pb"]
        policies.add(record.get("generator_weight_policy","genWeight"))
        if len(policies)>1:raise ValueError("Cannot mix unit and genWeight training shards")
        if dataset in cross_sections and cross_sections[dataset]!=cross_section:
            raise ValueError("Conflicting cross sections for "+dataset)
        cross_sections[dataset]=cross_section
        for file in record["files"]:
            identity=(file["lfn"],record["split"])
            if identity in seen: raise ValueError("Duplicate training file: "+file["lfn"])
            seen.add(identity)
            denominator=file["statistics"]["scanned"] if record.get("generator_weight_policy")=="ignore" else file["statistics"]["sumw"]
            if record.get("generator_weight_policy")=="ignore" and record["split"]!=2:raise ValueError("Unit-weight full-statistics templates require all input events, split=2")
            totals[dataset]=totals.get(dataset,0)+denominator
        records.append(record)
    if any(v<=0 for v in totals.values()): raise ValueError("Nonpositive dataset normalization")
    records=[]
    for path in files:
        f=open_root(ROOT,path);record=metadata(ROOT,f)
        if cfg is None: cfg=record["config"]
        require_compatible(record,cfg);records.append(record)
        for key in f.GetListOfKeys():
            name=key.GetName();obj=f.Get(name)
            if not obj.InheritsFrom("TH1"): continue
            clone=obj.Clone(name);clone.SetDirectory(0)
            if name.startswith("hGenMht"):
                dataset=record.get("normalization_group",record["sample"]["dataset"])
                clone.Scale(cross_sections[dataset]/totals[dataset])
            if name not in combined:
                combined[name]=clone
            elif name not in ["hPtTemplate","hEtaTemplate","hHtTemplate"]:
                combined[name].Add(clone)
        f.Close()
    # Validate all distributions before writing any template file.
    templates={}; specs={}; audit=[]; deficient=[]
    pt,eta,ht=cfg["pt_edges"],cfg["eta_edges"],cfg["ht_edges"]
    for tag in range(2):
        for ie in range(len(eta)-1):
            for ip in range(len(pt)-1):
                name=response_name(pt,eta,ip,ie,tag)
                specs[name]=("response",tag,ip,ie)
    for tag in range(4):
        for ih in range(len(ht)):
            for kind in ["Pt","Phi"]:
                specs[prior_name(ht,ih,tag,kind)]=(kind,tag,ih,0)
    unused=[name for name,spec in specs.items()
            if spec[0]=="response" and spec[1]==1 and eta[spec[3]]>=cfg["ht_eta"]]
    entries={name:effective_entries(combined[name]) for name in specs}
    valid=[name for name in specs if entries[name]>=args.min_entries and combined[name].Integral()>0]
    for name,spec in specs.items():
        if name in unused: continue
        if name in valid:
            templates[name]=combined[name]
            continue
        deficient.append(name)
        if not args.allow_sparse: continue
        # Keep flavour and observable; borrowing across eta/HT is explicitly a pilot approximation.
        candidates=[n for n in valid if specs[n][:2]==spec[:2]]
        if not candidates: raise ValueError(f"No populated donor in category {spec[:2]}")
        def distance(n):
            _,_,i,j=spec;_,_,ii,jj=specs[n]
            if spec[0]=="response":
                pi=(pt[i]+pt[i+1])/2;pj=(pt[ii]+pt[ii+1])/2
                ei=(eta[j]+eta[j+1])/2;ej=(eta[jj]+eta[jj+1])/2
                return abs(math.log(max(1,pi)/max(1,pj)))+2*abs(ei-ej)
            return abs(i-ii)
        donor=min(candidates,key=lambda n:(distance(n),n))
        h=combined[donor].Clone(name);h.SetDirectory(0);templates[name]=h
        audit.append(dict(target=name,donor=donor,target_effective_entries=entries[name],
                          donor_effective_entries=entries[donor]))
    # Forward jets cannot be tagged by NanoReader. Populate compatibility slots
    # with the same cell's untagged PDF, without treating this as a measured B PDF.
    for name in unused:
        _,_,ip,ie=specs[name]
        donor=response_name(pt,eta,ip,ie,0)
        if donor in templates:
            h=templates[donor].Clone(name);h.SetDirectory(0);templates[name]=h
    report=dict(config=cfg,generator_weight_policy=next(iter(policies)),normalization_totals=totals,training_records=records,raw_files=files,min_entries=args.min_entries,
                sparse_pilot=bool(audit),borrowed=audit,deficient=deficient,
                effective_entries=entries,smoothing=args.smooth,structurally_unused=unused,
                density_normalization="before smoothing (diagnostic)" if args.legacy_density_normalization else "after smoothing and bounded cubic numerical integral; evaluator uses histogram support",
                limitations=["NanoAOD Jet_pt>15 storage truncates low-response tails for low-pT gen jets",
                  "NanoAOD GenJet_pt>10 storage omits softer neighbors from the isolation calculation",
                  "Event flags, official jet ID and jet-veto map are applied; analysis lepton/photon/track vetoes, triggers and data corrections are not applied"])
    write_json(args.output+".coverage.json",report)
    if deficient and not args.allow_sparse:
        raise ValueError(f"{len(deficient)} deficient bins; see coverage report. Use --allow-sparse only for a pilot")
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    f=ROOT.TFile(args.output,"RECREATE");f.cd()
    for name in ["hPtTemplate","hEtaTemplate","hHtTemplate"]: combined[name].Write()
    for h in templates.values(): h.Write()
    splines=f.mkdir("splines");splines.cd()
    for name,h in templates.items():
        density=h.Clone(name+"_density");density.SetDirectory(0)
        if any(density.GetBinContent(i)<0 for i in range(1,density.GetNbinsX()+1)):
            raise ValueError(f"Negative probability bin: {name}")
        density.Scale(1.0/density.Integral(),"width");density.Smooth(args.smooth)
        if not args.legacy_density_normalization:
            density.Scale(1.0/density.Integral("width"))
        graph=ROOT.TGraph(density)
        if not args.legacy_density_normalization:
            spline=ROOT.TSpline3("normalization_spline",graph)
            low,high=density.GetXaxis().GetXmin(),density.GetXaxis().GetXmax()
            first,last=graph.GetX()[0],graph.GetX()[graph.GetN()-1]
            steps=16384;dx=(high-low)/steps
            integral=sum(max(0.,spline.Eval(min(last,max(first,low+i*dx))))*dx*
                         (0.5 if i in (0,steps) else 1) for i in range(steps+1))
            if not math.isfinite(integral) or integral<=0: raise ValueError("Invalid bounded PDF integral: "+name)
            for i in range(graph.GetN()):graph.SetPoint(i,graph.GetX()[i],graph.GetY()[i]/integral)
        graph.Write(name+"_graph")
    f.cd();write_metadata(ROOT,report);f.Close()
    # Read back exactly the complete naming grid consumed by GleanTemplatesFromFile.
    f=open_root(ROOT,args.output)
    for name in specs:
        if not f.Get(name) or not f.Get("splines/"+name+"_graph"):
            raise ValueError("Incomplete template output: "+name)
    f.Close()
    print(f"Wrote {args.output}: {len(specs)} PDFs, {len(audit)} explicitly borrowed pilot bins")

if __name__=="__main__": main()
