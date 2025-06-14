"""
A Smart Health chatbot which responed your prompt and your voice prompt and symptoms match diseases and you can see your history 
"""
import json
import spacy
from fuzzywuzzy import process
import sys
import speech_recognition as sr
import pyttsx3
import threading
import queue

# ---------- Voice Engine with Queue ----------
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)
speak_queue = queue.Queue()

def speak_worker():
    while True:
        text = speak_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        speak_queue.task_done()

threading.Thread(target=speak_worker, daemon=True).start()

def speak(text):
    speak_queue.put(text)

# ---------- Load spaCy Model ----------
nlp = spacy.load("en_core_web_sm")

# ---------- Load Health Data ----------
with open('health_data.json', 'r') as f:
    health_data = json.load(f)

keys = list(health_data.keys())

# ---------- History ----------
def save_to_history(user_query, matched_disease):
    entry = {"query": user_query, "match": matched_disease}
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history.append(entry)
    with open("history.json", "w") as f:
        json.dump(history, f, indent=2)

def show_history():
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
        if not history:
            return "📂 No history found."
        response = "📖 Your Query History:\n"
        for i, entry in enumerate(history, start=1):
            response += f"{i}. ❓ Query: {entry['query']} ➡️ 🦠 Match: {entry['match']}\n"
        return response
    except:
        return "⚠️ Error loading history."

# ---------- Matching ----------
def find_best_match(user_input):
    doc = nlp(user_input.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    processed_input = " ".join(tokens)
    match, score = process.extractOne(processed_input, keys)
    return match if score > 60 else None

# ---------- Response ----------
def get_response(disease_key):
    if disease_key in health_data:
        info = health_data[disease_key]
        print(f"\n🤖 *{disease_key.title()}*\n")
        print(f"🧾 Explanation: {info['explanation']}\n")
        print("🩺 Symptoms:\n" + "\n".join(f"• {s}" for s in info['symptoms']) + "\n")
        print("💊 Solutions:\n" + "\n".join(f"• {s}" for s in info['solutions']) + "\n")
        print("🪜 Step-by-step Guide:\n" + "\n".join(f"Step {i+1}: {s}" for i, s in enumerate(info['steps'])))
        return f"{disease_key.title()}: {info['explanation']}"
    else:
        print("🤖 Sorry, I don't have information on that topic.")
        return "Sorry, I don't have information on that topic."
# ---------- Symptom Checker ----------
def symptom_checker():
    print("🤖 Please enter your symptoms (comma-separated):")
    user_input = input("🧑 You: ")
    input_symptoms = [s.strip().lower() for s in user_input.split(',')]
    disease_scores = []

    for disease, data in health_data.items():
        disease_symptoms = [sym.lower() for sym in data['symptoms']]
        match_count = sum(1 for sym in input_symptoms if sym in disease_symptoms)
        if match_count > 0:
            score = match_count / len(disease_symptoms)
            disease_scores.append((disease, score))

    if not disease_scores:
        return "❌ No diseases matched your symptoms. Try adding more or clearer symptoms."

    # Sort by score descending
    disease_scores.sort(key=lambda x: x[1], reverse=True)

    # If a disease has ≥60% match, show only that one
    if disease_scores[0][1] >= 0.6:
        disease = disease_scores[0][0]
        return f"✅ Most relevant match based on symptoms:\n• {disease.title()}"
    else:
        top_matches = [d[0].title() for d in disease_scores[:3]]
        return "🔍 Top 3 possible matches based on symptoms:\n" + "\n".join(f"• {d}" for d in top_matches)

# ---------- Voice Input ----------
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            print(f"🧑 You said: {query}")
            return query
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand your voice."
        except sr.RequestError:
            return "API unavailable."

# ---------- Welcome ----------
print("💬 Welcome to Smart Health Chatbot!")
print("📌 How can I help you today?")
print(" Type your health question")
print(" Type 'check symptoms' to find possible diseases based on symptoms")
print("Type 'voice' to speak your query instead of typing")
print("Type 'history' to view your previous queries")
print("❌ Type 'exit' to quit the chatbot")

# ---------- Main Loop ----------
while True:
    print("\n🧑 You: ", end="")
    sys.stdout.flush()
    user_input = input()

    if user_input.lower() == 'exit':
        print("🤖 Goodbye! Stay healthy!")
        speak("Goodbye! Stay healthy!")
        break

    elif user_input.lower() == 'history':
        history = show_history()
        print("\n" + history)
        speak("Here is your history.")

    elif user_input.lower() == 'check symptoms':
        result = symptom_checker()
        print("\n" + result)
        speak("Based on your symptoms, here are possible conditions.")

    elif user_input.lower() == 'voice':
        voice_input = get_voice_input()
        match = find_best_match(voice_input)
        if match:
            save_to_history(voice_input, match)
            reply = get_response(match)
            speak(reply)
        else:
            print("🤖 Sorry, I didn't understand your voice query.")
            speak("Sorry, I didn't understand your voice query.")

    else:
        match = find_best_match(user_input)
        if match:
            save_to_history(user_input, match)
            reply = get_response(match)
            speak(reply)
        else:
            print("\n🤖 Sorry, I didn't understand your query. Please try asking differently.")
            speak("Sorry, I didn't understand your query. Please try asking differently.")
