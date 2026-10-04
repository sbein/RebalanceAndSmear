#!/usr/bin/env python3
"""Plot reco, R&S and legacy generator smearing with paired-seed ratio errors."""
import argparse
from pathlib import Path
from common import root,open_root,metadata,write_json
from plot_legacy_closure import REGIONS
OBSERVABLES=['MHT','MHT_full','HT','NJets','BTags','DPhi1','MinDPhi']
LABELS={'Inclusive':'Inclusive','HighMinDPhi':'High Min Dphi','LowMinDPhi':'Low Min Dphi (inverted selection)'}

def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--outdir',required=True)
    p.add_argument('--region',choices=list(LABELS)+['Legacy'],default='Inclusive')
    p.add_argument('--pdf',action='store_true',help='Also export PDFs for the standard plotting entry point')
    args=p.parse_args();R=root();R.gStyle.SetOptStat(0);f=open_root(R,args.input);meta=metadata(R,f)
    out=Path(args.outdir);out.mkdir(parents=True,exist_ok=True);numbers={}
    cut=meta['closure_selection']['rebalanced_mht_max_GeV'];gen_cut=meta['gen_smearing']['seed_mht_max_GeV']
    if not meta['gen_smearing']['enabled']:raise ValueError('No generator-smear prediction in this file')
    for plot in REGIONS if args.region=='Legacy' else OBSERVABLES:
        observable='MHT' if plot=='MHT_full' else plot
        prefix=plot if args.region=='Legacy' else observable+'_'+args.region
        a=f.Get(prefix+'_observed');b=f.Get(prefix+'_prediction');g=f.Get(prefix+'_genSmear_prediction')
        rb=f.Get(prefix+'_ratio');rg=f.Get(prefix+'_genSmear_ratio')
        if not all([a,b,g,rb,rg]):raise ValueError('Missing three-method histograms: '+prefix)
        search=prefix.startswith('SearchBins');side='Sideband' in prefix
        c=R.TCanvas('three_'+prefix,'Three-method closure',1600 if search else 1000,850)
        top=R.TPad('top','',0,.3,1,1);bot=R.TPad('bot','',0,0,1,.3)
        top.SetBottomMargin(.02);top.SetTopMargin(.25);bot.SetTopMargin(.03);bot.SetBottomMargin(.3)
        top.Draw();bot.Draw();top.cd();top.SetLogy();a.SetTitle('');a.SetMarkerStyle(20);a.SetMarkerSize(.5 if search else 1)
        a.GetYaxis().SetTitle('Cross section [pb / bin]');a.GetXaxis().SetLabelSize(0);a.GetXaxis().SetTitleSize(0)
        b.SetLineColor(R.kAzure+2);b.SetFillColorAlpha(R.kAzure+1,.25)
        g.SetLineColor(R.kGreen+2);g.SetFillColorAlpha(R.kGreen+1,.16);g.SetLineWidth(2)
        maximum=max(a.GetMaximum(),b.GetMaximum(),g.GetMaximum(),1.e-5)
        a.SetMinimum(max(1.e-9,maximum*1.e-5));a.SetMaximum(maximum*20)
        lower=a.GetXaxis().GetXmin();upper=a.GetXaxis().GetXmax()
        if args.region=='Legacy' and not search:lower=200 if side else 250;upper=400 if side else 1500
        elif plot=='MHT':upper=1000
        a.GetXaxis().SetRangeUser(lower,upper)
        a.Draw('E1');b.Draw('E2 SAME');b.Draw('HIST SAME');g.Draw('E2 SAME');g.Draw('HIST SAME');a.Draw('E1 SAME')
        leg=R.TLegend(.58,.51,.9,.73);leg.SetBorderSize(0)
        leg.AddEntry(a,'Held-out reco QCD','pe');leg.AddEntry(b,'Rebalance + smear','lf');leg.AddEntry(g,'Gen + smear (no rebalancing)','lf');leg.Draw()
        txt=R.TLatex();txt.SetNDC();txt.SetTextFont(42);txt.SetTextSize(.025)
        txt.DrawLatex(.12,.965,'2024 NanoAODv15 QCD HT1200-1500; held-out split')
        label=LABELS.get(args.region,prefix.replace('_',' '))
        txt.DrawLatex(.12,.921,label+f'; reb MHT < {cut:g} GeV; gen MHT < {gen_cut:g} GeV')
        txt.DrawLatex(.12,.877,'Legacy jet-region cuts' if args.region=='Legacy' else 'HT >300, N_{jets} #geq2; no MHT or HT-ratio cut')
        txt.DrawLatex(.12,.833,'Paired seed errors; template uncertainty and analysis object vetoes pending')
        bot.cd();rb.SetTitle('');rb.GetYaxis().SetTitle('Prediction / reco')
        title='SUS-19-006 bin number' if search else ('MHT [GeV]' if prefix.startswith('MHT') else observable+(' [GeV]' if observable=='HT' else (' [rad]' if 'DPhi' in observable else '')))
        rb.GetXaxis().SetTitle(title)
        visible=[(r.GetBinContent(i),r.GetBinError(i)) for r in [rb,rg] for i in range(1,a.GetNbinsX()+1) if a.GetBinContent(i)>0 and a.GetBinLowEdge(i)<upper]
        rb.SetMinimum(min([0.]+[1.1*(v-e) for v,e in visible]));rb.SetMaximum(max([2.5]+[1.1*(v+e) for v,e in visible]))
        for axis in [rb.GetXaxis(),rb.GetYaxis()]:axis.SetTitleSize(.1);axis.SetLabelSize(.08)
        rb.GetYaxis().SetTitleOffset(.45);rb.GetXaxis().SetRangeUser(lower,upper);rb.Draw('AXIS')
        points=[]
        for r,color,marker in [(rb,R.kAzure+2,20),(rg,R.kGreen+2,24)]:
            graph=R.TGraphErrors()
            for i in range(1,a.GetNbinsX()+1):
                if a.GetBinContent(i)<=0:continue
                j=graph.GetN();graph.SetPoint(j,a.GetBinCenter(i),r.GetBinContent(i));graph.SetPointError(j,a.GetBinWidth(i)/2,r.GetBinError(i))
            graph.SetMarkerStyle(marker);graph.SetMarkerSize(.5 if search else 1);graph.SetMarkerColor(color);graph.SetLineColor(color);graph.Draw('P SAME');points.append(graph)
        line=R.TLine(lower,1,upper,1);line.SetLineStyle(2);line.Draw();c.cd();c.SaveAs(str(out/(plot+'.png')))
        if args.pdf:c.SaveAs(str(out/(plot+'.pdf')))
        numbers[prefix]=[dict(bin=i,low=a.GetBinLowEdge(i),high=a.GetBinLowEdge(i+1),observed_pb=a.GetBinContent(i),predicted_pb=b.GetBinContent(i),gensmear_pb=g.GetBinContent(i),observed_error_pb=a.GetBinError(i),predicted_error_pb=b.GetBinError(i),gensmear_error_pb=g.GetBinError(i),ratio=rb.GetBinContent(i) if a.GetBinContent(i)>0 else None,ratio_error=rb.GetBinError(i) if a.GetBinContent(i)>0 else None,gensmear_ratio=rg.GetBinContent(i) if a.GetBinContent(i)>0 else None,gensmear_ratio_error=rg.GetBinError(i) if a.GetBinContent(i)>0 else None) for i in range(1,a.GetNbinsX()+1)]
    write_json(out/'bins.json',numbers);f.Close()
if __name__=='__main__':main()
