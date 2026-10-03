#ifndef RUN3_EVENT_CLEANING_H
#define RUN3_EVENT_CLEANING_H
#include <correction.h>
#include <cmath>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

// Payloads are loaded once. All event-level work remains in compiled C++.
std::unique_ptr<correction::CorrectionSet> Run3JetIDSet, Run3VetoSet;
correction::Correction::Ref Run3TightCorrection, Run3LepVetoCorrection, Run3VetoCorrection;
std::string Run3VetoType;
bool Run3IsData=false;
std::map<unsigned int,std::vector<std::pair<unsigned int,unsigned int>>> Run3LumiRanges;

void ConfigureRun3Cleaning(const std::string &idpath,const std::string &vetopath,
                          const std::string &vetoname,const std::string &vetotype) {
  Run3JetIDSet=correction::CorrectionSet::from_file(idpath);
  Run3VetoSet=correction::CorrectionSet::from_file(vetopath);
  Run3TightCorrection=Run3JetIDSet->at("AK4PUPPI_Tight");
  Run3LepVetoCorrection=Run3JetIDSet->at("AK4PUPPI_TightLeptonVeto");
  Run3VetoCorrection=Run3VetoSet->at(vetoname);
  Run3VetoType=vetotype;
}

bool Run3JetID(double eta,double chf,double nhf,double cef,double nef,double muf,
               int nch,int nneutral,bool lepVeto=false) {
  auto c=lepVeto ? Run3LepVetoCorrection : Run3TightCorrection;
  if (!c) throw std::runtime_error("ConfigureRun3Cleaning must run before event selection");
  return c->evaluate({eta,chf,nhf,cef,nef,muf,nch,nneutral,nch+nneutral})>0.5;
}

bool Run3InVetoMap(double eta,double phi) {
  if (!Run3VetoCorrection) throw std::runtime_error("Missing jet-veto correction");
  const double pi=std::acos(-1.0);
  phi=std::remainder(phi,2*pi);
  if(phi>=pi) phi=std::nextafter(pi,0.0);
  return Run3VetoCorrection->evaluate({Run3VetoType,eta,phi})!=0;
}

// Working phase-space choice: stored jets pT>15, |eta|<5, TightLeptonVeto ID,
// and electromagnetic fraction <0.9. Reject the event, never remove its recoil jet.
bool Run3VetoEligible(double pt,double eta,double chf,double nhf,double cef,
                      double nef,double muf,int nch,int nneutral) {
  return pt>15 && std::abs(eta)<5 && cef+nef<0.9 &&
         Run3JetID(eta,chf,nhf,cef,nef,muf,nch,nneutral,true);
}

void Run3ResetLumiMask(bool isData) {Run3IsData=isData; Run3LumiRanges.clear();}
void Run3AddLumi(unsigned int run,unsigned int first,unsigned int last) {
  if(first>last) throw std::runtime_error("Invalid golden JSON lumi range");
  Run3LumiRanges[run].push_back({first,last});
}
bool Run3PassLumi(unsigned int run,unsigned int lumi) {
  if(!Run3IsData) return true;
  auto it=Run3LumiRanges.find(run);
  if(it==Run3LumiRanges.end()) return false;
  for(auto range:it->second) if(lumi>=range.first && lumi<=range.second) return true;
  return false;
}

template<class F,class I>
bool Run3PassAnalysisJetID(const F &pt,const F &eta,const F &chf,const F &nhf,
                          const F &cef,const F &nef,const F &muf,const I &nch,const I &nne) {
  for(unsigned int i=0;i<pt.size();++i)
    if(pt[i]>30 && std::abs(eta[i])<5 && !Run3JetID(eta[i],chf[i],nhf[i],cef[i],nef[i],muf[i],nch[i],nne[i])) return false;
  return true;
}
template<class F,class I>
bool Run3PassVetoMap(const F &pt,const F &eta,const F &phi,const F &chf,const F &nhf,
                     const F &cef,const F &nef,const F &muf,const I &nch,const I &nne) {
  for(unsigned int i=0;i<pt.size();++i)
    if(Run3VetoEligible(pt[i],eta[i],chf[i],nhf[i],cef[i],nef[i],muf[i],nch[i],nne[i]) && Run3InVetoMap(eta[i],phi[i])) return false;
  return true;
}
#endif
