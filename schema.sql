PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS emotion_records (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    language TEXT NOT NULL,
    primary_emotion TEXT NOT NULL,
    secondary_emotions TEXT NOT NULL DEFAULT '[]',
    emotion_intensity_1_5 INTEGER NOT NULL CHECK (emotion_intensity_1_5 BETWEEN 1 AND 5),
    expression_type TEXT NOT NULL,
    language_style TEXT NOT NULL,
    profanity_present INTEGER NOT NULL CHECK (profanity_present IN (0,1)),
    sarcasm TEXT NOT NULL,
    negation_present INTEGER NOT NULL CHECK (negation_present IN (0,1)),
    sensitive_category TEXT NOT NULL,
    context_required INTEGER NOT NULL CHECK (context_required IN (0,1)),
    source_type TEXT NOT NULL CHECK (source_type IN ('synthetic','public_dataset','human_annotated')),
    source_name TEXT NOT NULL,
    source_license TEXT NOT NULL,
    annotation_status TEXT NOT NULL,
    split TEXT NOT NULL CHECK (split IN ('train','validation','test')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emotion_primary ON emotion_records(primary_emotion);
CREATE INDEX IF NOT EXISTS idx_emotion_language ON emotion_records(language);
CREATE INDEX IF NOT EXISTS idx_emotion_sensitive ON emotion_records(sensitive_category);
CREATE INDEX IF NOT EXISTS idx_emotion_source ON emotion_records(source_type);
CREATE INDEX IF NOT EXISTS idx_emotion_split ON emotion_records(split);
