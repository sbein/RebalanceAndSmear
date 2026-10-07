#!/usr/bin/env bash
_run3_setup() {
    local repo area previous root_version
    repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)" || return 1
    area="$repo/CMSSW_15_0_9"
    source /cvmfs/cms.cern.ch/cmsset_default.sh || return 1
    export SCRAM_ARCH=el9_amd64_gcc12
    if [[ ! -d "$area/.SCRAM/$SCRAM_ARCH" ]]; then
        if [[ -e "$area" ]]; then
            echo "Incomplete or incompatible CMSSW area: $area" >&2
            return 1
        fi
        (cd "$repo" && cmsrel CMSSW_15_0_9) || return 1
    fi
    previous="$PWD"
    cd "$area/src" || return 1
    cmsenv
    cd "$previous" || return 1
    if [[ "$CMSSW_VERSION" != CMSSW_15_0_9 || "$CMSSW_BASE" != "$area" ]]; then
        echo "Could not activate the local CMSSW_15_0_9 area" >&2
        return 1
    fi
    root_version="$(root-config --version)" || return 1
    if [[ "$root_version" != 6.32.13 ]]; then
        echo "Expected CMSSW ROOT 6.32.13, found $root_version" >&2
        return 1
    fi
    export X509_USER_PROXY="${X509_USER_PROXY:-/uscms/home/$USER/x509up_u$(id -u)}"
    export XRD_REQUESTTIMEOUT=45
}
_run3_setup || { unset -f _run3_setup; return 1 2>/dev/null || exit 1; }
unset -f _run3_setup
