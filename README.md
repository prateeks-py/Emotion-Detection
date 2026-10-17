# Emotion Dataset Bundle

## Included files
- `emotion_dataset.csv`: 10,000-row synthetic starter dataset (UTF-8 with BOM for spreadsheet compatibility).
- `emotion_dataset.sqlite`: SQLite database containing the same rows.
- `schema.sql`: database schema and indexes.
- `build_dataset.py`: reproducible build pipeline; can optionally ingest a public multilingual dataset.
- `requirements.txt`: dependency for optional public-source ingestion.
- `manifest.json`: row counts, provenance and limitations.
- `DATA_DICTIONARY.md`: field definitions and recommended use.

## Provenance status — important
The CSV and SQLite files included in this bundle contain **10,000 synthetic rows only**. They do not claim to contain real conversations or sourced public-dataset examples. This is deliberate: public records were not downloaded into this environment, so no real-source provenance is fabricated.

To build a mixed dataset with public source rows, use a network-enabled Python environment:
```bash
python -m pip install -r requirements.txt
python build_dataset.py --mixed --size 10000 --public-rows 7000 --outdir mixed_build
```
The pipeline uses `Horizon-Labs/go-emotions-multilingual` via Hugging Face `datasets`, with source labels retained and sensitive categories marked `not_annotated`. Review the current dataset card, license, and usage terms before redistributing the resulting data. The source dataset is described as Apache-2.0 in its current card, but always re-check.

## Reproducibility
- Random seed: `20261017`
- Synthetic template generation and labeling are deterministic.
- Default current files: synthetic-only.
- Mixed mode: public multilingual emotion records + synthetic rows to fill the target size.
- Public source labels are not equivalent to human labels for all safety categories. Sensitive categories require separate human annotation.

## Validation
Run:
```bash
python validate_dataset.py --csv emotion_dataset.csv --db emotion_dataset.sqlite
```
