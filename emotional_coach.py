import sqlite3
import json
import joblib
from pathlib import Path
import urllib.request

class ConditionalTrajectoryCounselor:
    def __init__(self, db_path="extracted_bundle/emotion_dataset_bundle/emotion_dataset.sqlite", 
                 model_path="extracted_bundle/emotion_dataset_bundle/emotion_model.joblib", 
                 ollama_model="llama3.2"):
        self.ollama_model = ollama_model
        self.db_path = Path(db_path)
        self.chat_history = []

        # 1. Load trained classification model
        if Path(model_path).exists():
            self.emotion_classifier = joblib.load(model_path)
        else:
            self.emotion_classifier = None

        # 2. Connect to SQLite database
        if self.db_path.exists():
            self.conn = sqlite3.connect(str(self.db_path))
        else:
            self.conn = None

    def query_dataset_examples(self, primary_emotion, limit=2):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT text, language, primary_emotion 
            FROM emotion_records 
            WHERE primary_emotion = ? OR language = 'hinglish'
            LIMIT ?
        """, (primary_emotion, limit))
        return cursor.fetchall()

    def classify_text(self, text):
        if not self.emotion_classifier:
            return "unknown"
        return self.emotion_classifier.predict([text])[0]

    def query_ollama(self, prompt):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }
        
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "").strip()
        except Exception as e:
            return f"Error communicating with local Ollama server: {e}"

    def analyze(self, user_text):
        predicted_emo = self.classify_text(user_text)
        dataset_refs = self.query_dataset_examples(predicted_emo, limit=2)
        ref_text = "\n".join([f"- \"{row[0]}\" (Emotion: {row[2]})" for row in dataset_refs])

        # Updated System Prompt with strict behavioral rules against hallucinations
        system_instruction = f"""
        You are an empathetic, emotionally intelligent local companion. 
        The user is communicating in Hinglish or English (e.g., "itni bakwas karte hai woh" means "they talk so much nonsense / trash"). Do not misquote the user. Do not hallucinate that they are talking about you or your advice unless they explicitly state it.

        Model Classification:
        - Primary Detected Emotion: {predicted_emo.upper()}
        - Exact User Input: "{user_text}"

        Dataset Reference Examples:
        {ref_text if ref_text else "None."}

        Guidelines:
        1. **Listen & Validate First**: Respond naturally and conversationally to what the user actually said. If they are venting about other people talking nonsense, acknowledge their annoyance or frustration with that situation.
        2. **Conditional Future Outlook**: ONLY include a "Future Outlook & Trajectory" section if the user is showing signs of severe burnout, chronic stress, or explicitly asking about long-term consequences. For normal venting, casual complaints, or brief remarks, **omit the future trajectory section entirely** to keep the conversation natural.
        3. **Constructive Pivot**: Offer practical, grounding advice or a supportive ear without sounding robotic or formulaic.
        """

        self.chat_history.append(f"User: {user_text}")
        context = "\n".join(self.chat_history[-6:])

        full_prompt = f"{system_instruction}\n\nConversation History:\n{context}\n\nResponse:"
        return self.query_ollama(full_prompt)

    def run(self):
        print("\n" + "="*70)
        print("   SMART CONDITIONAL-TRAJECTORY COUNSELOR (Llama 3.2)")
        print("="*70)
        print("Chat naturally in Hinglish or English. Type 'quit' to exit.\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    print("\n[Session ended.]")
                    break

                response = self.analyze(user_input)
                self.chat_history.append(f"Counselor: {response}")
                print(f"\nResponse:\n{response}")
                print("-" * 70)

            except KeyboardInterrupt:
                print("\n\n[Session closed.]")
                break

if __name__ == "__main__":
    counselor = ConditionalTrajectoryCounselor()
    counselor.run()