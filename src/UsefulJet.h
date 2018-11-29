#ifndef USEFULJET_H
#define USEFULJET_H

#include <cmath>
#include <vector>
#include <iostream>
#include <stdlib.h>
#include "TMinuit.h"
#include "TLorentzVector.h"
#include "TF1.h"
#include "TH1F.h"
#include "TGraph.h"

//using namespace std;

double BTAG_CSV = 0.8484;

struct UsefulJet
{ 
  TLorentzVector tlv;
  double csv;
  double originalPt;
  bool operator < (const UsefulJet& jet) const 
  {
    return (tlv.Pt() > jet.tlv.Pt());
  }
  UsefulJet& operator+=(const UsefulJet& other)
  {
    tlv += other.tlv;
    return *this;
  }
  UsefulJet& operator-=(const UsefulJet& other)
  {
    tlv -= other.tlv;
    return *this;
  }
  UsefulJet& operator*=(const double multiplier)
  {
    tlv *= multiplier;
    return *this;
  }
  UsefulJet& operator+=(const TLorentzVector& other)
  {
    tlv += other;
    return *this;
  }
  UsefulJet& operator-=(const TLorentzVector& other)
  {
    tlv -= other;
    return *this;
  }
UsefulJet(TLorentzVector tlv_ = TLorentzVector(), double csv_ = 0, double originalPt_=0) :
  tlv(tlv_), csv(csv_), originalPt(originalPt_) {}
  double Pt() const{return tlv.Pt();}
  double Px() const{return tlv.Px();}
  double Py() const{return tlv.Py();}
  double Pz() const{return tlv.Pz();}
  double Eta()const{return tlv.Eta();}
  double Phi() const{return tlv.Phi();}
  double E() const{return tlv.E();}
  double Csv() const{return csv;}
  double OriginalPt() const{return originalPt;}
  UsefulJet Clone()
  {
    UsefulJet newjet(tlv, csv, originalPt);
    return newjet;
  }
  double DeltaR(const UsefulJet& other)
  {
    return tlv.DeltaR(other.tlv);
  }
  double DeltaR(const TLorentzVector& other)
  {
    return tlv.DeltaR(other);
  }
  double DeltaPhi(const UsefulJet& other)
  {
    return tlv.DeltaPhi(other.tlv);
  }
  double DeltaPhi(const TLorentzVector& other)
  {
    return tlv.DeltaPhi(other);
  }

};


struct TemplateSet
{ 
 
  
  TH1F * hPtTemplate;
  TH1F * hEtaTemplate;
  TH1F * hHtTemplate;

  std::vector<std::vector<std::vector<TH1F*>>> ResponseHistos;
  std::vector<std::vector<std::vector<TGraph*>>> ResponseFunctions;
  std::vector<TGraph*> gGenMhtPtTemplatesB0, gGenMhtPtTemplatesB1, gGenMhtPtTemplatesB2, gGenMhtPtTemplatesB3;
  std::vector<TGraph*> gGenMhtDPhiTemplatesB0, gGenMhtDPhiTemplatesB1, gGenMhtDPhiTemplatesB2, gGenMhtDPhiTemplatesB3;
				    
  double rebThresh;
  double lhdMhtThresh;
  std::vector<UsefulJet> untouchedJets;

  int nparams;
  std::vector<UsefulJet> dynamicJets;

  TemplateSet() {}
};

UsefulJet operator+(UsefulJet first, const UsefulJet& second){
  first += second; // implement in terms of mutating operator
  return first; // NRVO (or move-construct)
}

UsefulJet operator-(UsefulJet first, // parameter as value, move-construct (or elide)
		    const UsefulJet& second) 
{
  first -= second; // implement in terms of mutating operator
  return first; // NRVO (or move-construct)
}

UsefulJet operator+(UsefulJet first, // parameter as value, move-construct (or elide)
		    const TLorentzVector& second) 
{
  first += second; // implement in terms of mutating operator
  return first; // NRVO (or move-construct)
}

