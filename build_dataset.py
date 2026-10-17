#!/usr/bin/env python3
"""
Reproducible emotion dataset builder.

Default: generates 10,000 synthetic starter rows.
Optional --mixed: fetches a public multilingual emotion dataset through Hugging Face
datasets, keeps documented source metadata, and combines public rows with synthetic rows.
No real-source rows are claimed unless actually downloaded and loaded.
"""
import argparse, csv, json, random, sqlite3, hashlib
from pathlib import Path

SEED = 20261017
LANG_MAP = {
    "english":"en", "hindi":"hi", "Hindi":"hi", "hinglish":"hinglish",
    "spanish":"es", "french":"fr", "arabic":"ar", "bengali":"bn",
    "marathi":"mr", "tamil":"ta", "urdu":"ur", "portuguese":"pt",
    "german":"de", "indonesian":"id", "italian":"it", "japanese":"ja",
    "korean":"ko", "russian":"ru", "chinese":"zh"
}
def load_existing_synthetic(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def public_rows_from_hf(limit, dataset_name="Horizon-Labs/go-emotions-multilingual"):
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc
    ds = load_dataset(dataset_name, split="train")
    # Dataset card reports Apache-2.0; verify current dataset card and license before redistribution.
    label_names = [
        "admiration","amusement","anger","annoyance","approval","caring","confusion","curiosity",
        "desire","disappointment","disapproval","disgust","embarrassment","excitement","fear",
        "gratitude","grief","joy","love","nervousness","optimism","pride","realization","relief",
        "remorse","sadness","surprise","neutral"
    ]
    out=[]
    for idx, row in enumerate(ds):
        if len(out) >= limit: break
        txt = str(row.get("text","")).strip()
        if not txt: continue
        labels = row.get("labels", [])
        if isinstance(labels, int): labels=[labels]
        labels = [label_names[x] for x in labels if isinstance(x,int) and 0 <= x < len(label_names)]
        lang = str(row.get("lang", row.get("language", "unknown")))
        source_text = row.get("source_text")
        # These rows have emotion labels from the source dataset; sensitive labels are NOT inferred.
        out.append({
            "id": f"PUB{len(out)+1:06d}",
            "text": txt,
            "language": lang,
            "primary_emotion": labels[0] if labels else "unlabeled_emotion",
            "secondary_emotions": json.dumps(labels[1:], ensure_ascii=False),
            "emotion_intensity_1_5": "",
            "expression_type": "public_dataset_text",
            "language_style": "not_annotated",
            "profanity_present": "",
            "sarcasm": "unknown",
            "negation_present": "",
            "sensitive_category": "not_annotated",
            "context_required": True,
            "source_type": "public_dataset",
            "source_name": dataset_name,
            "source_license": "Apache-2.0 (verify current dataset card before redistribution)",
            "annotation_status": "source_labels; sensitive_labels_not_annotated",
            "split": "train",
            "source_text": source_text or "",
        })
    return out

def build_db(rows, db_path, schema_path):
    schema = Path(schema_path).read_text(encoding="utf-8")
    conn=sqlite3.connect(db_path)
    conn.executescript(schema)
    cols=["id","text","language","primary_emotion","secondary_emotions","emotion_intensity_1_5",
          "expression_type","language_style","profanity_present","sarcasm","negation_present",
          "sensitive_category","context_required","source_type","source_name","source_license",
          "annotation_status","split"]
    conn.execute("DELETE FROM emotion_records")
    for r in rows:
        vals=[]
        for c in cols:
            v=r.get(c,"")
            if c in ("profanity_present","negation_present","context_required"):
                v = 1 if str(v).lower() in ("true","1") else 0 if str(v).lower() in ("false","0","") else 0
            if c=="emotion_intensity_1_5" and (v=="" or v is None): v=1
            vals.append(v)
        conn.execute("INSERT OR REPLACE INTO emotion_records ("+",".join(cols)+") VALUES ("+",".join(["?"]*len(cols))+")", vals)
    conn.commit(); conn.close()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--size", type=int, default=10000)
    ap.add_argument("--mixed", action="store_true", help="Include public multilingual GoEmotions-derived records")
    ap.add_argument("--public-rows", type=int, default=7000)
    args=ap.parse_args()
    outdir=Path(args.outdir); outdir.mkdir(parents=True,exist_ok=True)
    starter=Path(__file__).with_name("emotion_dataset.csv")
    synth=load_existing_synthetic(starter)
    random.seed(SEED)
    synth = synth[:max(0,args.size)]
    rows=synth
    if args.mixed:
        public=public_rows_from_hf(min(args.public_rows,args.size))
        # Keep synthetic rows to fill the requested size. Public rows remain traceable.
        rows=public + synth[:max(0,args.size-len(public))]
    # Stable unique IDs, and explicit provenance in every record.
    for i,r in enumerate(rows,1):
        r["id"]=f"EMO{i:06d}"
        if not r.get("source_type"): r["source_type"]="synthetic"
    csv_path=outdir/"emotion_dataset.csv"
    fields=["id","text","language","primary_emotion","secondary_emotions","emotion_intensity_1_5",
            "expression_type","language_style","profanity_present","sarcasm","negation_present",
            "sensitive_category","context_required","source_type","source_name","source_license",
            "annotation_status","split"]
    with csv_path.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    schema_path=Path(__file__).with_name("schema.sql")
    build_db(rows,outdir/"emotion_dataset.sqlite",schema_path)
    # Manifest records actual provenance counts and file hashes.
    counts={}
    for r in rows: counts[r.get("source_type","unknown")]=counts.get(r.get("source_type","unknown"),0)+1
    manifest={"seed":SEED,"rows":len(rows),"source_counts":counts,"mixed_mode":args.mixed,
              "dataset_name":"Emotion lexicon starter dataset","limitations":[
                  "Synthetic records are template-generated and weakly labeled; they are not real user messages.",
                  "Public dataset rows retain source labels, but sensitive categories are not annotated by that source.",
                  "Verify current dataset license, terms, and attribution before redistribution.",
                  "Do not use this dataset alone for clinical diagnosis or high-stakes decisions."
              ]}
    (outdir/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
