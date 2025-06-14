
🩺 Smart Health Chatbot 🤖💊

A health chatbot that understands both text and voice queries to provide medical information, symptom analysis, and maintains your query history.

Tech Stack 🛠️

Python 3 (Core language)

spaCy (NLP processing)

fuzzywuzzy (Fuzzy string matching)

SpeechRecognition (Voice input)

pyttsx3 (Text-to-speech)

JSON (Data storage)

Installation ⚙️

Install dependencies:

pip install -r requirements.txt
python -m spacy download en_core_web_sm
Add your health_data.json file to the project folder

How to Use 🚀
Run the chatbot:

python "health chatbot.py"

Commands:

Just type your health question

check symptoms - Enter symptoms to find possible conditions

voice - Speak your query instead of typing

history - View your previous queries

exit - Quit the program

What It Provides 💡
Instant medical information about diseases
step by step guide 

Symptom-based condition matching

Voice interaction support

Query history tracking

Detailed disease explanations with treatment options

How It Works 🔍
Processes your text/voice input using NLP

Matches against medical knowledge base

Provides structured response with:

Disease explanation

Symptoms list

Treatment options

Step-by-step guidance

Note: Requires microphone for voice features and speakers for audio responses.
