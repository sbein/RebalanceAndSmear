#!/usr/bin/env python3
"""Compare paired-seed MHT closure ratios from explicitly labelled workflow variants."""
import argparse
from common import *


def main():
    p=argparse.ArgumentParser();p.add_argument("--inputs",nargs="+",required=True)
    p.add_argument("--labels",nargs="+",required=True);p.add_argument("--output",required=True)
    args=p.parse_args()
    if len(args.inputs)!=len(args.labels):p.error("One label required per input")
    R=root();R.gStyle.SetOptStat(0)
    canvas=R.TCanvas("compare_closure","MHT closure comparison",1000,650)
    canvas.SetTopMargin(.15);canvas.SetBottomMargin(.13);canvas.SetLeftMargin(.11)
    frame=R.TH1D("frame",";MHT [GeV];R&S / observed reco",70,0,700)
    frame.SetMinimum(0);frame.SetMaximum(3);frame.Draw("AXIS")
    frame.GetYaxis().SetTitleOffset(1.2)
    legend=R.TLegend(.5,.62,.88,.82);legend.SetBorderSize(0)
    graphs=[];files=[];report=[]
    for i,(path,label) in enumerate(zip(args.inputs,args.labels)):
        f=open_root(R,path);files.append(f);observed=f.Get("MHT_observed");ratio=f.Get("MHT_ratio")
        g=R.TGraphErrors();rows=[]
        for ib in range(1,observed.GetNbinsX()+1):
            if observed.GetBinContent(ib)<=0:continue
            low,high=observed.GetXaxis().GetBinLowEdge(ib),observed.GetXaxis().GetBinUpEdge(ib)
            value,error=ratio.GetBinContent(ib),ratio.GetBinError(ib)
            rows.append(dict(low=low,high=high,ratio=value,ratio_error=error))
            if low>=700:continue
            index=g.GetN();g.SetPoint(index,(low+high)/2,value);g.SetPointError(index,(high-low)/2,error)
        g.SetLineColor([R.kGray+2,R.kOrange+7,R.kBlue+1][i%3]);g.SetMarkerColor(g.GetLineColor())
        g.SetMarkerStyle(20+i);g.SetLineWidth(2);g.Draw("LP SAME")
        legend.AddEntry(g,label,"lp");graphs.append(g)
        report.append(dict(label=label,path=path,bins=rows))
    ymax=max([3.]+[1.1*(row["ratio"]+row["ratio_error"]) for variant in report for row in variant["bins"] if row["low"]<700])
    frame.SetMaximum(ymax)
    one=R.TLine(0,1,700,1);one.SetLineStyle(2);one.Draw();legend.Draw()
    title=R.TLatex();title.SetNDC();title.SetTextSize(.03)
    title.DrawLatex(.11,.95,"2024 NanoAODv15 QCD HT1200-1500; held-out split")
    title.DrawLatex(.11,.90,"Seed-statistical errors; template uncertainty excluded")
    canvas.SaveAs(args.output)
    write_json(args.output+".json",dict(variants=report,note="Variants share events and are correlated; plotted errors are individual paired-seed ratio errors, not errors on differences."))
    for f in files:f.Close()


if __name__=="__main__":main()
