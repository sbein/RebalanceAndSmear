#!/usr/bin/env python3
"""ROOT-only diagnostic plotting, with correlated MHT ratio uncertainties."""
import argparse
from pathlib import Path
from common import root, open_root, metadata, write_json

def main():
    p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--outdir",default="run3_work/plots")
    p.add_argument("--label",required=True)
    args=p.parse_args();ROOT=root();f=open_root(ROOT,args.input);record=metadata(ROOT,f)
    outdir=Path(args.outdir);outdir.mkdir(parents=True,exist_ok=True)
    numbers={}
    for plotname in ["MHT","MHT_full","HT","NJets","BTags","DPhi1"]:
        observable="MHT" if plotname=="MHT_full" else plotname
        a=f.Get(observable+"_observed");b=f.Get(observable+"_prediction")
        c=ROOT.TCanvas("c"+plotname,"Run 3 R&S closure",900,850)
        top=ROOT.TPad("top","",0,0.30,1,1);bot=ROOT.TPad("bot","",0,0,1,0.30)
        top.SetBottomMargin(0.02);top.SetTopMargin(0.22);bot.SetTopMargin(0.03);bot.SetBottomMargin(0.3)
        top.Draw();bot.Draw();top.cd();top.SetLogy()
        a.SetStats(False);a.SetMarkerStyle(20);a.SetLineColor(ROOT.kBlack)
        b.SetLineColor(ROOT.kAzure+2);b.SetFillColorAlpha(ROOT.kAzure+1,0.3)
        a.SetTitle("");a.GetYaxis().SetTitle("Cross section [pb / bin]")
        a.GetXaxis().SetLabelSize(0);a.GetXaxis().SetTitleSize(0)
        upper=1000 if plotname=="MHT" else a.GetXaxis().GetXmax()
        a.GetXaxis().SetRangeUser(a.GetXaxis().GetXmin(),upper)
        a.SetMinimum(max(1e-8,a.GetMaximum()*1e-5));a.SetMaximum(max(a.GetMaximum(),b.GetMaximum())*20)
        a.Draw("E1");b.Draw("E2 SAME");b.Draw("HIST SAME");a.Draw("E1 SAME")
        leg=ROOT.TLegend(0.56,0.58,0.89,0.78);leg.SetBorderSize(0)
        leg.AddEntry(a,"Held-out reco QCD","pe");leg.AddEntry(b,"Rebalance + smear","lf");leg.Draw()
        txt=ROOT.TLatex();txt.SetNDC();txt.SetTextSize(0.03);txt.SetTextFont(42)
        txt.SetTextSize(.026)
        txt.DrawLatex(0.12,0.96,"2024 NanoAODv15 QCD HT1200-1500")
        txt.DrawLatex(0.12,0.918,args.label)
        txt.DrawLatex(0.12,0.876,"Inclusive pilot: HT > 300, N_{jets} #geq 2")
        txt.DrawLatex(0.12,0.834,"Seed errors; template uncertainty excluded")
        bot.cd()
        ratio=f.Get("MHT_ratio") if observable=="MHT" else b.Clone(observable+"_ratio_plot")
        if observable!="MHT": ratio.Divide(a)
        ratio.SetTitle("");ratio.SetStats(False);ratio.GetYaxis().SetTitle("R&S / reco")
        ratio.GetXaxis().SetTitle(observable+(" [GeV]" if observable in ["MHT","HT"] else ""))
        visible=[(ratio.GetBinContent(i),ratio.GetBinError(i)) for i in range(1,a.GetNbinsX()+1)
                 if a.GetBinContent(i)>0 and a.GetBinLowEdge(i)<upper]
        ratio.SetMinimum(min([0.]+[1.1*(v-e) for v,e in visible]))
        ratio.SetMaximum(max([2.5]+[1.1*(v+e) for v,e in visible]))
        ratio.SetMarkerStyle(20)
        for ax in [ratio.GetXaxis(),ratio.GetYaxis()]:ax.SetTitleSize(0.1);ax.SetLabelSize(0.08)
        ratio.GetXaxis().SetRangeUser(ratio.GetXaxis().GetXmin(),upper)
        ratio.GetYaxis().SetTitleOffset(0.45);ratio.Draw("AXIS")
        points=ROOT.TGraphErrors()
        for ib in range(1,a.GetNbinsX()+1):
            if a.GetBinContent(ib)<=0:continue
            ip=points.GetN()
            points.SetPoint(ip,a.GetBinCenter(ib),ratio.GetBinContent(ib))
            points.SetPointError(ip,a.GetBinWidth(ib)/2,ratio.GetBinError(ib))
        points.SetMarkerStyle(20);points.SetMarkerColor(ROOT.kAzure+2);points.Draw("P SAME")
        line=ROOT.TLine(ratio.GetXaxis().GetXmin(),1,upper,1);line.SetLineStyle(2);line.Draw()
        c.cd();c.SaveAs(str(outdir/(plotname+".png")))
        numbers[observable]=[dict(low=a.GetBinLowEdge(i),high=a.GetBinLowEdge(i+1),
            observed_pb=a.GetBinContent(i),predicted_pb=b.GetBinContent(i),
            ratio=ratio.GetBinContent(i) if a.GetBinContent(i)>0 else None,
            ratio_error=ratio.GetBinError(i) if a.GetBinContent(i)>0 else None,
            ratio_error_scope="paired seed clusters" if observable=="MHT" else "uncorrelated plotting approximation")
          for i in range(1,a.GetNbinsX()+1)]
    write_json(outdir/"bins.json",numbers)
    f.Close()

if __name__=="__main__": main()
