#!/usr/bin/env python3
import argparse,html,re,subprocess,sys
from pathlib import Path
from urllib.parse import quote
from common import BASE

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args()
    base=Path(args.root).resolve();directories=[base]+sorted(d for d in base.rglob('*') if d.is_dir())
    header=(BASE/'gallery_header.html').read_text()
    for directory in directories:
        if list(directory.glob('*.png')):continue
        title='Index of '+str(directory.relative_to(base.parent))
        start=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',header,flags=re.S)
        start=re.sub(r'<h1>.*?</h1>','<h1>'+html.escape(title)+'</h1>',start,flags=re.S)
        rows=['<tr><td class="name"><a href="../index.html">Parent directory</a></td></tr>'] if directory!=base else []
        rows+=['<tr><td class="name"><a href="'+quote(d.name)+'/index.html">'+html.escape(d.name)+'</a></td></tr>' for d in sorted(directory.iterdir()) if d.is_dir()]
        (directory/'index.html').write_text(start+'<table>'+''.join(rows)+'</table></div></body></html>\n')
    for directory in directories:
        if list(directory.glob('*.png')):
            subprocess.run([sys.executable,str(BASE/'whiphtml.py'),str(directory/'*.png')],check=True)
            p=directory/'index.html';s=p.read_text()
            p.write_text(re.sub(r'<P>[^\n]*','<P>'+html.escape(str(directory.relative_to(base)))+'; <a href="../index.html">parent directory</a></P>',s,count=1))

if __name__=='__main__':main()
