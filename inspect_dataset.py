
import csv
import sqlite3
from collections import Counter

# 1. Read a few examples from the CSV
with open("emotion_dataset.csv", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    print("FIRST 5 RECORDS")
    for i, row in enumerate(reader):
        if i == 5:
            break

        print(f"\nText: {row['text']}")
        print(f"Language: {row['language']}")
        print(f"Emotion: {row['primary_emotion']}")
        print(f"Intensity: {row['emotion_intensity_1_5']}")

# 2. Count emotions in the CSV
with open("emotion_dataset.csv", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    emotion_counts = Counter(
        row["primary_emotion"] for row in reader
    )

print("\nEMOTION DISTRIBUTION")
for emotion, count in emotion_counts.most_common():
    print(f"{emotion}: {count}")

# 3. Query the SQLite database
connection = sqlite3.connect("emotion_dataset.sqlite")

print("\nSAMPLE SQLITE RECORDS")
cursor = connection.execute("""
    SELECT text, language, primary_emotion,
           emotion_intensity_1_5
    FROM emotion_records
    LIMIT 5
""")

for record in cursor.fetchall():
    print(record)

connection.close()
