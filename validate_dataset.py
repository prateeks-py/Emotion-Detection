#!/usr/bin/env python3
import argparse, csv, sqlite3, json, sys
from pathlib import Path

REQUIRED = ["id","text","language","primary_emotion","secondary_emotions","emotion_intensity_1_5",
"expression_type","language_style","profanity_present","sarcasm","negation_present","sensitive_category",
"context_required","source_type","source_name","source_license","annotation_status","split"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="emotion_dataset.csv")
    p.add_argument("--db",default="emotion_dataset.sqlite")
    p.add_argument("--expected",type=int,default=10000)
    a=p.parse_args()
    errors=[]
    with open(a.csv,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != REQUIRED: errors.append(f"Unexpected CSV columns: {reader.fieldnames}")
        rows=list(reader)
    if len(rows)!=a.expected: errors.append(f"Expected {a.expected} rows, found {len(rows)}")
    ids=[r["id"] for r in rows]
    if len(set(ids))!=len(ids): errors.append("Duplicate IDs found")
    for i,r in enumerate(rows):
        if not r["text"].strip(): errors.append(f"Empty text at row {i+2}")
        try:
            secondary=json.loads(r["secondary_emotions"])
            if not isinstance(secondary,list): errors.append(f"secondary_emotions is not a JSON list at row {i+2}")
        except Exception: errors.append(f"Invalid secondary_emotions JSON at row {i+2}")
        try:
            v=int(r["emotion_intensity_1_5"])
            if not 1<=v<=5: errors.append(f"Intensity out of range at row {i+2}")
        except Exception: errors.append(f"Invalid intensity at row {i+2}")
        if r["split"] not in ("train","validation","test"): errors.append(f"Invalid split at row {i+2}")
        if r["source_type"] not in ("synthetic","public_dataset","human_annotated"): errors.append(f"Invalid source_type at row {i+2}")
    con=sqlite3.connect(a.db)
    db_count=con.execute("SELECT COUNT(*) FROM emotion_records").fetchone()[0]
    con.close()
    if db_count!=len(rows): errors.append(f"CSV rows ({len(rows)}) and SQLite rows ({db_count}) differ")
    print(json.dumps({"csv_rows":len(rows),"sqlite_rows":db_count,"source_counts":dict(__import__("collections").Counter(r["source_type"] for r in rows)),
                      "errors":errors,"valid":not errors},indent=2))
    sys.exit(1 if errors else 0)
if __name__=="__main__": main()
