#!/usr/bin/env python3
"""Export authoritative branch types and built-in documentation from an actual NanoAOD file."""
import argparse
from common import root, open_root, write_json


def main():
    p=argparse.ArgumentParser();p.add_argument("--nano",required=True);p.add_argument("--output",required=True)
    args=p.parse_args();R=root();f=open_root(R,args.nano);t=f.Get("Events")
    if not t:raise ValueError("Missing Events tree")
    branches={}
    for b in t.GetListOfBranches():
        branches[b.GetName()]=dict(documentation=b.GetTitle(),
                 leaves=[dict(name=l.GetName(),type=l.GetTypeName(),counter=l.GetLeafCount().GetName() if l.GetLeafCount() else None)
                         for l in b.GetListOfLeaves()])
    write_json(args.output,dict(input=args.nano,entries=int(t.GetEntries()),branches=branches,
               interpretation="Built-in branch documentation from this file; describes content, not POG analysis recommendations"))
    print(len(branches),"branches; Jet_jetId present:","Jet_jetId" in branches)
    f.Close()


if __name__=="__main__":main()