UsefulJet operator-(UsefulJet first, // parameter as value, move-construct (or elide)
		    const TLorentzVector& second) 
{
  first -= second; // implement in terms of mutating operator
  return first; // NRVO (or move-construct)
}


std::vector<UsefulJet> CreateUsefulJetVector(std::vector<TLorentzVector> tlvVec, std::vector<double> csvVec){
  if (tlvVec.size()!=csvVec.size()) cout << "warning, size issue!" << endl;
  std::vector<UsefulJet> usefulJetVector;
  for (unsigned int i = 0; i< tlvVec.size(); i++)
    {
      if (!(fabs(tlvVec[i].Eta())<5)) continue;
      UsefulJet jet = UsefulJet(tlvVec[i], csvVec[i], tlvVec[i].Pt());
      usefulJetVector.push_back(jet);
    }
  return usefulJetVector;
}


std::vector<UsefulJet> RemoveUnmatchedJets(std::vector<UsefulJet> uRecVec, std::vector<UsefulJet> uGenVec){
  std::vector<UsefulJet> usefulJetVector;
  for (unsigned int ir = 0; ir< uRecVec.size(); ir++)
    {
      bool matched = false;
      for (unsigned int ig = 0; ig< uGenVec.size(); ig++)
	{    
	  if (uRecVec[ir].tlv.DeltaR(uGenVec[ig].tlv)<0.5)
	    {
	      matched = true;
	      break;
	    }
	}
      if(!(matched)) continue;
      usefulJetVector.push_back(uRecVec[ir]);
    }
  return usefulJetVector;
}

std::vector<UsefulJet> VetoOnUnmatchedJets(std::vector<UsefulJet> uRecVec, std::vector<UsefulJet> uGenVec){
  std::vector<UsefulJet> usefulJetVector;
  for (unsigned int ir = 0; ir< uRecVec.size(); ir++)
    {
      bool matched = false;
      if (uRecVec[ir].Pt()>30)
	{
	  for (unsigned int ig = 0; ig< uGenVec.size(); ig++)
	    {    
	      if (uRecVec[ir].tlv.DeltaR(uGenVec[ig].tlv)<0.5)
		{
		  matched = true;
		  break;
		}
	    }
	}
      else matched = true;
      if(!(matched)) {	
      std::vector<UsefulJet> emptyVec;
      return emptyVec;
      }
      usefulJetVector.push_back(uRecVec[ir]);
    }
  return usefulJetVector;
}

std::vector<UsefulJet> VetoOnUnmatchedJets100(std::vector<UsefulJet> uRecVec, std::vector<UsefulJet> uGenVec){
  std::vector<UsefulJet> usefulJetVector;
  for (unsigned int ir = 0; ir< uRecVec.size(); ir++)
    {
      bool matched = false;
      if (uRecVec[ir].Pt()>100)
	{
	  for (unsigned int ig = 0; ig< uGenVec.size(); ig++)
	    {    
	      if (uRecVec[ir].tlv.DeltaR(uGenVec[ig].tlv)<0.5)
		{
		  matched = true;
		  break;
		}
	    }
	}
      else matched = true;
      if(!(matched)) {	
      std::vector<UsefulJet> emptyVec;
      return emptyVec;
      }
      usefulJetVector.push_back(uRecVec[ir]);
    }
  return usefulJetVector;
}


int getAverageCsv(std::vector<UsefulJet> jets, double thresh){
  int njets = 0;
  double csv_ave = 0;
  for (unsigned int j=0; j<jets.size(); j++){
    if (!(jets[j].Pt()>thresh)) continue;
    if (!(abs(jets[j].Eta())<2.4)) continue;
    njets+=1;
    csv_ave+=jets[j].csv;
  }
  return csv_ave/njets;
}

