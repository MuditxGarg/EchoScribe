# -------------------------
# uses: Whisper, TTS, GPT 4o
# for: base_file.py
# currently not using Whisper
# -------------------------

# streamlit_app.py
import streamlit as st
import os
import azure.cognitiveservices.speech as speechsdk
import tempfile
from dotenv import load_dotenv
from base_file import ChatBot

# Load environment variables
load_dotenv()
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

st.title("Conversational Bot")

# Initialize ChatBot and conversation history in session state.
if "chatbot" not in st.session_state:
    sys_prompt = """You are a professional and lively AI assistant designed to help users summarize and create meeting notes. 
    Respond in a concise and professional manner. You can accept input in text or audio form. When a user requests a note 
    (e.g., 'Draft me a note'), ask for the following key details: customer name, meeting agenda, task description, and project specifics.
    Use an engaging, formal tone without emojis or overly casual expressions.
    Before responding, review your answer to ensure it meets these guidelines. If uncertain, ask the user for clarification."""

    st.session_state.chatbot = ChatBot(
        system_prompt=sys_prompt
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message is from the assistant, add a speaker button.
        if message["role"] == "assistant":
            if st.button("🔊", key=f"speaker_{i}"):
                st.session_state.chatbot.speak_text(message["content"])

# Input area
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.chat_input("Your message")
with col2:
    if st.button("🎤"):
        try:
            # Set up Speech SDK for voice input.
            speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
            speech_config.speech_recognition_language = "en-US"
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            result = recognizer.recognize_once_async().get()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                prompt = result.text
            else:
                st.error("Voice not recognized. Please try again.")
        except Exception as e:
            st.error("Error recording voice input: " + str(e))

if prompt:
    # Append the user prompt to the conversation history.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the bot response.
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            bot_response = st.session_state.chatbot.generate_response(prompt)
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
