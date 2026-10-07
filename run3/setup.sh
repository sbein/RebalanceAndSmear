#!/usr/bin/env bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
_rands_cmssw="${RANDS_CMSSW:-/cvmfs/cms.cern.ch/el9_amd64_gcc12/cms/cmssw/CMSSW_15_0_9}"
eval "$(cd "$_rands_cmssw/src" && scram runtime -sh)"
unset _rands_cmssw
export X509_USER_PROXY="${X509_USER_PROXY:-/uscms/home/$USER/x509up_u$(id -u)}"
export XRD_REQUESTTIMEOUT=45
