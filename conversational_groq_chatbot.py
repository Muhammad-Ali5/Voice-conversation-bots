import os
import speech_recognition as sr
import pyttsx3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini model via LangChain
chat = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # try "gemini-1.5-pro" for deeper answers
    temperature=0.7
)

# Add conversational memory
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=chat, memory=memory, verbose=True)

# Initialize recognizer + text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

print("🎙️ Gemini Voice Chatbot ready! Speak into your mic... (Ctrl+C to quit)")

while True:
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        # 🎤 Speech → Text
        user_input = recognizer.recognize_google(audio)
        print(f"🧑 You: {user_input}")

        # 🤖 Gemini Response (with memory)
        response = conversation.predict(input=user_input)
        print(f"🤖 Bot: {response}")

        # 🗣️ Speak response
        speak(response)

    except sr.UnknownValueError:
        print("❌ Sorry, I didn’t catch that.")
    except KeyboardInterrupt:
        print("\n👋 Exiting chat...")
        break
