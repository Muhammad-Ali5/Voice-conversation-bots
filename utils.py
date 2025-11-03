# utils.py
import os
import base64
import streamlit as st
from google.cloud import speech, texttospeech
import requests
import tempfile

# Google Cloud Setup - You need to set up credentials
# Option 1: Set GOOGLE_APPLICATION_CREDENTIALS environment variable
# Option 2: Use API keys (shown in alternative functions)

def get_answer(messages):
    """
    Get response using Google's Dialogflow or a simple rule-based system
    For production, use Dialogflow CX API
    """
    try:
        # Simple rule-based responses (replace with Dialogflow API call)
        last_message = messages[-1]["content"].lower()
        
        if any(greeting in last_message for greeting in ["hello", "hi", "hey"]):
            return "Hello! How can I help you today?"
        elif "how are you" in last_message:
            return "I'm doing well, thank you for asking! How can I assist you?"
        elif any(bye in last_message for bye in ["bye", "goodbye", "see you"]):
            return "Goodbye! Have a great day!"
        elif "name" in last_message:
            return "I'm your Google voice assistant. How can I help you?"
        elif "thank" in last_message:
            return "You're welcome! Is there anything else I can help with?"
        else:
            return f"I heard you say: '{last_message}'. How can I assist you with that?"
            
    except Exception as e:
        print(f"Error in get_answer: {e}")
        return "I'm having trouble understanding. Could you please repeat that?"

def text_to_speech(text):
    """
    Convert text to speech using Google Text-to-Speech API
    """
    try:
        # Initialize client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D",  # High-quality voice
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        
        # Select the type of audio file
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Save the audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(response.audio_content)
            audio_file = f.name
        
        return audio_file
        
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        # Fallback to gTTS if Google Cloud fails
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tts.save(f.name)
                return f.name
        except Exception as fallback_error:
            print(f"gTTS fallback also failed: {fallback_error}")
            return None

def speech_to_text(audio_file_path):
    """
    Convert speech to text using Google Speech-to-Text API
    """
    try:
        # Initialize client
        client = speech.SpeechClient()
        
        # Read audio file
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Configure recognition
        audio = speech.RecognitionAudio(content=content)
        
        # Determine encoding based on file extension
        if audio_file_path.endswith(".wav"):
            encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        elif audio_file_path.endswith(".flac"):
            encoding = speech.RecognitionConfig.AudioEncoding.FLAC
        else:
            # Default to WEBM_OPUS for webm files
            encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
        
        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        # Perform speech recognition
        response = client.recognize(config=config, audio=audio)
        
        # Process results
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        
        return transcript.strip()
        
    except Exception as e:
        print(f"Error in speech_to_text: {e}")
        # Try API key method as fallback
        try:
            return speech_to_text_with_api_key(audio_file_path)
        except Exception as api_error:
            print(f"API key method also failed: {api_error}")
            return "Could not transcribe audio. Please try again."

def speech_to_text_with_api_key(audio_file_path, api_key=None):
    """
    Alternative method using Google Speech-to-Text with API key
    """
    try:
        # Read audio file
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Base64 encode
        audio_content = base64.b64encode(content).decode("utf-8")
        
        # Get API key from environment or parameter
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found")
        
        # API endpoint
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
        
        # Determine encoding
        if audio_file_path.endswith(".wav"):
            encoding = "LINEAR16"
        elif audio_file_path.endswith(".flac"):
            encoding = "FLAC"
        else:
            encoding = "WEBM_OPUS"
        
        # Request payload
        payload = {
            "config": {
                "encoding": encoding,
                "sampleRateHertz": 48000,
                "languageCode": "en-US",
                "enableAutomaticPunctuation": True
            },
            "audio": {
                "content": audio_content
            }
        }
        
        # Make request
        response = requests.post(url, json=payload)
        response.raise_for_status()
        results = response.json()
        
        # Process results
        transcript = ""
        if "results" in results:
            for result in results["results"]:
                transcript += result["alternatives"][0]["transcript"] + " "
        
        return transcript.strip()
        
    except Exception as e:
        print(f"Error in speech_to_text_with_api_key: {e}")
        raise

def autoplay_audio(file_path):
    """
    Autoplay audio in Streamlit
    """
    try:
        if file_path and os.path.exists(file_path):
            # Read audio file and encode to base64
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
            
            # Create HTML audio element with autoplay
            md = f"""
                <audio autoplay controls style="display: none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
            return True
        return False
    except Exception as e:
        print(f"Error in autoplay_audio: {e}")
        return False