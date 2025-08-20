import streamlit as st
import os
import azure.cognitiveservices.speech as speechsdk
import tempfile
from dotenv import load_dotenv
from EchoScribe import ChatBot

# Load environment variables
load_dotenv()
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

st.title("EchoScribe: Task Management")

# Initialize ChatBot in session state
if "chatbot" not in st.session_state:
    sys_prompt = """
    Extract and structure task details from user input, even if embedded in a paragraph without explicit headers. 
    Identify key elements like task number, name, description, customer, meeting agenda, project specifics, and time. 
    Output the result in either a table or nested JSON format.
    - Parse input to recognize tasks and relevant details.
    - Structure data into a clear format, filling missing fields as null.
    - If task number is missing, generate them appropriately
    - Format output as:
        Table: Each row represents a task with structured columns.
        JSON: Hierarchical representation of tasks and details.
    If critical details (e.g., task number) are missing, flag them. Handle varied phrasing and input styles dynamically.
    """
    
    st.session_state.chatbot = ChatBot(system_prompt=sys_prompt)

# Initialize messages in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Please provide the following details about each entry: Task Number, Module Name, Module Description"}
    ]

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input section
col1, col2 = st.columns([4, 1])

# Text input
with col1:
    prompt = st.chat_input("Your message")

# Microphone button for speech input
audio_file_path = None
transcribed_text = None
with col2:
    if st.button("🎤"):
        with st.spinner("Recording audio..."):
            audio_file_path, transcribed_text = st.session_state.chatbot.record_audio()

            if audio_file_path:
                # Show both [Audio Input] and transcribed text
                st.session_state.messages.append({"role": "user", "content": f"**[Audio Input]**\n{transcribed_text}"})
                with st.chat_message("user"):
                    st.markdown(f"**[Audio Input]**\n{transcribed_text}")
            else:
                st.error("Audio recording failed. Please try again.")

# Handle text input using GPT-4o
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            bot_response = st.session_state.chatbot.generate_response(user_input=prompt)
        st.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# Handle audio input using GPT-4o Audio Preview
elif audio_file_path:
    with st.chat_message("assistant"):
        with st.spinner("Processing audio..."):
            bot_response = st.session_state.chatbot.generate_response(audio_file_path=audio_file_path)
        st.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
