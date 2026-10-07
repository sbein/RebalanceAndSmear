#!/usr/bin/env python3
import argparse
import math
from pathlib import Path
from common import root,open_root,metadata,write_json
from targetCutScan import FAMILIES

SETS = {
    'HT5overHT':['HT2','HT1p8','HT1p5','HT1p3'],
    'PFMETminusMHT':['PF100','PF80','PF60','PF40'],
    'PuppiMETminusMHT':['Puppi100','Puppi80','Puppi60','Puppi40'],
    'HT2_and_PF':['HT2_PF100','HT2_PF80','HT2_PF60','HT2_PF40'],
    'HT2_and_Puppi':['HT2_Puppi100','HT2_Puppi80','HT2_Puppi60','HT2_Puppi40'],
}

def label(spec):
    cuts=[]
    if spec['ht_max']>0:cuts.append(f"HT5/HT < {spec['ht_max']:g}")
    if spec['met_max']>0:
        met='PF' if spec['met_type']==1 else 'PUPPI'
        cuts.append(f"|{met} MET - MHT| < {spec['met_max']:g} GeV")
    return ', '.join(cuts) or 'Original reco QCD'

def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--outdir',required=True)
    a=p.parse_args();R=root();R.gStyle.SetOptStat(0);f=open_root(R,a.input);record=metadata(R,f)
    lumi=record['normalization']['luminosity_pb_inverse']/1000.
    choices={s['name']:s for s in record['variants']};out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    colors=[R.kRed+1,R.kOrange+7,R.kViolet+1,R.kCyan+2];results={}
    for family in FAMILIES:
        search=family.startswith('SearchBins');side='Sideband' in family
        if search and record['min_mht']>300:continue
        original=f.Get('Baseline__'+family);pred=f.Get(family+'_prediction');gen=f.Get(family+'_genSmear_prediction')
        lower=.5 if search else record['min_mht'];upper=174.5 if search else (400. if side else 2500.)
        start=1 if search else original.FindBin(lower)
        rows={}
        for name,spec in choices.items():
            h=f.Get(name+'__'+family)
            value=h.Integral(start,h.GetNbinsX()+1);err=math.sqrt(sum(h.GetBinError(b)**2 for b in range(start,h.GetNbinsX()+2)))
            high=h.Integral(h.FindBin(700.),h.GetNbinsX()+1) if not search else None
            ptotal=pred.Integral(start,pred.GetNbinsX()+1);gtotal=gen.Integral(start,gen.GetNbinsX()+1)
            rows[name]=dict(selection=label(spec),target=value,target_error=err,
                rands=ptotal,gen_smear=gtotal,rands_over_target=ptotal/value if value>0 else None,
                gen_over_target=gtotal/value if value>0 else None,target_mht_ge700=high,
                surviving_fraction=value/original.Integral(start,original.GetNbinsX()+1) if original.Integral(start,original.GetNbinsX()+1)>0 else None)
        results[family]=rows
        for group,names in SETS.items():
            directory=out/family/group;directory.mkdir(parents=True,exist_ok=True)
            c=R.TCanvas('target_'+family+'_'+group,'Target selection scan',1600 if search else 1100,950)
            top=R.TPad('top','',0,.30,1,1);bot=R.TPad('bot','',0,0,1,.30)
            top.SetTopMargin(.32);top.SetBottomMargin(.025);bot.SetTopMargin(.03);bot.SetBottomMargin(.3)
            top.Draw();bot.Draw();top.cd();top.SetLogy()
            base=original.Clone('base_'+group);base.SetDirectory(0);base.SetTitle('');base.SetMarkerStyle(20);base.SetMarkerSize(.5 if search else .8)
            b=pred.Clone('pred_'+group);b.SetDirectory(0);b.SetFillStyle(1001);b.SetFillColor(R.kAzure+1);b.SetLineColor(R.kAzure+2)
            g=gen.Clone('gen_'+group);g.SetDirectory(0);g.SetFillStyle(0);g.SetLineWidth(2);g.SetLineColor(R.kGreen+2)
            alternatives=[]
            for name,color in zip(names,colors):
                h=f.Get(name+'__'+family).Clone(name+'_'+group);h.SetDirectory(0);h.SetFillStyle(0);h.SetLineColor(color);h.SetLineWidth(2);alternatives.append(h)
            hs=[base,b,g]+alternatives
            visible=[h.GetBinContent(i) for h in hs for i in range(1,h.GetNbinsX()+1) if lower<=h.GetBinCenter(i)<upper and h.GetBinContent(i)>0]
            base.SetMinimum(max(1.e-9,min(visible)*.2) if visible else 1.e-9);base.SetMaximum(max(visible)*30 if visible else 1.)
            base.GetXaxis().SetRangeUser(lower,upper);base.GetXaxis().SetLabelSize(0);base.GetXaxis().SetTitleSize(0)
            base.GetYaxis().SetTitle('Expected events / bin');base.Draw('E1');b.Draw('HIST SAME');g.Draw('HIST SAME')
            for h in alternatives:h.Draw('HIST SAME')
            base.Draw('E1 SAME')
            leg=R.TLegend(.11,.73,.93,.91);leg.SetNColumns(2);leg.SetTextSize(.023);leg.SetBorderSize(0)
            leg.AddEntry(base,'Original reco QCD','pe');leg.AddEntry(b,'Frozen rebalance + smear','f');leg.AddEntry(g,'Frozen gen + smear','l')
            for name,h in zip(names,alternatives):leg.AddEntry(h,label(choices[name]),'l')
            leg.Draw();text=R.TLatex();text.SetNDC();text.SetTextFont(42);text.SetTextSize(.025)
            text.DrawLatex(.11,.962,f'2024 NanoAODv15 QCD, {lumi:g} fb^{{-1}}; '+family.replace('_',' '))
            text.DrawLatex(.11,.704,'Additional cuts on reconstructed target only; predictions unchanged')
            bot.cd();axis=base.Clone('axis_'+group);axis.Reset();axis.SetTitle('');axis.GetXaxis().SetRangeUser(lower,upper)
            axis.GetYaxis().SetTitle('R&S / target');axis.GetXaxis().SetTitle('SUS-19-006 bin number' if search else 'MHT [GeV]')
            for ax in [axis.GetXaxis(),axis.GetYaxis()]:ax.SetTitleSize(.09);ax.SetLabelSize(.075)
            axis.GetYaxis().SetTitleOffset(.5);axis.SetMinimum(0);axis.SetMaximum(2.5);axis.Draw('AXIS')
            graphs=[];ratioMaximum=2.5
            for target,color in [(base,R.kAzure+2)]+list(zip(alternatives,colors)):
                graph=R.TGraphErrors()
                for i in range(1,target.GetNbinsX()+1):
                    denominator=target.GetBinContent(i)
                    if denominator<=0:continue
                    numerator=b.GetBinContent(i);ratio=numerator/denominator
                    error=math.hypot(b.GetBinError(i)/denominator,numerator*target.GetBinError(i)/denominator**2)
                    if lower<=target.GetBinCenter(i)<upper:ratioMaximum=max(ratioMaximum,1.1*(ratio+error))
                    j=graph.GetN();graph.SetPoint(j,target.GetBinCenter(i),ratio);graph.SetPointError(j,target.GetBinWidth(i)/2,error)
                graph.SetLineColor(color);graph.SetMarkerColor(color);graph.SetMarkerStyle(20);graph.SetMarkerSize(.4 if search else .65);graph.Draw('P SAME');graphs.append(graph)
            axis.SetMaximum(ratioMaximum)
            line=R.TLine(lower,1,upper,1);line.SetLineStyle(2);line.Draw();c.cd();c.SaveAs(str(directory/'MHT.png' if not search else directory/'SearchBins.png'))
    write_json(out/'target_yields.json',dict(min_mht=record['min_mht'],results=results,
        ratios='Frozen predictions divided by the selected reconstructed target',
        ratio_errors='Uncorrelated diagnostic approximation; new paired covariance is unavailable',
        overflows='Integral summaries include overflow; displayed MHT range stops at 2500 GeV'))
    f.Close()

if __name__=='__main__':main()
