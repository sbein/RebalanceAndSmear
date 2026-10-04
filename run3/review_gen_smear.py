#!/usr/bin/env python3
"""Export five-cut, three-method closure galleries and a checked scan report."""
import argparse,json
from pathlib import Path
import subprocess
from common import BASE,root,open_root,metadata,write_json
from plot_three_method_closure import LABELS

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',default='run3_work/gen_smear_dphi20261004')
    p.add_argument('--cuts',nargs='+',type=int,default=[90,95,100]);args=p.parse_args()
    directory=Path(args.directory);R=root();R.gStyle.SetOptStat(0);files=[];report=[];previous=None
    for cut in args.cuts:
        path=directory/f'closure_rebalance{cut}.root';f=open_root(R,path);files.append(f);meta=metadata(R,f)
        data=R.RDataFrame(f.Get('seeds')).AsNumpy(['event','fit','accepted','RebalancedMHT','genAccepted'])
        if previous is not None:
            for key in ['event','fit','RebalancedMHT','genAccepted']:assert (data[key]==previous[key]).all(),key
            assert (previous['accepted']<=data['accepted']).all()
        previous=data;regions={}
        for name in LABELS:
            a=f.Get('MHT_'+name+'_observed');b=f.Get('MHT_'+name+'_prediction');g=f.Get('MHT_'+name+'_genSmear_prediction')
            regions[name]=dict(observed_pb=a.Integral(),predicted_pb=b.Integral(),gensmear_pb=g.Integral(),
                observed_seeds=int(a.GetEntries()),observed_positive_bins=sum(a.GetBinContent(i)>0 for i in range(1,a.GetNbinsX()+1)))
        report.append(dict(cut_GeV=cut,statistics=meta['statistics'],regions=regions,gen_smearing=meta['gen_smearing'],diagnostic_views=meta['diagnostic_views']))
        for region,folder in [('Inclusive','inclusive'),('HighMinDPhi','high-min-dphi'),('LowMinDPhi','low-min-dphi'),('Legacy','legacy-jet-regions')]:
            subprocess.run(['python3',str(BASE/'plot_three_method_closure.py'),str(path),'--outdir',str(directory/'plots'/f'rebalance{cut}'/folder),'--region',region],check=True)
    out=directory/'plots'/'comparisons';out.mkdir(parents=True,exist_ok=True)
    palette=[R.kOrange+7,R.kGreen+2,R.kRed+1,R.kMagenta+1,R.kBlue+1]
    for region in LABELS:
        prefix='MHT_'+region;c=R.TCanvas('scan_'+prefix,'Cut scan with generator reference',1100,800)
        c.SetTopMargin(.24);c.SetBottomMargin(.13);h=R.TH1D('frame_'+prefix,';MHT [GeV];Prediction / reco',100,0,1000)
        h.SetMinimum(0);h.SetMaximum(3);h.Draw('AXIS');leg=R.TLegend(.55,.46,.89,.76);leg.SetBorderSize(0)
        graphs=[];limits=[]
        variants=[(f,prefix+'_ratio',f'Reb MHT < {cut} GeV',palette[i],20+i,1) for i,(cut,f) in enumerate(zip(args.cuts,files))]
        variants.append((files[-1],prefix+'_genSmear_ratio','Gen-smear; gen MHT <150 GeV',R.kBlack,25,2))
        for f,key,label,color,marker,style in variants:
            a=f.Get(prefix+'_observed');ratio=f.Get(key);g=R.TGraphErrors()
            for i in range(1,a.GetNbinsX()+1):
                if a.GetBinContent(i)<=0 or a.GetBinLowEdge(i)>=1000:continue
                v,e=ratio.GetBinContent(i),ratio.GetBinError(i);j=g.GetN()
                g.SetPoint(j,a.GetBinCenter(i),v);g.SetPointError(j,a.GetBinWidth(i)/2,e);limits.append((v,e))
            g.SetMarkerStyle(marker);g.SetMarkerColor(color);g.SetLineColor(color);g.SetLineWidth(2);g.SetLineStyle(style)
            g.Draw('LP SAME');graphs.append(g);leg.AddEntry(g,label,'lp')
        h.SetMaximum(max([3.]+[1.1*(v+e) for v,e in limits]));h.SetMinimum(min([0.]+[1.1*(v-e) for v,e in limits]))
        leg.Draw();line=R.TLine(0,1,1000,1);line.SetLineStyle(2);line.Draw();t=R.TLatex();t.SetNDC();t.SetTextFont(42);t.SetTextSize(.026)
        t.DrawLatex(.1,.96,'2024 NanoAODv15 QCD HT1200-1500; '+LABELS[region])
        t.DrawLatex(.1,.916,'Legacy #Delta#phi cuts: 0.5 / 0.5 / 0.3 / 0.3; low is the logical complement')
        t.DrawLatex(.1,.872,'Common draws within each method; independent generator-smear stream')
        t.DrawLatex(.1,.828,'Paired seed errors; variants correlated; template and full-selection studies pending')
        c.SaveAs(str(out/(region+'_MHT_seed-cut-scan.png')))
    # Compare generator and rebalance seed recoils before their independent acceptance cuts.
    ref=files[-1];d=R.RDataFrame(ref.Get('seeds')).AsNumpy(['GenMHT','RebalancedMHT','fit'])
    out=directory/'plots'/'seed-diagnostics';out.mkdir(parents=True,exist_ok=True)
    gen=R.TH1D('gen_seed',';Seed MHT [GeV];Seeds / 5 GeV',100,0,500);reb=R.TH1D('reb_seed','',100,0,500)
    for gm,rm,fit in zip(d['GenMHT'],d['RebalancedMHT'],d['fit']):
        gen.Fill(float(gm))
        if fit:reb.Fill(float(rm))
    c=R.TCanvas('seed_recoils','Seed recoil comparison',1000,700);c.SetTopMargin(.2);c.SetLogy();gen.SetLineColor(R.kGreen+2);gen.SetLineWidth(2)
    reb.SetLineColor(R.kAzure+2);reb.SetLineWidth(2);gen.SetMinimum(.5);gen.SetMaximum(max(gen.GetMaximum(),reb.GetMaximum())*10)
    gen.Draw('HIST');reb.Draw('HIST SAME');leg=R.TLegend(.53,.6,.88,.8);leg.SetBorderSize(0);leg.AddEntry(gen,'Generator seeds (all selected reco events)','l');leg.AddEntry(reb,'Successful rebalanced seeds','l');leg.Draw()
    lines=[]
    for cut,color in [(95,R.kRed+1),(150,R.kGreen+2)]:
        line=R.TLine(cut,.5,cut,gen.GetMaximum());line.SetLineColor(color);line.SetLineStyle(2);line.Draw();lines.append(line)
    t=R.TLatex();t.SetNDC();t.SetTextFont(42);t.SetTextSize(.027);t.DrawLatex(.1,.95,'2024 QCD HT1200-1500; seed recoils before acceptance')
    t.DrawLatex(.1,.905,'Red: new 95 GeV R&S diagnostic; green: legacy 150 GeV generator cut')
    c.SaveAs(str(out/'GenMHT_vs_RebalancedMHT.png'))
    result=dict(cuts=report,all_seed_fits_identical=True,nested_rebalanced_acceptance=True,
        gen_smear_identical_across_rebalance_cuts=True,preferred_diagnostic_cut_GeV=95,production_seed_cut_GeV=90,historical_default_cut_GeV=160,
        definition='Inclusive HT>300, NJets>=2; high requires legacy central-jet delta-phi cuts; Low Min Dphi is the complement. No MHT or HT-ratio cut in these three views.',
        uncertainty_scope='Paired seed errors; no template uncertainty or error on differences between correlated variants.',
        training_rerun=False)
    write_json(directory/'gen_smear_scan.json',result)
    for f in files:f.Close()
    print(json.dumps([dict(cut_GeV=r['cut_GeV'],statistics=r['statistics'],regions=r['regions']) for r in report],indent=2))
if __name__=='__main__':main()
