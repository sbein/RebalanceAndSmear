#ifndef RUN3_NANO_READER_H
#define RUN3_NANO_READER_H
#include <TFile.h>
#include <TTree.h>
#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>
#include <memory>
#include <stdexcept>
#include <algorithm>
using namespace std;
#include "../src/UsefulJet.h"
#include "BayesRandSRun3.h"
#include "EventCleaning.h"

struct Run3NanoReader {
  unique_ptr<TFile> file;
  TTree *tree;
  TTreeReader reader;
  TTreeReaderArray<Float_t> pt, eta, phi, mass, btag, nhf, nef, chf, cef, muf;
  TTreeReaderArray<UChar_t> nch, nneutral, nconst;
  TTreeReaderArray<Short_t> genidx;
  TTreeReaderArray<Float_t> gpt, geta, gphi, gmass;
  TTreeReaderValue<ULong64_t> event;
  TTreeReaderValue<UInt_t> run, lumi;
  TTreeReaderValue<Float_t> genweight;
  vector<unique_ptr<TTreeReaderValue<Bool_t>>> filters;
  vector<UsefulJet> jets, genjets;
  vector<TLorentzVector> fixedObjects;
  TLorentzVector fixedSum;
  unique_ptr<TTreeReaderArray<Float_t>> photonPt,photonEta,photonPhi;
  unique_ptr<TTreeReaderArray<UChar_t>> photonID;
  unique_ptr<TTreeReaderValue<UChar_t>> goodVertices;
  unique_ptr<TTreeReaderValue<Float_t>> pfmetPt,pfmetPhi,calometPt;
  bool analysisCleaning=false;
  vector<int> indices;
  double tagcut;
  Long64_t seen=0;
  Long64_t afterFilters=0, afterJetID=0, afterVeto=0;
  Long64_t afterVertex=0,afterHighMETMuon=0,afterHighMETNeutral=0,afterPFCalo=0;
  vector<Long64_t> flagFailed, flagCumulative;
  Run3NanoReader(const string &path, const string &tagbranch, double cut,
                const vector<string> &filterNames,bool fixedPhotons=false,bool cleanAnalysis=false):
    file(TFile::Open(path.c_str())),
    tree(file && !file->IsZombie() ? dynamic_cast<TTree*>(file->Get("Events")):nullptr),
    reader(tree),
    pt(reader,"Jet_pt"),eta(reader,"Jet_eta"),phi(reader,"Jet_phi"),mass(reader,"Jet_mass"),
    btag(reader,tagbranch.c_str()),nhf(reader,"Jet_neHEF"),nef(reader,"Jet_neEmEF"),chf(reader,"Jet_chHEF"),
    cef(reader,"Jet_chEmEF"),muf(reader,"Jet_muEF"),
    nch(reader,"Jet_chMultiplicity"),nneutral(reader,"Jet_neMultiplicity"),nconst(reader,"Jet_nConstituents"),
    genidx(reader,"Jet_genJetIdx"),
    gpt(reader,"GenJet_pt"),geta(reader,"GenJet_eta"),gphi(reader,"GenJet_phi"),gmass(reader,"GenJet_mass"),
    event(reader,"event"),run(reader,"run"),lumi(reader,"luminosityBlock"),
    genweight(reader,"genWeight"),tagcut(cut) {
    if (!tree) throw runtime_error("Missing Events tree: "+path);
    analysisCleaning=cleanAnalysis;
    if(analysisCleaning) {
      for(const auto &b:{"PV_npvsGood","PFMET_pt","PFMET_phi","CaloMET_pt"})
        if(!tree->GetBranch(b))throw runtime_error(string("Missing analysis-cleaning branch: ")+b);
      goodVertices=make_unique<TTreeReaderValue<UChar_t>>(reader,"PV_npvsGood");
      pfmetPt=make_unique<TTreeReaderValue<Float_t>>(reader,"PFMET_pt");
      pfmetPhi=make_unique<TTreeReaderValue<Float_t>>(reader,"PFMET_phi");
      calometPt=make_unique<TTreeReaderValue<Float_t>>(reader,"CaloMET_pt");
    }
    if(fixedPhotons) {
      for(const auto &b:{"Photon_pt","Photon_eta","Photon_phi","Photon_cutBased"})
        if(!tree->GetBranch(b))throw runtime_error(string("Missing photon branch: ")+b);
      photonPt=make_unique<TTreeReaderArray<Float_t>>(reader,"Photon_pt");
      photonEta=make_unique<TTreeReaderArray<Float_t>>(reader,"Photon_eta");
      photonPhi=make_unique<TTreeReaderArray<Float_t>>(reader,"Photon_phi");
      photonID=make_unique<TTreeReaderArray<UChar_t>>(reader,"Photon_cutBased");
    }
    for (auto &name:filterNames) {
      if (!tree->GetBranch(name.c_str())) throw runtime_error("Missing required filter "+name);
      filters.push_back(make_unique<TTreeReaderValue<Bool_t>>(reader,name.c_str()));
    }
    flagFailed.resize(filters.size(),0); flagCumulative.resize(filters.size(),0);
  }
  bool next() {
    if (!reader.Next()) {
      if (reader.GetEntryStatus()!=TTreeReader::kEntryBeyondEnd)
        throw runtime_error("NanoAOD read failed (check branch types or XRootD)");
      return false;
    }
    ++seen;
    return true;
  }
  bool selected() {
    bool pass=true;
    for(unsigned int i=0;i<filters.size();++i) {
      if(!**filters[i]) {++flagFailed[i];pass=false;}
      if(pass) ++flagCumulative[i];
    }
    if(!pass) return false;
    ++afterFilters;
    if(analysisCleaning && **goodVertices==0) return false;
    ++afterVertex;
    if(analysisCleaning && !Run3PassAnalysisJetID(pt,eta,chf,nhf,cef,nef,muf,nch,nneutral,true)) return false;
    fixedObjects.clear();fixedSum=TLorentzVector();
    if(photonPt)for(unsigned int i=0;i<photonPt->GetSize();++i) {
      if((*photonPt)[i]<=20 || fabs((*photonEta)[i])>=2.4 || (*photonID)[i]<2)continue;
      TLorentzVector v;v.SetPtEtaPhiM((*photonPt)[i],(*photonEta)[i],(*photonPhi)[i],0);
      fixedObjects.push_back(v);fixedSum+=v;
    }
    vector<bool> removed(pt.GetSize(),false);vector<int> matches(fixedObjects.size(),0);
    for(unsigned int i=0;i<pt.GetSize();++i) {
      if(pt[i]<=15 || fabs(eta[i])>=5 || fixedObjects.empty())continue;
      TLorentzVector v;v.SetPtEtaPhiM(pt[i],eta[i],phi[i],mass[i]);
      double dr=.5;int closest=-1;
      for(unsigned int j=0;j<fixedObjects.size();++j)
        if(v.DeltaR(fixedObjects[j])<dr){dr=v.DeltaR(fixedObjects[j]);closest=j;}
      if(closest>=0) {
        if(dr>=.4)return false;
        removed[i]=true;++matches[closest];
      }
    }
    if(any_of(matches.begin(),matches.end(),[](int n){return n!=1;}))return false;
    for(unsigned int i=0;i<pt.GetSize();++i)
      if(!analysisCleaning && !removed[i] && pt[i]>30 && fabs(eta[i])<5 && !Run3AnalysisJetID(eta[i],chf[i],nhf[i],cef[i],nef[i],muf[i],nch[i],nneutral[i])) return false;
    ++afterJetID;
    if(analysisCleaning && !Run3PassQCDHighMETMuon(pt,phi,muf,**pfmetPhi)) return false;
    ++afterHighMETMuon;
    if(analysisCleaning && !Run3PassQCDHighMETNeutral(pt,phi,nef,**pfmetPhi)) return false;
    ++afterHighMETNeutral;
    if(analysisCleaning && !Run3PassPFCaloMET(**pfmetPt,**calometPt)) return false;
    ++afterPFCalo;
    for(unsigned int i=0;i<pt.GetSize();++i)
      if(!removed[i] && Run3VetoEligible(pt[i],eta[i],chf[i],nhf[i],cef[i],nef[i],muf[i],nch[i],nneutral[i]) && Run3InVetoMap(eta[i],phi[i])) return false;
    ++afterVeto;
    jets.clear(); genjets.clear(); indices.clear();

    for (unsigned int i=0;i<pt.GetSize();++i) {
      if (fabs(eta[i])>=5 || pt[i]<=15 || removed[i]) continue;
      TLorentzVector v; v.SetPtEtaPhiM(pt[i],eta[i],phi[i],mass[i]);

      jets.emplace_back(v,fabs(eta[i])<2.4 && btag[i]>tagcut ? 1.0:0.0,pt[i]);
      indices.push_back(i);
    }
    vector<pair<UsefulJet,int>> ordered;
    for (unsigned int i=0;i<jets.size();++i) ordered.push_back({jets[i],indices[i]});
    sort(ordered.begin(),ordered.end(),[](auto &a,auto &b){return a.first.Pt()>b.first.Pt();});
    for (unsigned int i=0;i<ordered.size();++i) {jets[i]=ordered[i].first; indices[i]=ordered[i].second;}
    for (unsigned int i=0;i<gpt.GetSize();++i) {
      if (fabs(geta[i])>=5) continue;
      TLorentzVector v; v.SetPtEtaPhiM(gpt[i],geta[i],gphi[i],gmass[i]);
      if(any_of(fixedObjects.begin(),fixedObjects.end(),[&](const auto &o){return v.DeltaR(o)<.1;}))continue;
      double score=0;
      for (unsigned int j=0;j<jets.size();++j)
        if (genidx[indices[j]]==int(i) && jets[j].DeltaR(v)<0.4) {score=jets[j].csv; break;}
      genjets.emplace_back(v,score,gpt[i]);
    }
    sort(genjets.begin(),genjets.end());
    SetRun3FixedObjects(fixedSum);
    return jets.size()>=2;
  }
  ULong64_t splitKey() {

    ULong64_t x=*event ^ (ULong64_t(*run)<<32) ^ (ULong64_t(*lumi)<<16);
    x ^= x>>30; x *= 0xbf58476d1ce4e5b9ULL;
    x ^= x>>27; x *= 0x94d049bb133111ebULL;
    return x ^ (x>>31);
  }
  vector<double> response(unsigned int ig) {
    auto &g=genjets.at(ig);
    double sumg=0; for (auto &other:genjets) if(other.Pt()>2 && other.DeltaR(g)<0.7) sumg+=other.Pt();
    if (sumg<=0 || g.Pt()/sumg<=0.98) return {};
    int match=-1; double mindr=0.4;
    for (unsigned int ir=0;ir<jets.size();++ir) {
      double dr=jets[ir].DeltaR(g);
      if(dr<mindr) {mindr=dr; match=ir;}
    }
    if(match<0) return {};
    auto &r=jets[match];
    double sumr=0; for(auto &other:jets) if(other.DeltaR(r)<0.7) sumr+=other.Pt();
    if (r.Pt()/sumr<=0.98) return {};
    return {r.Pt()/g.Pt(),r.csv};
  }
};
#endif