std::vector<UsefulJet> CreateUsefulJetVector(std::vector<TLorentzVector> tlvVec){
  std::vector<UsefulJet> usefulJetVector;
  for (unsigned int i = 0; i< tlvVec.size(); i++)
    {
      if (!(tlvVec[i].Pt()>2)) continue;
      if (!(fabs(tlvVec[i].Eta())<5)) continue;
      UsefulJet jet = UsefulJet(tlvVec[i], 0, tlvVec[i].Pt());
      usefulJetVector.push_back(jet);
    }
  return usefulJetVector;
}

bool functionForMaxElement(UsefulJet i, UsefulJet j) { return i.Pt() < j.Pt(); }//This needs to be there


int countJets(std::vector<UsefulJet> jets, double thresh){
  int count = 0;
  for (unsigned int j=0; j<jets.size(); j++){
    if (!(jets[j].Pt()>thresh)) continue;
    if (!(abs(jets[j].Eta())<2.4)) continue;
    count+=1;
  }
  return count;
}

double JET_PT_THRESH = 30;
double lhdMhtThresh = 15;

TLorentzVector getMHT(std::vector<UsefulJet> jets, double thresh)
{
  TLorentzVector mhtvec;
  for(unsigned int i=0; i < jets.size(); i++)
    {
      if (! (jets.at(i).Pt()>thresh)) continue;
      if (! (abs(jets.at(i).Eta())<5.0)) continue;
      mhtvec-=jets.at(i).tlv;
    }
  return mhtvec;
}   

double getHT(std::vector<UsefulJet> jets, double thresh, double etathresh=2.4){
  double ht = 0;
  for(unsigned int i=0; i < jets.size(); i++){
    if (!(abs(jets.at(i).Eta())<etathresh)) continue;
    if (!(jets.at(i).Pt()>thresh)) continue;
    ht+=jets.at(i).Pt();
  }
  return ht;
}

double getHT(std::vector<TLorentzVector> jets, double thresh, double etathresh = 2.4){
  double ht = 0;
  for(unsigned int i=0; i < jets.size(); i++){
    if (!(abs(jets.at(i).Eta())<etathresh)) continue;
    if (!(jets.at(i).Pt()>thresh)) continue;
    ht+=jets.at(i).Pt();
  }
  return ht;
}

int countBJets_Useful(std::vector<UsefulJet> jets, double thresh){
  int count = 0;
  for (unsigned int j=0; j<jets.size(); j++){
    if (!(jets.at(j).Pt()>thresh)) continue;
    if (!(abs(jets.at(j).Eta())<2.4)) continue;;
    if (!(jets.at(j).csv>BTAG_CSV)) continue;
    count+=1;
  }
  return count;
}

TLorentzVector redoMET(TLorentzVector originalMet, std::vector<UsefulJet> originalJets, std::vector<UsefulJet> newJets){
  if (!(originalJets.size()==newJets.size())) {cout << "mismatch" << endl;}
  TLorentzVector newMET; newMET.SetPtEtaPhiE(originalMet.Pt(),0,originalMet.Phi(),originalMet.Pt());
  for(unsigned int i=0; i < originalJets.size(); i++)
    newMET+=originalJets[i].tlv;
  for(unsigned int i=0; i < newJets.size(); i++)
    newMET+=newJets[i].tlv;
  return newMET;
}
TLorentzVector redoMET(TLorentzVector originalMet, std::vector<TLorentzVector> originalJets, std::vector<TLorentzVector> newJets){
  if (!(originalJets.size()==newJets.size())) {cout << "mismatch" << endl;}
  TLorentzVector newMET; newMET.SetPtEtaPhiE(originalMet.Pt(),0,originalMet.Phi(),originalMet.Pt());
  for(unsigned int i=0; i < originalJets.size(); i++)
    newMET+=originalJets[i];
  for(unsigned int i=0; i < newJets.size(); i++)
    newMET+=newJets[i];
  return newMET;
}

std::vector<UsefulJet> ConcatenateVectors(std::vector<UsefulJet> a, std::vector<UsefulJet> b)
{
  std::vector<UsefulJet> jetvec = a;
  for (unsigned int i = 0; i< b.size(); i++) {
    jetvec.push_back(b[i]);
  }
  return jetvec;
}

#endif
