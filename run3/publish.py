#!/usr/bin/env python3
import argparse,subprocess,sys
from pathlib import Path
from common import BASE

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    p.add_argument('--host');args=p.parse_args();source=Path(args.source).resolve()
    subprocess.run([sys.executable,str(BASE/'gallery.py'),'--root',str(source)],check=True)
    target=(args.host+':' if args.host else '')+args.destination.rstrip('/')+'/'
    subprocess.run(['rsync','-a',str(source)+'/',target],check=True)

if __name__=='__main__':main()
