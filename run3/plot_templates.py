#!/usr/bin/env python3
"""Audit every PDF's support, cubic interpolation and histogram/spline agreement."""
import argparse
import math
from array import array
from pathlib import Path
from common import root, open_root, metadata, write_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--templates", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--points", type=int, default=4097)
    args = p.parse_args()
    R = root()
    f = open_root(R, args.templates)
    meta = metadata(R, f)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    borrowed = {r["target"]: r for r in meta["borrowed"]}
    unused = set(meta["structurally_unused"])
    rows = []
    plots = []
    R.gStyle.SetOptStat(0)
    R.gStyle.SetPaperSize(28,20)
    canvas = R.TCanvas("spline_audit", "Spline audit", 1400, 1000)
    canvas.Divide(3, 3, 0.003, 0.003)
    pdf = str(out / "spline_atlas.pdf")
    canvas.Print(pdf + "[")
    directory = f.Get("splines")
    for index, key in enumerate(directory.GetListOfKeys()):
        name = key.GetName().removesuffix("_graph")
        g = directory.Get(key.GetName())
        h = f.Get(name)
        s = R.TSpline3("audit_spline", g)
        low, high = g.GetX()[0], g.GetX()[g.GetN()-1]
        dx = (high-low)/(args.points-1)
        xs = [low+i*dx for i in range(args.points)]
        ys = [s.Eval(x) for x in xs]
        finite = all(math.isfinite(y) for y in ys)
        peak = max(ys)
        negative_area = sum(max(0, -y)*dx*(0.5 if i in (0,len(ys)-1) else 1)
                            for i,y in enumerate(ys))
        area = sum(y*dx*(0.5 if i in (0,len(ys)-1) else 1) for i,y in enumerate(ys))
        axis_low,axis_high=h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax()
        axis_dx=(axis_high-axis_low)/(args.points-1)
        bounded_values=[max(0.,s.Eval(min(high,max(low,axis_low+i*axis_dx)))) for i in range(args.points)]
        bounded_area=sum(y*axis_dx*(0.5 if i in (0,len(bounded_values)-1) else 1)
                         for i,y in enumerate(bounded_values))
        density = h.Clone("raw_density")
        density.SetDirectory(0)
        density.Scale(1/h.Integral(), "width")

        l1 = sum(abs(y-density.GetBinContent(density.FindBin(x)))*dx for x,y in zip(xs,ys))
        under, over = h.GetBinContent(0), h.GetBinContent(h.GetNbinsX()+1)
        flow = (under+over)/(h.Integral()+under+over)
        status = "unused" if name in unused else "borrowed" if name in borrowed else "measured"
        row = dict(name=name, status=status, effective_entries=meta["effective_entries"][name],
                   donor=borrowed.get(name, {}).get("donor"),
                   finite=finite, knot_domain=[low,high], integral_on_knot_domain=area,
                   min_density=min(ys), max_density=peak, negative_area=negative_area,
                   significant_negative=min(ys)<-max(1e-12,1e-6*peak),
                   negative_fraction=sum(y<0 for y in ys)/len(ys),
                   histogram_spline_l1=l1, donor_histogram_flow_fraction=flow)
        row.update(histogram_support=[axis_low,axis_high],bounded_integral_on_histogram_support=bounded_area,
                   production_policy=meta["config"].get("spline_pdf_policy","legacy_cubic"))
        if name.startswith("hRTemplate"):
            fit_x = [0.3+3.2*i/(args.points-1) for i in range(args.points)]
            fit_y = [s.Eval(x) for x in fit_x]
            row.update(fitter_domain=[0.3,3.5], fitter_min_density=min(fit_y),
                       fitter_significant_negative=min(fit_y)<-max(1e-12,1e-6*peak),
                       fraction_fitter_domain_extrapolated=sum(x<low or x>high for x in fit_x)/len(fit_x))
        rows.append(row)
        pad = canvas.cd(index%9+1)
        pad.SetLeftMargin(0.13); pad.SetBottomMargin(0.12); pad.SetTopMargin(0.13)
        density.SetTitle(name.replace("hRTemplate", "").replace("hGenMht", "")+";"+
                         ("reco p_{T} / gen p_{T}" if name.startswith("hR") else "MHT [GeV]" if "PtB" in name else "|#Delta#phi|" )+";density")
        density.SetLineColor(R.kGray+2); density.SetLineWidth(1)
        density.GetXaxis().SetTitleSize(.045); density.GetYaxis().SetTitleSize(.045)
        density.GetYaxis().SetTitleOffset(1.4)
        density.SetMinimum(min(0,min(ys)*1.2)); density.SetMaximum(max(peak,density.GetMaximum())*1.25)
        density.Draw("HIST")
        line = R.TGraph(len(xs),array("d",xs),array("d",ys))
        line.SetLineColor(R.kBlue+1 if status=="measured" else R.kOrange+7 if status=="borrowed" else R.kGray+1)
        line.SetLineWidth(2); line.Draw("L SAME")
        label = R.TLatex(); label.SetNDC(); label.SetTextSize(.036)
        label.DrawLatex(.14,.91,f"{status}, N_{{eff}}={row['effective_entries']:.0f}")
        label.DrawLatex(.14,.83,f"#int={area:.3f}, min={min(ys):.2g}")
        single=R.TCanvas("template_curve",name,1000,750)
        density.Draw("HIST");line.Draw("L SAME");label.DrawLatex(.14,.91,f"{status}, N_{{eff}}={row['effective_entries']:.0f}")
        single.SaveAs(str(out/(name+'.png')))
        canvas.cd(index%9+1)
        plots.extend([density,line,label])
        if index%9==8 or index==directory.GetListOfKeys().GetSize()-1:
            canvas.cd()
            canvas.Print(pdf)
            if index<9: canvas.SaveAs(str(out/"first_page.png"))
            canvas.Clear(); canvas.Divide(3,3,0.003,0.003); plots.clear()
    canvas.Print(pdf+"]")
    counts = {status:sum(r["status"]==status for r in rows) for status in ["measured","borrowed","unused"]}
    summary = dict(total=len(rows), **counts,
                   nonfinite=sum(not r["finite"] for r in rows),
                   significant_negative=sum(r["significant_negative"] for r in rows),
                   significant_negative_reachable=sum(r["significant_negative"] and r["status"]!="unused" for r in rows),
                   fitter_significant_negative=sum(r.get("fitter_significant_negative",False) and r["status"]!="unused" for r in rows),
                   integral_range=[min(r["integral_on_knot_domain"] for r in rows),max(r["integral_on_knot_domain"] for r in rows)],
                   bounded_integral_range=[min(r["bounded_integral_on_histogram_support"] for r in rows),max(r["bounded_integral_on_histogram_support"] for r in rows)],
                   max_negative_area=max(r["negative_area"] for r in rows))
    write_json(out/"audit.json", dict(templates=str(Path(args.templates).resolve()), summary=summary, curves=rows,
               interpretation="Histogram smoothing followed by cubic interpolation; there is no fitted spline convergence criterion. No model changes made by this audit.",
               note="Gray: unsmoothed normalized histogram used for sampling; colored: spline used in likelihood. Integrals exclude outer half-bins; MC statistical support is separate from numerical smoothness."))
    print(summary)
    f.Close()


if __name__ == "__main__":
    main()
