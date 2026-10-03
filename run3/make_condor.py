#!/usr/bin/env python3
"""Prepare one template job per NanoAOD file; submit only after reviewing the JDL."""
import argparse
import json
import shlex
from pathlib import Path
from common import BASE,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",required=True)
    p.add_argument("--outdir",default="run3_work/condor")
    p.add_argument("--max-events-per-file",type=int,default=-1)
    args=p.parse_args();manifest=json.loads(Path(args.manifest).read_text())
    jobs=Path(args.outdir).resolve();jobs.mkdir(parents=True,exist_ok=True)
    code=BASE.parent.resolve()
    queue=[]
    for s in manifest["samples"]:
        for file in s["files"]:
            i=len(queue);job=jobs/f"{i:05d}";job.mkdir(exist_ok=False)
            write_json(job/"manifest.json",dict(manifest,samples=[dict(s,files=[file])]))
            script=job/"run.sh"
            script.write_text("#!/usr/bin/env bash\nset -euo pipefail\ncd "+shlex.quote(str(code))+
                "\nsource run3/setup.sh\npython3 -u run3/response_maker.py --manifest "+
                shlex.quote(str(job/"manifest.json"))+" --output-dir "+shlex.quote(str(job/"raw"))+
                " --max-events-per-file "+str(args.max_events_per_file)+"\n")
            script.chmod(0o755)
            queue.append(str(script))
    (jobs/"workers.txt").write_text("\n".join(queue)+"\n")
    (jobs/"templates.jdl").write_text(
        "universe = vanilla\nexecutable = $(worker)\ngetenv = True\n"
        "request_cpus = 1\nrequest_memory = 2500MB\nrequest_disk = 2GB\n"
        "should_transfer_files = NO\nuse_x509userproxy = True\n"
        f"output = {jobs}/$(Cluster).$(Process).out\n"
        f"error = {jobs}/$(Cluster).$(Process).err\n"
        f"log = {jobs}/$(Cluster).log\n"
        f"queue worker from {jobs}/workers.txt\n")
    print("Prepared",len(queue),"jobs; review",jobs/"templates.jdl")
    print("Merge with: python3 run3/articulate_splines.py --inputs "+
          shlex.quote(str(jobs/"*"/"raw"/"*.root"))+" --output run3_work/templates_production.root")

if __name__=="__main__":main()
