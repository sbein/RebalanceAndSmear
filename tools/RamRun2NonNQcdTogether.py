from ROOT import *


zjetsversion = 'ZJets'
zjetsversion = ''

####This should be done to update the Run2 MC

f16 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MC2016.root')
f17 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MC2017.root')
f18 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MC2018.root')
f18.ls()

keys = f16.GetListOfKeys()
f2 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MCRun2.root','recreate')
for key in keys:
    name = key.GetName()
    if 'Hemv' in name: continue
    if 'LowDeltaPhi' in name: continue
    if 'MaxHemJet' in name: continue
    hr2 = f16.Get(name)
    lumi16 = 35.9
    lumi17 = 41.5
    lumi18 = 59.2
    lumir2 = lumi16+lumi17+lumi18
    hr2.Scale(lumi16/lumir2)
    hr2.Add(f17.Get(name),lumi17/lumir2)
    print 'trying', name
    hr2.Add(f18.Get(name),lumi18/lumir2)    
    f2.cd()
    hr2.Write()
print 'just created', f2.GetName()
f2.Close()
f16.Close()
f17.Close()


f16 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MC2016.root')
f17 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MC2017.root')
f18 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MC2018.root')
keys = f16.GetListOfKeys()
f2 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MCRun2.root','recreate')
for key in keys:
    name = key.GetName()
    if 'Hemv' in name: continue
    if 'LowDeltaPhi' in name: continue
    if 'MaxHemJet' in name: continue    
    hr2 = f16.Get(name)
    lumi16 = 35.9
    lumi17 = 41.5
    lumi18 = 59.2
    lumir2 = lumi16+lumi17+lumi18
    hr2.Scale(lumi16/lumir2)
    hr2.Add(f17.Get(name),lumi17/lumir2)
    hr2.Add(f18.Get(name),lumi18/lumir2)    
    f2.cd()
    hr2.Write()

print 'just created', f2.GetName()
f2.Close()
f16.Close()
f17.Close()
