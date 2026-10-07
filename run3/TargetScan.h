#ifndef RUN3_TARGET_SCAN_H
#define RUN3_TARGET_SCAN_H
#include "Workflow.h"
#include "TargetCuts.h"

struct Run3TargetVariant {
  string name;
  double htMaximum,metMaximum;
  int metType;
};
struct Run3TargetSummary {
  Long64_t scanned=0,candidates=0,selected=0;
};
bool Run3TargetQuality(Run3NanoReader &n) {
  for(auto &flag:n.filters)if(!**flag)return false;
  if(**n.goodVertices==0)return false;
  if(!Run3PassAnalysisJetID(n.pt,n.eta,n.chf,n.nhf,n.cef,n.nef,n.muf,n.nch,n.nneutral,true))return false;
  if(!Run3PassQCDHighMETMuon(n.pt,n.phi,n.muf,**n.pfmetPhi) ||
     !Run3PassQCDHighMETNeutral(n.pt,n.phi,n.nef,**n.pfmetPhi) ||
     !Run3PassPFCaloMET(**n.pfmetPt,**n.calometPt))return false;
  for(unsigned int i=0;i<n.pt.GetSize();++i)
    if(Run3VetoEligible(n.pt[i],n.eta[i],n.chf[i],n.nhf[i],n.cef[i],n.nef[i],n.muf[i],n.nch[i],n.nneutral[i]) && Run3InVetoMap(n.eta[i],n.phi[i]))return false;
  return true;
}
Run3TargetSummary Run3TargetScan(const string &input,const string &output,const string &tagbranch,
  double tagcut,const vector<string> &filters,const vector<Run3TargetVariant> &variants,
  double minimumMht=250,Long64_t maxEvents=-1) {
  Run3NanoReader n(input,tagbranch,tagcut,filters,false,true);
  TTreeReaderValue<Float_t> puppi(n.reader,"PuppiMET_pt");
  if(!n.tree->GetBranch("PuppiMET_pt"))throw runtime_error("Missing PuppiMET_pt");
  TFile file(output.c_str(),"RECREATE");if(file.IsZombie())throw runtime_error("Cannot create target scan");
  vector<double> mhtEdges={0,30,60,90,120,160,200,250,300,400,500,700,1000,1500,2500};
  vector<double> searchEdges;for(int i=0;i<=174;++i)searchEdges.push_back(i+.5);
  vector<string> names={"MHT_Inclusive","MHT_HighMinDPhi","MHT_LowMinDPhi",
    "MHT_jetOnlyHighDPhi","MHT_jetOnlyLowDPhi","MHT_jetOnlyHighDPhiSideband",
    "MHT_jetOnlyLowDPhiSideband","SearchBins_jetOnlyHighDPhi","SearchBins_jetOnlyLowDPhi"};
  map<string,unique_ptr<TH1D>> histograms;
  for(const auto &variant:variants)for(const auto &name:names) {
    const auto &edges=name.find("SearchBins")==0?searchEdges:mhtEdges;
    string key=variant.name+"__"+name;
    histograms[key]=make_unique<TH1D>(key.c_str(),"Target-only selection",edges.size()-1,edges.data());
    histograms[key]->Sumw2();histograms[key]->SetDirectory(nullptr);
  }
  ULong64_t event;UInt_t run,lumi;double ht,ht5,mht,pfmet,puppimet,dphi1;
  int nj,nb;bool high,legacyHigh,legacyLow;
  TTree targets("targets","Selected reconstructed targets for cut diagnostics");targets.SetDirectory(nullptr);
  targets.Branch("event",&event);targets.Branch("run",&run);targets.Branch("luminosityBlock",&lumi);
  targets.Branch("HT",&ht);targets.Branch("HT5",&ht5);targets.Branch("MHT",&mht);
  targets.Branch("PFMET",&pfmet);targets.Branch("PuppiMET",&puppimet);targets.Branch("DeltaPhi1",&dphi1);
  targets.Branch("NJets",&nj);targets.Branch("BTags",&nb);targets.Branch("HighMinDPhi",&high);
  targets.Branch("LegacyHigh",&legacyHigh);targets.Branch("LegacyLow",&legacyLow);
  Run3TargetSummary summary;
  while((maxEvents<0 || summary.scanned<maxEvents) && n.next()) {
    ++summary.scanned;
    vector<UsefulJet> jets;
    for(unsigned int i=0;i<n.pt.GetSize();++i) {
      if(n.pt[i]<=15 || fabs(n.eta[i])>=5)continue;
      TLorentzVector p;p.SetPtEtaPhiM(n.pt[i],n.eta[i],n.phi[i],n.mass[i]);
      jets.emplace_back(p,fabs(n.eta[i])<2.4 && n.btag[i]>tagcut?1.:0.,n.pt[i]);
    }
    sort(jets.begin(),jets.end(),[](const auto &a,const auto &b){return a.Pt()>b.Pt();});
    Run3LegacyJetFeatures v(jets);
    if(!std::isfinite(v.mht) || !std::isfinite(v.ht) || v.ht<300 || v.nj<2 || v.mht<minimumMht)continue;
    ++summary.candidates;if(!Run3TargetQuality(n))continue;
    ++summary.selected;event=*n.event;run=*n.run;lumi=*n.lumi;
    ht=v.ht;ht5=v.ht5;mht=v.mht;pfmet=**n.pfmetPt;puppimet=*puppi;nj=v.nj;nb=v.nb;
    high=v.highDeltaPhi();legacyHigh=v.highRegion();legacyLow=v.lowRegion();dphi1=v.dphi[0];targets.Fill();
    for(const auto &variant:variants) {
      if(variant.htMaximum>0 && !Run3TargetHtRatio(ht5,ht,variant.htMaximum))continue;
      if(variant.metMaximum>0 && !Run3TargetMetConsistency(variant.metType==1?pfmet:puppimet,mht,variant.metMaximum))continue;
      auto fill=[&](const string &name,double x){histograms.at(variant.name+"__"+name)->Fill(x);};
      if(v.inclusiveDiagnostic()) {fill("MHT_Inclusive",mht);fill(high?"MHT_HighMinDPhi":"MHT_LowMinDPhi",mht);}
      int bin=v.searchBin();
      if(legacyHigh) {fill("MHT_jetOnlyHighDPhi",mht);if(bin>0)fill("SearchBins_jetOnlyHighDPhi",bin);}
      if(legacyLow) {fill("MHT_jetOnlyLowDPhi",mht);if(bin>0)fill("SearchBins_jetOnlyLowDPhi",bin);}
      if(v.sideband(true))fill("MHT_jetOnlyHighDPhiSideband",mht);
      if(v.sideband(false))fill("MHT_jetOnlyLowDPhiSideband",mht);
    }
  }
  file.cd();for(auto &h:histograms)h.second->Write();targets.Write();
  TTree count("tCount","Uncut encountered source events");count.SetEntries(summary.scanned);count.Write();file.Close();
  return summary;
}
#endif
