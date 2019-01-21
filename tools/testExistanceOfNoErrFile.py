from glob import glob
import os

counter = 0
shlist = glob('jobs/RebalanceAndSmear-Run2017B-31Mar2018*.sh')
for shfile in shlist:
    errfilename = shfile.replace('.sh','.err')
    if not os.path.exists(errfilename):
        counter+=1
        print 'missing', errfilename, '!'

print 'found', counter, 'missing files'
