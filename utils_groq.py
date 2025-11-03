import speech_recognition as sr
from gtts import gTTS
import streamlit as st
import os

def get_answer(messages):
    # Placeholder: Replace with LLM API (e.g., xAI Grok API)
    return "This is a response to: " + messages[-1]["content"]

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_file = f"response_{uuid.uuid4()}.mp3"
    tts.save(audio_file)
    return audio_file

def speech_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        raise Exception(f"Speech-to-text error: {e}")

def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        st.audio(f, format="audio/mp3", autoplay=True)