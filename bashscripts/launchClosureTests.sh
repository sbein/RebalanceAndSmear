python tools/mergeHistosFinalizeWeights.py output/Summer16MiniAODv3.QCD_HT/
mv QCD.root QCD-Summer16.root
python tools/closureTests.py QCD-Summer16.root