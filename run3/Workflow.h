#ifndef RUN3_WORKFLOW_H
#define RUN3_WORKFLOW_H
#include "NanoReader.h"
#include <TH1D.h>
#include <TRandom.h>
#include <TTree.h>
#include <chrono>
#include "LegacyJetSelection.h"
struct Run3RawSummary {
  Long64_t scanned=0, training=0, selected=0, responses=0, negative=0;
  double sumw=0, seconds=0;
  Long64_t after_filters=0, after_jet_id=0, after_jet_veto=0;
  vector<Long64_t> flag_failed, flag_cumulative;
};
Run3RawSummary Run3BuildRaw(const string &path, const string &tagbranch, double cut,
   const vector<string> &filters, TH1F *hp, TH1F *he, TH1F *hh,
   const vector<TH1F*> &responses, const vector<TH1F*> &priors,
   Long64_t maxEvents, int split=0) {
  auto start=chrono::steady_clock::now();
  Run3NanoReader n(path,tagbranch,cut,filters);
  Run3RawSummary out;
  while ((maxEvents<0 || out.scanned<maxEvents) && n.next()) {
    ++out.scanned;
    if (split<2 && int(n.splitKey()%2)!=split) continue;
    ++out.training; double w=*n.genweight; out.sumw+=w;
    if (w<0) ++out.negative;
    if (!n.selected()) continue;
    ++out.selected;
    for (unsigned int ig=0;ig<n.genjets.size();++ig) {
      auto &g=n.genjets[ig];
      auto pair=n.response(ig);
      if(pair.empty()) continue;
      int ip=hp->FindBin(g.Pt()), ie=he->FindBin(fabs(g.Eta()));
      if(ip<1 || ip>hp->GetNbinsX() || ie<1 || ie>he->GetNbinsX()) continue;
      int tag=pair[1]>0.5;
      responses[(tag*he->GetNbinsX()+ie-1)*hp->GetNbinsX()+ip-1]->Fill(pair[0]);
      ++out.responses;
    }
    double ht=getHT(n.genjets,30);
    int ih=hh->FindBin(ht);
    ih=std::clamp(ih,1,hh->GetNbinsX()+1);
    auto mht=getMHT(n.genjets,15);
    int nb=std::min(3,countBJets_Useful(n.jets,15));
    int ng=countJets(n.genjets,30);
    if(ng<2 || (nb==3 && ng<3)) continue;
    UsefulJet leading=n.genjets.front();
    if(nb>0) {
      auto b=find_if(n.genjets.begin(),n.genjets.end(),[](auto &j){return j.csv>0.5;});
      if(b==n.genjets.end()) continue;
      leading=*b;
    }
    int offset=(nb*(hh->GetNbinsX()+1)+ih-1)*2;
    priors[offset]->Fill(mht.Pt(),w);
    priors[offset+1]->Fill(fabs(leading.DeltaPhi(mht)),w);
  }
  out.seconds=chrono::duration<double>(chrono::steady_clock::now()-start).count();
  out.after_filters=n.afterFilters; out.after_jet_id=n.afterJetID; out.after_jet_veto=n.afterVeto;
  out.flag_failed=n.flagFailed; out.flag_cumulative=n.flagCumulative;
  return out;
}
struct Run3ClosureSummary {
  Long64_t scanned=0, validation=0, selected=0, fitted=0, accepted=0, smears=0;
  double sumw=0, seconds=0;
  Long64_t after_filters=0, after_jet_id=0, after_jet_veto=0;
  vector<Long64_t> flag_failed, flag_cumulative;
  Long64_t rejected_rebalanced_mht=0,nonfinite_rebalanced=0,rejected_smeared_mht=0,nonfinite_smears=0;
};
Run3ClosureSummary Run3Closure(const string &path,const string &tagbranch,double cut,
   const vector<string> &filters, const string &output, Long64_t maxEvents,
   int nsmears, double rebMax, unsigned int randomSeed=12345,
   bool cached=true, int split=1,double smearMax=2000,bool perSeedRandom=false) {
  if(nsmears<1) throw runtime_error("nsmears must be positive");
  Run3UseCachedSplines=cached;
  gRandom->SetSeed(randomSeed);
  SetRun3FixedObjects(TLorentzVector());
  auto start=chrono::steady_clock::now();
  Run3NanoReader n(path,tagbranch,cut,filters);
  TFile f(output.c_str(),"RECREATE");
  if(f.IsZombie()) throw runtime_error("Cannot create closure output");
  vector<double> edges={0,30,60,90,120,160,200,250,300,400,500,700,1000,1500,2500};
  TH1D truth("MHT_observed","Observed reco QCD;MHT [GeV];weighted seeds",edges.size()-1,edges.data());
  TH1D pred("MHT_prediction","R&S QCD;MHT [GeV];weighted seeds",edges.size()-1,edges.data());
  TH1D rebalanced("MHT_rebalanced","Rebalanced;MHT [GeV];weighted seeds",edges.size()-1,edges.data());
  TH1D allRebalanced("MHT_rebalanced_allFits","Successful fits before seed acceptance;MHT [GeV];weighted seeds",edges.size()-1,edges.data());
  TH1D cross("MHT_cross_covariance","sum observed * predicted per seed",edges.size()-1,edges.data());
  TH1D httruth("HT_observed","Observed;HT [GeV];weighted seeds",50,0,2500);
  TH1D htpred("HT_prediction","R&S;HT [GeV];weighted seeds",50,0,2500);
  TH1D njtruth("NJets_observed","Observed;NJets;weighted seeds",16,0,16);
  TH1D njpred("NJets_prediction","R&S;NJets;weighted seeds",16,0,16);
  TH1D nbtruth("BTags_observed","Observed;BTags;weighted seeds",5,0,5);
  TH1D nbpred("BTags_prediction","R&S;BTags;weighted seeds",5,0,5);
  TH1D hdpTruth("DPhi1_observed","Observed;DeltaPhi(j1,MHT);weighted seeds",32,0,3.2);
  TH1D hdpPred("DPhi1_prediction","R&S;DeltaPhi(j1,MHT);weighted seeds",32,0,3.2);
  for(auto h:{&truth,&pred,&rebalanced,&allRebalanced,&cross,&httruth,&htpred,&njtruth,&njpred,&nbtruth,&nbpred,&hdpTruth,&hdpPred}) h->Sumw2();
  vector<double> searchEdges;for(int i=0;i<=174;++i) searchEdges.push_back(i+.5);
  Run3ClosurePair highMht("MHT_jetOnlyHighDPhi",edges),lowMht("MHT_jetOnlyLowDPhi",edges);
  Run3ClosurePair highBins("SearchBins_jetOnlyHighDPhi",searchEdges),lowBins("SearchBins_jetOnlyLowDPhi",searchEdges);
  Run3ClosurePair highSide("MHT_jetOnlyHighDPhiSideband",edges),lowSide("MHT_jetOnlyLowDPhiSideband",edges);
  vector<Run3ClosurePair*> regions={&highMht,&lowMht,&highBins,&lowBins,&highSide,&lowSide};
  auto fillRegions=[&](const Run3LegacyJetFeatures &v,double w,bool observed) {
    auto fill=[&](Run3ClosurePair &pair,double value) { if(observed) pair.fillObserved(value,w);else pair.fillPrediction(value,w); };
    int bin=v.searchBin();
    if(v.highRegion()) {fill(highMht,v.mht);if(bin>0)fill(highBins,bin);}
    if(v.lowRegion()) {fill(lowMht,v.mht);if(bin>0)fill(lowBins,bin);}
    if(v.sideband(true))fill(highSide,v.mht);
    if(v.sideband(false))fill(lowSide,v.mht);
  };
  ULong64_t event; UInt_t run,lumi;
  double weight,ht,mht,gmht,rmht;
  int nj,nb,np,fit,accepted;
  TTree seeds("seeds","One row per selected validation seed, including failed fits");
  seeds.SetDirectory(nullptr);
  seeds.Branch("run",&run); seeds.Branch("lumi",&lumi); seeds.Branch("event",&event);
  seeds.Branch("genWeight",&weight);seeds.Branch("HT",&ht);seeds.Branch("MHT",&mht);
  seeds.Branch("GenMHT",&gmht);seeds.Branch("RebalancedMHT",&rmht);
  seeds.Branch("NJets",&nj);seeds.Branch("BTags",&nb);seeds.Branch("nparams",&np);
  seeds.Branch("fit",&fit);seeds.Branch("accepted",&accepted);
  Run3ClosureSummary out;
  vector<double> varM(truth.GetNbinsX()+2,0);
  vector<pair<TH1D*,TH1D*>> other={{&httruth,&htpred},{&njtruth,&njpred},{&nbtruth,&nbpred},{&hdpTruth,&hdpPred}};
  vector<vector<double>> vars;
  for(auto &p:other) vars.push_back(vector<double>(p.second->GetNbinsX()+2,0));
  while((maxEvents<0 || out.scanned<maxEvents) && n.next()) {
    ++out.scanned;
    if(split<2 && int(n.splitKey()%2)!=split) continue;
    ++out.validation; weight=*n.genweight; out.sumw+=weight;
    if(!n.selected()) continue;
    ++out.selected;
    event=*n.event;run=*n.run;lumi=*n.lumi;
    ht=getHT(n.jets,30);mht=getMHT(n.jets,30).Pt();
    gmht=getMHT(n.genjets,30).Pt();nj=countJets(n.jets,30);nb=countBJets_Useful(n.jets,30);
    for(auto *region:regions)region->beginSeed();
    fillRegions(Run3LegacyJetFeatures(n.jets),weight,true);
    bool baseline=ht>300 && nj>=2;
    int tb=-1;
    if(baseline) {
      truth.Fill(mht,weight);tb=truth.FindBin(mht);
      httruth.Fill(ht,weight);njtruth.Fill(nj,weight);nbtruth.Fill(nb,weight);
      auto lead=find_if(n.jets.begin(),n.jets.end(),[](auto &j){return j.Pt()>30 && fabs(j.Eta())<2.4;});
      if(lead!=n.jets.end()) hdpTruth.Fill(fabs(lead->DeltaPhi(getMHT(n.jets,30))),weight);
    }
    fit=RebalanceJets_BayesFitter(n.jets);np=_Templates_.nparams;
    rmht=getMHT(_Templates_.dynamicJets,30).Pt();
    accepted=Run3AcceptRebalancedSeed(fit,rmht,rebMax);
    if(fit) {
      ++out.fitted;
      if(!std::isfinite(rmht))++out.nonfinite_rebalanced;
      else {allRebalanced.Fill(rmht,weight);if(rmht>=rebMax)++out.rejected_rebalanced_mht;}
    }
    seeds.Fill();
    if(!accepted) continue;
    ++out.accepted;
    if(perSeedRandom) {
      // Common random draws for the same accepted seed across threshold scans.
      auto keyed=n.splitKey() ^ (ULong64_t(randomSeed)*0x9e3779b97f4a7c15ULL);
      UInt_t seed=UInt_t(keyed ^ (keyed>>32));gRandom->SetSeed(seed?seed:1);
    }
    auto balanced=_Templates_.dynamicJets;
    rebalanced.Fill(rmht,weight);
    vector<double> contrib(truth.GetNbinsX()+2,0);
    vector<vector<double>> extra;
    for(auto &p:other) extra.push_back(vector<double>(p.second->GetNbinsX()+2,0));
    for(int is=0;is<nsmears;++is) {
      // Original CMS script: "one key difference between the golden and space ages".
      auto smeared=smearJets_CC(balanced,99+_Templates_.nparams);
      ++out.smears;
      double sh=getHT(smeared,30), sm=getMHT(smeared,30).Pt();
      if(!std::isfinite(sm)) {++out.nonfinite_smears;continue;}
      if(!Run3AcceptSmearedMht(sm,smearMax)) {++out.rejected_smeared_mht;continue;}
      fillRegions(Run3LegacyJetFeatures(smeared),weight/nsmears,false);
      int sn=countJets(smeared,30), sb=countBJets_Useful(smeared,30);
      if(sh<=300 || sn<2) continue;
      double sw=weight/nsmears;
      pred.Fill(sm,sw);contrib[pred.FindBin(sm)]+=sw;
      auto lead=find_if(smeared.begin(),smeared.end(),[](auto &j){return j.Pt()>30 && fabs(j.Eta())<2.4;});
      double dphi=lead==smeared.end()?0:fabs(lead->DeltaPhi(getMHT(smeared,30)));
      vector<double> values={sh,double(sn),double(sb),dphi};
      for(unsigned int k=0;k<other.size();++k) {
        other[k].second->Fill(values[k],sw);
        extra[k][other[k].second->FindBin(values[k])]+=sw;
      }
    }
    for(unsigned int ib=0;ib<contrib.size();++ib) {
      varM[ib]+=contrib[ib]*contrib[ib];
      if(int(ib)==tb) cross.AddBinContent(ib,weight*contrib[ib]);
    }
    for(unsigned int k=0;k<other.size();++k)
      for(unsigned int ib=0;ib<extra[k].size();++ib) vars[k][ib]+=extra[k][ib]*extra[k][ib];
    for(auto *region:regions)region->endSeed();
  }
  for(unsigned int ib=0;ib<varM.size();++ib) pred.SetBinError(ib,sqrt(varM[ib]));
  for(unsigned int k=0;k<other.size();++k)
    for(unsigned int ib=0;ib<vars[k].size();++ib) other[k].second->SetBinError(ib,sqrt(vars[k][ib]));
  TH1D ratio("MHT_ratio","R&S / observed;MHT [GeV];ratio",edges.size()-1,edges.data());
  for(int ib=1;ib<=truth.GetNbinsX();++ib) {
    double t=truth.GetBinContent(ib), p=pred.GetBinContent(ib);
    if(t==0) continue;
    double r=p/t;
    double variance=pred.GetBinError(ib)*pred.GetBinError(ib)+r*r*truth.GetBinError(ib)*truth.GetBinError(ib)-2*r*cross.GetBinContent(ib);
    ratio.SetBinContent(ib,r);ratio.SetBinError(ib,sqrt(std::max(0.0,variance))/fabs(t));
  }
  for(auto h:{&truth,&pred,&rebalanced,&allRebalanced,&cross,&httruth,&htpred,&njtruth,&njpred,&nbtruth,&nbpred,&hdpTruth,&hdpPred,&ratio}) h->Write();
  for(auto *region:regions)region->write();
  seeds.Write();f.Close();
  out.seconds=chrono::duration<double>(chrono::steady_clock::now()-start).count();
  out.after_filters=n.afterFilters; out.after_jet_id=n.afterJetID; out.after_jet_veto=n.afterVeto;
  out.flag_failed=n.flagFailed; out.flag_cumulative=n.flagCumulative;
  return out;
}
#endif
