#ifndef RUN3_LEGACY_JET_SELECTION_H
#define RUN3_LEGACY_JET_SELECTION_H
#include <array>
#include "SearchBins2018.h"


bool Run3PassAndrewsTightHtRatio(double dphi1,double ht5,double ht) {
  if(ht==0) return true;
  if(ht5/ht>1.2 && dphi1<5.3*ht5/ht-4.78) return false;
  return true;
}
bool Run3AcceptRebalancedSeed(bool fit,double mht,double maximum) {

  return fit && std::isfinite(mht) && mht<maximum;
}
bool Run3AcceptSmearedMht(double mht,double maximum) {

  return std::isfinite(mht) && mht<=maximum;
}
struct Run3LegacyJetFeatures {
  double ht,ht5,mht;
  int nj,nb;
  std::array<double,4> dphi{{99,99,99,99}};
  explicit Run3LegacyJetFeatures(const vector<UsefulJet> &jets,const TLorentzVector &fixed=TLorentzVector()) {
    ht=getHT(jets,30);ht5=getHT(jets,30,5);nj=countJets(jets,30);nb=countBJets_Useful(jets,30);
    auto recoil=getMHT(jets,30);recoil-=fixed;mht=recoil.Pt();

    vector<const UsefulJet*> central;
    for(const auto &j:jets) if(j.Pt()>30 && fabs(j.Eta())<2.4) central.push_back(&j);
    sort(central.begin(),central.end(),[](const auto *a,const auto *b){return a->Pt()>b->Pt();});
    for(unsigned int i=0;i<std::min(size_t(4),central.size());++i) dphi[i]=fabs(central[i]->tlv.DeltaPhi(recoil));
  }
  bool highDeltaPhi() const {
    const double limits[4]={.5,.5,.3,.3};
    for(int i=0;i<std::min(4,nj);++i) if(dphi[i]<limits[i]) return false;
    return true;
  }
  double minDeltaPhi() const {
    double result=99;
    for(int i=0;i<std::min(4,nj);++i) result=std::min(result,dphi[i]);
    return result;
  }
  bool highMinDeltaPhi(double commonCut=-1) const {
    return commonCut<0 ? highDeltaPhi() : minDeltaPhi()>=commonCut;
  }
  bool inclusiveDiagnostic() const {
    return std::isfinite(ht) && std::isfinite(mht) && ht>300 && nj>=2;
  }
  bool common() const {
    return std::isfinite(ht) && std::isfinite(mht) && ht>=300 && nj>=2 && mht<ht &&
      Run3PassAndrewsTightHtRatio(dphi[0],ht5,ht);
  }
  bool highRegion() const { return common() && mht>=300 && highDeltaPhi(); }
  bool lowRegion() const { return common() && mht>=300 && ht5/ht<=2 && !highDeltaPhi(); }
  bool sideband(bool high) const { return common() && mht>=250 && mht<=300 && ht5/ht<=2 && highDeltaPhi()==high; }
  int searchBin() const { return Run3SearchBinNumber2018(ht,mht,nj,nb); }
};


struct Run3ClosurePair {
  TH1D observed,prediction,cross,ratio;
  vector<double> contributions,variance;
  int observedBin=-1;
  double observedWeight=0;
  Run3ClosurePair(const string &name,const vector<double> &edges):
    observed((name+"_observed").c_str(),"Jet-only observed",edges.size()-1,edges.data()),
    prediction((name+"_prediction").c_str(),"Jet-only R&S",edges.size()-1,edges.data()),
    cross((name+"_cross_covariance").c_str(),"Paired seed covariance",edges.size()-1,edges.data()),
    ratio((name+"_ratio").c_str(),"R&S / observed",edges.size()-1,edges.data()),
    contributions(edges.size()+1,0),variance(edges.size()+1,0) {
    observed.Sumw2();prediction.Sumw2();cross.Sumw2();ratio.Sumw2();
  }
  void beginSeed() { std::fill(contributions.begin(),contributions.end(),0);observedBin=-1;observedWeight=0; }
  void fillObserved(double value,double weight) { observed.Fill(value,weight);observedBin=observed.FindBin(value);observedWeight=weight; }
  void fillPrediction(double value,double weight) { prediction.Fill(value,weight);contributions[prediction.FindBin(value)]+=weight; }
  void endSeed() {
    for(unsigned int i=0;i<contributions.size();++i) {
      variance[i]+=contributions[i]*contributions[i];
      if(int(i)==observedBin) cross.AddBinContent(i,observedWeight*contributions[i]);
    }
  }
  void write() {
    for(unsigned int i=0;i<variance.size();++i) prediction.SetBinError(i,sqrt(variance[i]));
    for(int i=1;i<=observed.GetNbinsX();++i) {
      double t=observed.GetBinContent(i),p=prediction.GetBinContent(i);
      if(t==0) continue;
      double r=p/t;
      double v=variance[i]+r*r*pow(observed.GetBinError(i),2)-2*r*cross.GetBinContent(i);
      ratio.SetBinContent(i,r);ratio.SetBinError(i,sqrt(std::max(0.,v))/fabs(t));
    }
    for(auto *h:{&observed,&prediction,&cross,&ratio}) h->Write();
  }
};
#endif
