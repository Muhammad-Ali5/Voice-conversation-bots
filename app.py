import os
import streamlit as st
from utils import get_answer, text_to_speech, speech_to_text, autoplay_audio
from streamlit_audio_recorder import audio_recorder
from streamlit_float import *
import tempfile

# Initialize float
float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your Google voice assistant. How can I help you today?"}
        ]
    if "processing" not in st.session_state:
        st.session_state.processing = False

initialize_session_state()

st.title("Google Voice Assistant Chatbot")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Audio recorder at the bottom
with st.container():
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_size="2x",
    )

# Process audio when recorded
if audio_bytes and not st.session_state.processing:
    st.session_state.processing = True
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
        f.write(audio_bytes)
        audio_path = f.name
    
    # Transcribe audio
    with st.spinner("Transcribing..."):
        transcript = speech_to_text(audio_path)
    
    if transcript and transcript != "Could not transcribe audio. Please try again.":
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": transcript})
        with st.chat_message("user"):
            st.write(transcript)
    
    # Clean up
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    st.session_state.processing = False
    st.rerun()

# Generate assistant response if last message is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            final_response = get_answer(st.session_state.messages)
        
        st.write(final_response)
        
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_response)
        
        if audio_file:
            # Auto-play the audio
            autoplay_audio(audio_file)
            
            # Clean up audio file after use
            if os.path.exists(audio_file):
                os.remove(audio_file)
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": final_response})