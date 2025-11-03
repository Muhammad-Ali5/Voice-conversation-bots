import os
import streamlit as st
from utils import get_answer, text_to_speech, speech_to_text, autoplay_audio
from streamlit_audio_recorder import audio_recoder
from streamlit_float import *

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "HI! I'm your voice assistant. How can I help you today?\n How can I help you today?"}
        ]
initialize_session_state()

st.title("Conversational Voice Chatbot")
# create the footer container for the microphone button
footer_container = st.container()
with footer_container:
    audio_bytes = audio_recoder()
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    with st.spinner("Transcribing..."):
        webm_file_path = "temp_audio.mp3"
        with open(webm_file_path, "wb") as f:
            f.write(audio_bytes)

        transcript = speech_to_text(webm_file_path)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(webm_file_path)

# reply from the Model
if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            final_answer = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):
            audio_file = text_to_speech(final_answer)
            autoplay_audio(audio_file)
        
        st.write(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        os.remove(audio_file)
        
# float the footer container and provide the css to target it with
footer_container.float("bottom", "center", "100%", "10px")
footer_container.markdown(
    """
    <style>
    .stContainer {
        padding-bottom: 80px; /* Adjust based on footer height */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
