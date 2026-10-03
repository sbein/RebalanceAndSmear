#!/usr/bin/env python3
"""Jet-only closure plots; use stored paired-seed errors and label missing object vetoes."""
import argparse
from pathlib import Path
from common import root,open_root,metadata,write_json
REGIONS=['MHT_jetOnlyHighDPhi','MHT_jetOnlyLowDPhi','SearchBins_jetOnlyHighDPhi','SearchBins_jetOnlyLowDPhi','MHT_jetOnlyHighDPhiSideband','MHT_jetOnlyLowDPhiSideband']

def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--outdir',required=True)
    args=p.parse_args();R=root();R.gStyle.SetOptStat(0);f=open_root(R,args.input);record=metadata(R,f)
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);numbers={}
    cut=record['closure_selection']['rebalanced_mht_max_GeV']
    for name in REGIONS:
        a=f.Get(name+'_observed');b=f.Get(name+'_prediction');ratio=f.Get(name+'_ratio')
        search=name.startswith('SearchBins');side='Sideband' in name;high='HighDPhi' in name
        c=R.TCanvas('legacy_'+name,'Jet-only legacy closure',1600 if search else 950,850)
        top=R.TPad('top','',0,.3,1,1);bot=R.TPad('bot','',0,0,1,.3)
        top.SetBottomMargin(.02);top.SetTopMargin(.24);bot.SetTopMargin(.03);bot.SetBottomMargin(.3)
        top.Draw();bot.Draw();top.cd();top.SetLogy();a.SetTitle('');a.SetMarkerStyle(20);a.SetMarkerSize(.5 if search else 1)
        a.GetYaxis().SetTitle('Cross section [pb / bin]');a.GetXaxis().SetLabelSize(0);a.GetXaxis().SetTitleSize(0)
        b.SetLineColor(R.kAzure+2);b.SetFillColorAlpha(R.kAzure+1,.3)
        maximum=max(a.GetMaximum(),b.GetMaximum(),1.e-5);a.SetMinimum(max(1.e-9,maximum*1.e-5));a.SetMaximum(maximum*20)
        upper=a.GetXaxis().GetXmax() if search else (400 if side else 1500)
        lower=.5 if search else (200 if side else 250)
        a.GetXaxis().SetRangeUser(lower,upper)
        a.Draw('E1');b.Draw('E2 SAME');b.Draw('HIST SAME');a.Draw('E1 SAME')
        leg=R.TLegend(.64,.58,.89,.75);leg.SetBorderSize(0);leg.AddEntry(a,'Held-out reco QCD','pe');leg.AddEntry(b,'Rebalance + smear','lf');leg.Draw()
        txt=R.TLatex();txt.SetNDC();txt.SetTextFont(42);txt.SetTextSize(.026)
        txt.DrawLatex(.12,.965,'2024 NanoAODv15 QCD HT1200-1500; held-out split')
        txt.DrawLatex(.12,.921,('High' if high else 'Low')+' #Delta#phi; '+('174 SUS-19-006 bins' if search else ('250 #leq MHT #leq 300 GeV sideband' if side else 'MHT #geq 300 GeV'))+f'; rebalanced MHT < {cut:g} GeV')
        txt.DrawLatex(.12,.877,'Jet-only: central #Delta#phi, MHT < HT, Andrews HT-ratio filter')
        txt.DrawLatex(.12,.833,'Lepton/photon/isolated-track vetoes pending; seed errors only')
        bot.cd();ratio.SetTitle('');ratio.GetYaxis().SetTitle('R&S / reco');ratio.GetXaxis().SetTitle('SUS-19-006 bin number' if search else 'MHT [GeV]')
        visible=[(ratio.GetBinContent(i),ratio.GetBinError(i)) for i in range(1,a.GetNbinsX()+1) if a.GetBinContent(i)>0 and a.GetBinLowEdge(i)<upper]
        ratio.SetMinimum(min([0.]+[1.1*(v-e) for v,e in visible]));ratio.SetMaximum(max([2.5]+[1.1*(v+e) for v,e in visible]))
        for axis in [ratio.GetXaxis(),ratio.GetYaxis()]:axis.SetTitleSize(.1);axis.SetLabelSize(.08)
        ratio.GetYaxis().SetTitleOffset(.45);ratio.GetXaxis().SetRangeUser(lower,upper);ratio.Draw('AXIS')
        points=R.TGraphErrors()
        for i in range(1,a.GetNbinsX()+1):
            if a.GetBinContent(i)<=0:continue
            j=points.GetN();points.SetPoint(j,a.GetBinCenter(i),ratio.GetBinContent(i));points.SetPointError(j,a.GetBinWidth(i)/2,ratio.GetBinError(i))
        points.SetMarkerStyle(20);points.SetMarkerSize(.5 if search else 1);points.SetMarkerColor(R.kAzure+2);points.Draw('P SAME')
        line=R.TLine(lower,1,upper,1);line.SetLineStyle(2);line.Draw();c.cd();c.SaveAs(str(out/(name+'.png')))
        numbers[name]=[dict(bin=i,low=a.GetBinLowEdge(i),high=a.GetBinLowEdge(i+1),observed_pb=a.GetBinContent(i),predicted_pb=b.GetBinContent(i),observed_error_pb=a.GetBinError(i),predicted_error_pb=b.GetBinError(i),ratio=ratio.GetBinContent(i) if a.GetBinContent(i)>0 else None,ratio_error=ratio.GetBinError(i) if a.GetBinContent(i)>0 else None) for i in range(1,a.GetNbinsX()+1)]
    write_json(out/'bins.json',numbers);f.Close()
if __name__=='__main__':main()
