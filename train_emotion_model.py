"""Train a lightweight multilingual emotion-classification baseline.

Run from this folder:
    python train_emotion_model.py
    python train_emotion_model.py --predict "I am really happy today!"
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "emotion_dataset.csv"
MODEL_PATH = BASE_DIR / "emotion_model.joblib"
METRICS_PATH = BASE_DIR / "evaluation_report.txt"


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {"text", "primary_emotion", "split"}
    if not rows:
        raise ValueError(f"No records found in {path}")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    return [r for r in rows if r.get("text", "").strip() and r.get("primary_emotion", "").strip()]


def make_model():
    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), min_df=2,
            max_features=60000, sublinear_tf=True,
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char_wb", ngram_range=(3, 5), min_df=2,
            max_features=80000, sublinear_tf=True,
        )),
    ])
    return Pipeline([
        ("features", features),
        ("classifier", LogisticRegression(
            max_iter=1200, class_weight="balanced", random_state=42,
        )),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(DATA_PATH), help="Path to emotion_dataset.csv")
    parser.add_argument("--predict", help="Optional sentence to classify after training")
    args = parser.parse_args()

    rows = read_rows(Path(args.csv))
    train = [r for r in rows if r["split"].strip().lower() == "train"]
    valid = [r for r in rows if r["split"].strip().lower() in {"validation", "valid", "dev"}]
    test = [r for r in rows if r["split"].strip().lower() == "test"]

    if not train or not test:
        raise ValueError("Expected non-empty train and test partitions in the 'split' column.")

    X_train = [r["text"] for r in train]
    y_train = [r["primary_emotion"].strip().lower() for r in train]
    X_test = [r["text"] for r in test]
    y_test = [r["primary_emotion"].strip().lower() for r in test]

    model = make_model()
    print(f"Rows: {len(rows)} total | {len(train)} train | {len(valid)} validation | {len(test)} test")
    print("Training TF-IDF + Logistic Regression...")
    model.fit(X_train, y_train)

    # Validation metrics are shown separately from the final test metrics.
    if valid:
        X_valid = [r["text"] for r in valid]
        y_valid = [r["primary_emotion"].strip().lower() for r in valid]
        valid_pred = model.predict(X_valid)
        print("\nVALIDATION RESULTS")
        print(f"Accuracy: {accuracy_score(y_valid, valid_pred):.4f}")
        print(f"Macro F1: {f1_score(y_valid, valid_pred, average='macro', zero_division=0):.4f}")

    test_pred = model.predict(X_test)
    labels = sorted(set(y_test) | set(test_pred))
    report = classification_report(y_test, test_pred, labels=labels, zero_division=0)
    summary = (
        "TEST RESULTS\n"
        f"Accuracy: {accuracy_score(y_test, test_pred):.4f}\n"
        f"Macro F1: {f1_score(y_test, test_pred, average='macro', zero_division=0):.4f}\n\n"
        "Classification report:\n" + report + "\nConfusion matrix (rows=true, columns=predicted; labels="
        + json.dumps(labels) + "):\n" + str(confusion_matrix(y_test, test_pred, labels=labels)) + "\n"
    )
    print("\n" + summary)

    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(summary, encoding="utf-8")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved report: {METRICS_PATH}")

    if args.predict:
        prediction = model.predict([args.predict])[0]
        probabilities = model.predict_proba([args.predict])[0]
        classes = model.named_steps["classifier"].classes_
        ranked = sorted(zip(classes, probabilities), key=lambda item: item[1], reverse=True)
        print("\nCUSTOM PREDICTION")
        print(json.dumps({
            "text": args.predict,
            "predicted_emotion": prediction,
            "model_scores_not_calibrated_confidence": [
                {"emotion": label, "score": round(float(score), 4)}
                for label, score in ranked[:3]
            ],
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
