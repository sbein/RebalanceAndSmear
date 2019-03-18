from ROOT import *

zjetsversion = ''
zjetsversion = 'ZJets'

f16 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MC2016.root')
f17 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MC2017.root')
keys = f16.GetListOfKeys()
f2 = TFile('Vault/NonQcd'+zjetsversion+'_signalSideband_MCRun2.root','recreate')
for key in keys:
    name = key.GetName()
    hr2 = f16.Get(name)
    lumi16 = 35.9
    lumi17 = 100.7
    lumir2 = lumi16+lumi17
    hr2.Scale(lumi16/lumir2)
    hr2.Add(f17.Get(name),lumi17/lumir2)
    f2.cd()
    hr2.Write()
print 'just created', f2.GetName()
f2.Close()
f16.Close()
f17.Close()


f16 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MC2016.root')
f17 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MC2017.root')
keys = f16.GetListOfKeys()
f2 = TFile('Vault/NonQcd'+zjetsversion+'_LDP_MCRun2.root','recreate')
for key in keys:
    name = key.GetName()
    hr2 = f16.Get(name)
    lumi16 = 35.9
    lumi17 = 100.7
    lumir2 = lumi16+lumi17
    hr2.Scale(lumi16/lumir2)
    hr2.Add(f17.Get(name),lumi17/lumir2)
    f2.cd()
    hr2.Write()

print 'just created', f2.GetName()
f2.Close()
f16.Close()
f17.Close()
