import os
import json
from langchain_mistralai import ChatMistralAI

CHITCHAT_FILE = os.path.join(os.path.dirname(__file__), "chitchat.json")
MISTRAL_API_KEY = "AV7Bn0Douoc9YqtAKcRyFZcxiZD4zfbs"

# Load chitchat knowledge base
def load_chitchat():
    if not os.path.exists(CHITCHAT_FILE):
        return {}
    with open(CHITCHAT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Save chitchat knowledge base
def save_chitchat(data):
    with open(CHITCHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Detect and handle chitchat (returns None if not chitchat)
def detect_chitchat(question: str, lang: str = "en") -> str | None:
    chitchat = load_chitchat()
    q_lower = question.strip().lower()

    # Match existing chitchat
    if q_lower in chitchat:
        return f"🤖 {chitchat[q_lower]}"

    # Try to generate response for new chitchat
    try:
        llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-small")
        prompt = f"You are a friendly assistant. Respond in {lang.upper()} to this casual question:\n\n\"{question}\""
        response = llm.invoke(prompt).strip()

        # Save for next time
        chitchat[q_lower] = response
        save_chitchat(chitchat)

        return f"🤖 {response}"

    except Exception as e:
        print("❌ Error generating chitchat response:", e)
        return "🤖 I'm not sure how to respond to that, but I'm learning!"
