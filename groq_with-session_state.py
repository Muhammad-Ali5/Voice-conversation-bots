import os
import streamlit as st
from utils import get_answer, text_to_speech, speech_to_text, autoplay_audio
from streamlit_audiorec import st_audiorec  # Correct import
from streamlit_float import *
import uuid

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your voice assistant. How can I help you today?"}
        ]

initialize_session_state()

st.title("Conversational Voice Chatbot")

footer_container = st.container()
with footer_container:
    audio_bytes = st_audiorec()  # Use st_audiorec

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if audio_bytes:
    with st.spinner("Transcribing..."):
        try:
            webm_file_path = f"temp_audio_{uuid.uuid4()}.wav"  # Use .wav for st_audiorec
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)
            transcript = speech_to_text(webm_file_path)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
            else:
                st.error("Could not transcribe audio.")
        except Exception as e:
            st.error(f"Error processing audio: {e}")
        finally:
            if os.path.exists(webm_file_path):
                os.remove(webm_file_path)

if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            final_answer = get_answer(st.session_state.messages)
        with st.spinner("Generating audio response..."):
            try:
                audio_file = text_to_speech(final_answer)
                autoplay_audio(audio_file)
                st.write(final_answer)
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
            except Exception as e:
                st.error(f"Error generating response: {e}")
            finally:
                if os.path.exists(audio_file):
                    os.remove(audio_file)

footer_container.float("bottom", "center", "100%", "10px")
footer_container.markdown(
    """
    <style>
    .stContainer {
        padding-bottom: 80px;
    }
    .float-container {
        background-color: white;
        box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
        text-align: center;
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)