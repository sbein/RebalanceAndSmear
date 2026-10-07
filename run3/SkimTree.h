#ifndef RUN3_SKIM_TREE_H
#define RUN3_SKIM_TREE_H
struct Run3SkimTree {
  TTree tree{"RandS","Observed, rebalanced and smeared NanoAOD events"};
  ULong64_t event;UInt_t run,lumi;
  int isRandS,nsmears,fit,nj,nb;
  double ht,hardMet,hardMetPhi,fraction;
  vector<TLorentzVector> jets,rebalanced,fixed;
  vector<float> btags;
  Run3SkimTree() {
    tree.SetDirectory(nullptr);
    tree.Branch("run",&run);tree.Branch("luminosityBlock",&lumi);tree.Branch("event",&event);
    tree.Branch("IsRandS",&isRandS);tree.Branch("NSmearsPerEvent",&nsmears);tree.Branch("FitSucceed",&fit);
    tree.Branch("HT",&ht);tree.Branch("HardMETPt",&hardMet);tree.Branch("HardMETPhi",&hardMetPhi);
    tree.Branch("NJets",&nj);tree.Branch("BTags",&nb);tree.Branch("SmearFraction",&fraction);
    tree.Branch("Jets",&jets);tree.Branch("Jets_btag",&btags);
    tree.Branch("JetsRebalanced",&rebalanced);tree.Branch("FixedObjects",&fixed);
  }
  void fill(Run3NanoReader &n,const vector<UsefulJet> &objects,const vector<UsefulJet> &balanced,
            int method,int smears,int fitStatus) {
    run=*n.run;lumi=*n.lumi;event=*n.event;isRandS=method;nsmears=smears;fit=fitStatus;
    fraction=method==0?1.:1./smears;jets.clear();btags.clear();rebalanced.clear();fixed=n.fixedObjects;
    for(const auto &j:objects){jets.push_back(j.tlv);btags.push_back(j.csv);}
    for(const auto &j:balanced)rebalanced.push_back(j.tlv);
    Run3LegacyJetFeatures v(objects,n.fixedSum);ht=v.ht;hardMet=v.mht;nj=v.nj;nb=v.nb;
    hardMetPhi=(getMHT(objects,30)-n.fixedSum).Phi();tree.Fill();
  }
};
void Run3WeightSkim(TTree *tree,double scale) {
  double fraction,weight;
  tree->SetBranchAddress("SmearFraction",&fraction);
  auto input=tree->GetBranch("SmearFraction");
  auto output=tree->Branch("EventWeight",&weight,"EventWeight/D");
  for(Long64_t i=0;i<tree->GetEntries();++i){input->GetEntry(i);weight=fraction*scale;output->Fill();}
  tree->ResetBranchAddresses();tree->Write("RandS",TObject::kOverwrite);
}
#endif
