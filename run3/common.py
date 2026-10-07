"""Shared Run 3 configuration and ROOT I/O. All physics choices are recorded."""
import json
import hashlib
from pathlib import Path
from array import array

BASE = Path(__file__).resolve().parent
_skim_dictionary_loaded=False

def config(path=None):
    cfg = json.loads(Path(path or BASE / "config_2024.json").read_text())

    supported = {"input_jet_pt":15, "prior_mht_jet_pt":15, "analysis_jet_pt":30,
                 "ht_eta":2.4, "mht_eta":5, "response_match_dr":0.4,
                 "isolation_dr":0.7, "isolation_fraction":0.98, "rebalance_mht_max":95.0}
    for key, value in supported.items():
        if cfg[key] != value:
            raise ValueError(f"{key}={cfg[key]} is not supported by this backend; edit and validate C++ too")
    if cfg["era"] != "2024":
        raise ValueError("Validate jet ID and b tagging before changing era")
    if cfg.get("additional_jec",False):
        raise ValueError("Additional JEC is not implemented in this MC pilot")
    if cfg.get("analysis_jet_id_wp","AK4PUPPI_Tight") not in ["AK4PUPPI_Tight","AK4PUPPI_TightLeptonVeto"]:
        raise ValueError("Unsupported analysis jet-ID working point")
    return cfg

def root(load_core=False):
    global _skim_dictionary_loaded
    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)
    if load_core:
        import correctionlib
        correctionlib.register_pyroot_binding()
        for library in ["libMinuit", "libTreePlayer", "libPhysics"]:
            if ROOT.gSystem.Load(library)<0:
                raise RuntimeError("Cannot load ROOT "+library)
        ROOT.gInterpreter.AddIncludePath(str(BASE.parent))
        ROOT.gInterpreter.ProcessLine(".O 2")
        if not ROOT.gInterpreter.Declare('#include "run3/Workflow.h"'):
            raise RuntimeError("Run 3 C++ compilation failed")
        ROOT.BTAG_CSV = 0.5
        if not _skim_dictionary_loaded:
            ROOT.gInterpreter.GenerateDictionary('vector<TLorentzVector>','vector;TLorentzVector.h')
            if not ROOT.TClass.GetClass('vector<TLorentzVector>').IsLoaded():
                raise RuntimeError('Cannot compile the skim four-vector dictionary')
            _skim_dictionary_loaded=True
    return ROOT

def configure_cleaning(ROOT, cfg, is_data=False, golden_json=None):
    ROOT.Run3BoundedPdf=cfg.get("spline_pdf_policy")=="bounded_nonnegative"
    for spec in [cfg["jet_id_payload"], cfg["jet_veto_payload"]]:
        path=Path(spec["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=spec["sha256"]:
            raise ValueError("Payload checksum differs from pinned configuration: "+str(path))
    ROOT.ConfigureRun3Cleaning(cfg["jet_id_payload"]["path"],cfg["jet_veto_payload"]["path"],
                              cfg["jet_veto_payload"]["name"],cfg["jet_veto_payload"]["type"],
                              cfg.get("analysis_jet_id_wp","AK4PUPPI_Tight"))
    ROOT.Run3ResetLumiMask(is_data)
    if is_data:
        if not golden_json: raise ValueError("Data requires an explicit certified golden JSON")
        for run,ranges in json.loads(Path(golden_json).read_text()).items():
            for first,last in ranges: ROOT.Run3AddLumi(int(run),first,last)
    elif golden_json:
        raise ValueError("Golden JSON is data-only; omit it for MC")

def cleaning_summary(stats, cfg, analysis=False):
    result=dict(after_filters=stats.after_filters,after_jet_id=stats.after_jet_id,after_jet_veto=stats.after_jet_veto,
                flags=[dict(name=name,failed_independently=int(stats.flag_failed[i]),
                            passed_cumulative=int(stats.flag_cumulative[i])) for i,name in enumerate(
                                cfg['analysis_cleaning']['filters'] if analysis else cfg["filters"])])
    if analysis:
        result.update({name:int(getattr(stats,name)) for name in
            ['after_vertex','after_high_met_muon','after_high_met_neutral','after_pf_calo']})
    return result

def vector(ROOT, typename, items):
    out = ROOT.std.vector(typename)()
    for item in items:
        out.push_back(item)
    return out

def axis(ROOT, name, edges):
    return ROOT.TH1F(name, name, len(edges)-1, array("d",edges))

def response_name(pt, eta, ip, ie, tag):
    return f"hRTemplate(gPt{pt[ip]:.1f}-{pt[ip+1]:.1f}, gEta{eta[ie]:.1f}-{eta[ie+1]:.1f})" + ("B" if tag else "")

def prior_name(ht, ih, tag, kind):
    low = ht[ih] if ih<len(ht) else ht[-1]
    high = ht[ih+1] if ih+1<len(ht) else ht[-1]+(ht[-1]-ht[-2])
    return f"hGenMht{kind}B{tag}(ght{low:.1f}-{high:.1f})"

def write_json(path, data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")

def metadata(ROOT, file, key="run3_metadata"):
    obj=file.Get(key)
    if not obj:
        raise ValueError(f"Missing {key} in {file.GetName()}")
    return json.loads(obj.GetString().Data())

def write_metadata(ROOT, data, key="run3_metadata"):
    ROOT.TObjString(json.dumps(data,sort_keys=True)).Write(key)

def summary(obj, fields):
    return {field:getattr(obj,field) for field in fields}

def require_compatible(record, cfg, analysis=False):
    ignored={'analysis_cleaning'} | ({'rebalance_mht_max'} if analysis else set())
    training={k:v for k,v in record.get('config',{}).items() if k not in ignored}
    requested={k:v for k,v in cfg.items() if k not in ignored}
    if training != requested:
        raise ValueError("Configuration differs from template training configuration")

def open_root(ROOT, path):
    f=ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise OSError(f"Cannot open {path}")
    return f
