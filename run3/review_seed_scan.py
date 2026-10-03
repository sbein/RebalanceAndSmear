#!/usr/bin/env python3
"""Summarize a completed common-random-number seed-cut scan and export its plots."""
import argparse
import json
from pathlib import Path
import subprocess
from common import BASE,root,open_root,metadata,write_json
from plot_legacy_closure import REGIONS

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',default='run3_work/legacy_review20261004')
    args=p.parse_args();directory=Path(args.directory);R=root();R.gStyle.SetOptStat(0)
    cuts=[90,100,120,160];files=[];report=[];previous=None;previous_fits=None
    for cut in cuts:
        path=directory/('closure_rebalance'+str(cut)+'.root');f=open_root(R,path);files.append(f);meta=metadata(R,f)
        rows=R.RDataFrame(f.Get('seeds')).AsNumpy(['event','fit','accepted','RebalancedMHT','MHT'])
        if previous is not None:
            assert (rows['event']==previous['event']).all() and (rows['fit']==previous['fit']).all()
            assert (rows['RebalancedMHT']==previous['RebalancedMHT']).all(), 'Cut changed fitted seeds'
            assert (previous['accepted']<=rows['accepted']).all(), 'Acceptance is not nested'
        previous=rows
        regions={}
        for name in REGIONS:
            a=f.Get(name+'_observed');b=f.Get(name+'_prediction')
            regions[name]=dict(observed_pb=a.Integral(),predicted_pb=b.Integral(),
                observed_seeds=int(a.GetEntries()),filled_smears=int(b.GetEntries()),
                ratio=b.Integral()/a.Integral() if a.Integral()>0 else None,
                occupied_observed_bins=sum(a.GetBinContent(i)>0 for i in range(1,a.GetNbinsX()+1)))
        report.append(dict(cut_GeV=cut,statistics=meta['statistics'],regions=regions))
        target=directory/'plots'/('rebalance'+str(cut))
        subprocess.run(['python3',str(BASE/'plot_closure_gallery.py'),str(path),'--outdir',str(target/'inclusive'),'--label',f'Rebalanced MHT < {cut} GeV; common random draws per seed'],check=True)
        subprocess.run(['python3',str(BASE/'plot_legacy_closure.py'),str(path),'--outdir',str(target/'jet-only-regions')],check=True)
    subprocess.run(['python3',str(BASE/'plot_legacy_closure.py'),str(directory/'closure_reference160.root'),'--outdir',str(directory/'plots'/'reference160-jet-only-regions')],check=True)
    out=directory/'plots'/'comparisons';out.mkdir(parents=True,exist_ok=True)
    colors=[R.kOrange+7,R.kGreen+2,R.kMagenta+1,R.kBlue+1]
    for prefix in ['MHT','MHT_jetOnlyHighDPhi','MHT_jetOnlyLowDPhi']:
        c=R.TCanvas('scan_'+prefix,'Seed threshold comparison',1100,750);c.SetTopMargin(.23);c.SetBottomMargin(.13)
        low=0 if prefix=='MHT' else 300;high=1000
        h=R.TH1D('frame_'+prefix,';MHT [GeV];R&S / reco',100,low,high);h.SetMinimum(0);h.SetMaximum(3);h.Draw('AXIS')
        leg=R.TLegend(.59,.55,.89,.76);leg.SetBorderSize(0);graphs=[];limits=[]
        for j,(cut,f) in enumerate(zip(cuts,files)):
            a=f.Get(prefix+'_observed');ratio=f.Get(prefix+'_ratio');g=R.TGraphErrors()
            for i in range(1,a.GetNbinsX()+1):
                if a.GetBinContent(i)<=0 or a.GetBinLowEdge(i)>=high:continue
                v,e=ratio.GetBinContent(i),ratio.GetBinError(i);n=g.GetN()
                g.SetPoint(n,a.GetBinCenter(i),v);g.SetPointError(n,a.GetBinWidth(i)/2,e);limits.append((v,e))
            g.SetMarkerColor(colors[j]);g.SetLineColor(colors[j]);g.SetMarkerStyle(20+j);g.SetLineWidth(2);g.Draw('LP SAME');graphs.append(g)
            leg.AddEntry(g,f'Rebalanced MHT < {cut} GeV','lp')
        h.SetMaximum(max([3.]+[1.1*(v+e) for v,e in limits]));h.SetMinimum(min([0.]+[1.1*(v-e) for v,e in limits]))
        leg.Draw();line=R.TLine(low,1,high,1);line.SetLineStyle(2);line.Draw();t=R.TLatex();t.SetNDC();t.SetTextSize(.027)
        t.DrawLatex(.1,.95,'2024 NanoAODv15 QCD HT1200-1500; held-out split')
        t.DrawLatex(.1,.907,'Inclusive pilot' if prefix=='MHT' else ('Jet-only high #Delta#phi' if 'High' in prefix else 'Jet-only low #Delta#phi'))
        t.DrawLatex(.1,.864,'Same random draws per seed; correlated variants; individual paired-seed errors')
        t.DrawLatex(.1,.821,'Template uncertainty excluded; lepton/photon/isolated-track vetoes pending')
        c.SaveAs(str(out/(prefix+'_seed-cut-scan.png')))
    ref=files[-1];data=R.RDataFrame(ref.Get('seeds')).AsNumpy(['fit','RebalancedMHT','MHT'])
    diagnostics=directory/'plots'/'seed-diagnostics';diagnostics.mkdir(parents=True,exist_ok=True)
    h=R.TH1D('successful_rebalanced',';Rebalanced MHT [GeV];Successful fits / 5 GeV',100,0,500)
    scatter=R.TH2D('recoil_scatter',';Seed reco MHT [GeV];Rebalanced MHT [GeV]',100,0,1500,100,0,500)
    for fit,rmht,mht in zip(data['fit'],data['RebalancedMHT'],data['MHT']):
        if fit:h.Fill(float(rmht));scatter.Fill(float(mht),float(rmht))
    for plot,hist in [('RebalancedMHT_successful-fits',h),('SeedMHT_vs_RebalancedMHT',scatter)]:
        c=R.TCanvas('diagnostic_'+plot,'Rebalanced seed diagnostics',1000,750);c.SetTopMargin(.19)
        if hist==h:c.SetLogy();h.SetMinimum(.5);h.SetMaximum(max(h.GetMaximum(),1)*5);h.Draw('HIST')
        else:c.SetLogz();scatter.Draw('COLZ')
        t=R.TLatex();t.SetNDC();t.SetTextSize(.029);t.DrawLatex(.1,.95,'2024 NanoAODv15 QCD HT1200-1500; successful fits before seed cut')
        t.DrawLatex(.1,.905,'Reference acceptance remains fit success and rebalanced MHT < 160 GeV')
        lines=[];leg=R.TLegend(.6,.61,.87,.79);leg.SetBorderSize(0)
        for cut,color in zip(cuts,colors):
            line=R.TLine(cut,.5,cut,h.GetMaximum()) if hist==h else R.TLine(0,cut,1500,cut)
            line.SetLineColor(color);line.SetLineStyle(2);line.SetLineWidth(2);line.Draw();lines.append(line)
            leg.AddEntry(line,f'{cut} GeV seed cut','l')
        leg.Draw()
        c.SaveAs(str(diagnostics/(plot+'.png')))
    result=dict(cuts=report,all_seeds_and_fits_identical=True,nested_accepted_seed_sets=True,
        reference_cut_GeV=160,training_rerun=False,reason='Closure selections only; training PDFs unchanged',
        statistics_scope='Paired seed errors per bin; no template uncertainty; variants correlated. Integrated regional ratios have no assigned uncertainty.',
        selection_scope='Jet-only diagnostics, not the full SUS-19-006 SR selection')
    write_json(directory/'seed_cut_scan.json',result)
    for f in files:f.Close()
    print(json.dumps([dict(cut_GeV=r['cut_GeV'],accepted=r['statistics']['accepted'],regions=r['regions']) for r in report],indent=2))
if __name__=='__main__':main()
