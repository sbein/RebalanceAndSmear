
triggerIndecesV14 = {}
triggerIndecesV14['SingleEl'] = [19]
triggerIndecesV14['SingleEl45'] = [21]
triggerIndecesV14['SingleElCocktail'] = [11,12,14,15,16,18,19,20,21,22,63,64,65]
triggerIndecesV14['MhtMet6pack'] = [56,53,54,55,60,57,58,59]
triggerIndecesV14["SingleMu"] = [23,24,25,26,27]
triggerIndecesV14["SingleMuCocktail"] = [23,24,25,26,27,28,29,30,31,32]
triggerIndecesV14["SinglePho"] = [63]
triggerIndecesV14["SinglePhoWithHt"] = [63,64,65,66]
triggerIndecesV14['HtTrain'] = [38,39,42,43,45,47,48,50,51,52]

triggerIndecesV15 = {}
triggerIndecesV15['SingleEl'] = [36,39]
triggerIndecesV15['SingleEl45'] = [41]
triggerIndecesV15['SingleElCocktail'] = [21,22,23,24,26,27,30,31,32,33,36,37,40,139]
triggerIndecesV15['MhtMet6pack'] = [108,110,114,123,124,125,126,128,129,130,131,132,133,122,134]#123
triggerIndecesV15["SingleMu"] = [48,50,52,55,63]
triggerIndecesV15["SingleMuCocktail"] = [45,46,47,48,49,50,51,52,54,55,58,59,63,64,65,66]
triggerIndecesV15["SinglePho"] = [139]
triggerIndecesV15["SinglePhoWithHt"] = [138, 139,141,142,143]
triggerIndecesV15['HtTrain'] = [67,68,69,72,73,74,80,84,88,91,92,93,95,96,99,102,103,104]

triggerIndecesV16a = triggerIndecesV15

triggerIndecesV16 = {}
triggerIndecesV16['SingleEl'] = [36,39]
triggerIndecesV16['SingleEl45'] = [41]
triggerIndecesV16['SingleElCocktail'] = [21,22,23,24,26,27,30,31,32,33,36,37,40,139]
triggerIndecesV16['MhtMet6pack'] = [108,110,114,123,124,125,126,128,129,130,131,132,133,122,134]#123
triggerIndecesV16["SingleMu"] = [48,50,52,55,63]
triggerIndecesV16["SingleMuCocktail"] = [45,46,47,48,49,50,51,52,54,55,58,59,63,64,65,66]
triggerIndecesV16["SinglePho"] = [139]
triggerIndecesV16["SinglePhoWithHt"] = [138, 139,141,142,143]
triggerIndecesV16['HtTrain'] = [67,68,69,72,73,74,80,84,88,91,92,93,95,96,99,102,103,104]


regionCuts = {}
Inf = 9999
#regionCuts['Baseline']               = [[300,Inf],[300,Inf],[2,Inf],[0,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['LowDeltaPhiCR']               = [[1000,Inf],[250,300],[2,Inf],[0,Inf],[0,Inf],[0,Inf],[0,Inf],[0,Inf]]#gets help
#regionCuts['B1Baseline']               = [[300,Inf],[300,Inf],[2,Inf],[1,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
regionCuts['LowMhtBaseline']               = ([[300,Inf],[200,Inf],[6,Inf],[0,Inf],[0.0,Inf],[0.0,Inf],[0.0,Inf],[0.0,Inf]], 0)
#regionCuts['HighHtBaseline']               = [[2000,Inf],[300,Inf],[2,Inf],[0,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['BaselineBTags0']         = [[300,Inf],[300,Inf],[2,Inf],[0,0],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['BaselineBTags1']         = [[300,Inf],[300,Inf],[2,Inf],[1,1],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['BaselineBTags2-Inf']     = [[300,Inf],[300,Inf],[2,Inf],[2,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
regionCuts['LowDeltaPhi']            = ([[300,Inf],[300,Inf],[2,Inf],[0,Inf],[0,Inf],[0,Inf],[0,Inf],[0,Inf]], 0)#gets help
#regionCuts['LowMhtBaseline']            = [[500,Inf],[50,200],[4,Inf],[0,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['HighMhtBaseline']               = [[500,Inf],[300,Inf],[2,Inf],[0,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]
#regionCuts['GmsbBaseline']               = [[500,Inf],[100,Inf],[2,Inf],[0,Inf],[0.5,Inf],[0.5,Inf],[0.3,Inf],[0.3,Inf]]#photon



