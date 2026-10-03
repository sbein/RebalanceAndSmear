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

// DP-2024/028 tight PUPPI ID. v15 does not store Jet_jetId.
bool Run3TightID(double eta, double nhf, double nef, double chf,
                 int nch, int nneutral, int nconst) {
  double a = fabs(eta);
  if (a<=2.6) return nhf<0.99 && nef<0.90 && nconst>1 && chf>0 && nch>0;
  if (a<=2.7) return nhf<0.90 && nef<0.99;
  if (a<=3.0) return nhf<0.99;
  return nef<0.4 && nneutral>1;
}
struct Run3NanoReader {
  unique_ptr<TFile> file;
  TTree *tree;
  TTreeReader reader;
  TTreeReaderArray<Float_t> pt, eta, phi, mass, btag, nhf, nef, chf;
  TTreeReaderArray<UChar_t> nch, nneutral, nconst;
  TTreeReaderArray<Short_t> genidx;
  TTreeReaderArray<Float_t> gpt, geta, gphi, gmass;
  TTreeReaderValue<ULong64_t> event;
  TTreeReaderValue<UInt_t> run, lumi;
  TTreeReaderValue<Float_t> genweight;
  vector<unique_ptr<TTreeReaderValue<Bool_t>>> filters;
  vector<UsefulJet> jets, genjets;
  vector<int> indices;
  double tagcut;
  Long64_t seen=0;
  Run3NanoReader(const string &path, const string &tagbranch, double cut,
                const vector<string> &filterNames):
    file(TFile::Open(path.c_str())),
    tree(file && !file->IsZombie() ? dynamic_cast<TTree*>(file->Get("Events")):nullptr),
    reader(tree),
    pt(reader,"Jet_pt"),eta(reader,"Jet_eta"),phi(reader,"Jet_phi"),mass(reader,"Jet_mass"),
    btag(reader,tagbranch.c_str()),nhf(reader,"Jet_neHEF"),nef(reader,"Jet_neEmEF"),chf(reader,"Jet_chHEF"),
    nch(reader,"Jet_chMultiplicity"),nneutral(reader,"Jet_neMultiplicity"),nconst(reader,"Jet_nConstituents"),
    genidx(reader,"Jet_genJetIdx"),
    gpt(reader,"GenJet_pt"),geta(reader,"GenJet_eta"),gphi(reader,"GenJet_phi"),gmass(reader,"GenJet_mass"),
    event(reader,"event"),run(reader,"run"),lumi(reader,"luminosityBlock"),
    genweight(reader,"genWeight"),tagcut(cut) {
    if (!tree) throw runtime_error("Missing Events tree: "+path);
    for (auto &name:filterNames) {
      if (!tree->GetBranch(name.c_str())) throw runtime_error("Missing required filter "+name);
      filters.push_back(make_unique<TTreeReaderValue<Bool_t>>(reader,name.c_str()));
    }
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
    for (auto &flag:filters) if (!**flag) return false;
    jets.clear(); genjets.clear(); indices.clear();
    // Veto events with failing analysis jets; retain low-pT seed jets for migration.
    for (unsigned int i=0;i<pt.GetSize();++i) {
      if (fabs(eta[i])>=5 || pt[i]<=15) continue;
      if (pt[i]>30 && !Run3TightID(eta[i],nhf[i],nef[i],chf[i],nch[i],nneutral[i],int(nch[i])+int(nneutral[i])))
        return false;
      TLorentzVector v; v.SetPtEtaPhiM(pt[i],eta[i],phi[i],mass[i]);
      // Only central jets are b-tagged in the prior and response categories.
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
      double score=0;
      for (unsigned int j=0;j<jets.size();++j)
        if (genidx[indices[j]]==int(i) && jets[j].DeltaR(v)<0.4) {score=jets[j].csv; break;}
      genjets.emplace_back(v,score,gpt[i]);
    }
    sort(genjets.begin(),genjets.end());
    return jets.size()>=2;
  }
  ULong64_t splitKey() {
    // Stable keyed split; hashing decorrelates event-number ordering.
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
