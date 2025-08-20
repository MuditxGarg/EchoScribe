import os
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI
import sounddevice as sd
import numpy as np
import keyboard
import wave
import tempfile
import requests
from playsound import playsound

load_dotenv()
# Set up Azure OpenAI API
endpoint = os.getenv("AZ_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

gpt4o_mini_audio_client = AzureOpenAI(
    api_version="2024-08-01-preview",
    api_key=api_key,
    azure_endpoint=endpoint
)

# Load Whisper model for speech-to-text
whisper_model = "whisper"
whisper_client = AzureOpenAI(
        api_key=api_key,  
        api_version="2024-06-01",
        azure_endpoint=endpoint
    )

# Chat history
messages = []

# Audio recording settings
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5 

# Function to record audio from microphone
def record_audio(filename="input.wav"):
    print("\n🎤 Speak now (Press & hold ALT to record)...")
    audio_data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
        while keyboard.is_pressed("alt"):
            pass  # Wait for ALT key release

    # Convert recorded chunks to NumPy array
    audio_array = np.concatenate(audio_data, axis=0)

    # Save as WAV file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())

    print("🎙️ Recording stopped.")
    return filename

# Function to transcribe audio to text using Whisper
def transcribe_audio(audio_path):
    print("📝 Transcribing...")
    result = whisper_client.audio.transcriptions.create(
        file=open(audio_path, "rb"),            
        model=whisper_model
    )
    return result.text

# Function to send message to OpenAI API
def send_message(user_message):
    global messages
    messages.append({"role": "user", "content": user_message})

    # Call GPT-4o with multimodal response
    completion = gpt4o_mini_audio_client.chat.completions.create(
        model="gpt-4o-mini-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
        messages=messages
    )

    # Get text response
    bot_text_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": bot_text_response})

    # Get audio response
    bot_audio_url = completion.choices[0].message.audio.url

    return bot_text_response, bot_audio_url

# Function to save and play the bot's audio response
def play_bot_audio(audio_url):
    temp_audio_path = tempfile.mktemp(suffix=".wav")

    response = requests.get(audio_url)
    with open(temp_audio_path, "wb") as audio_file:
        audio_file.write(response.content)

    print("🔊 Playing bot response...")
    playsound(temp_audio_path)

#Main Chat Loop
def chat():
    print("\n💬 Chat Started! Press 'ALT' to speak or type your message.")

    while True:
        user_input = ""
        keyboard.wait("alt")
        audio_file = record_audio()
        user_input = transcribe_audio(audio_file)
        print(f"\n👤 You: {user_input}")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting chat.")
            break

        bot_text, bot_audio_url = send_message(user_input)
        print(f"\n🤖 Bot: {bot_text}")

        if bot_audio_url:
            play_bot_audio(bot_audio_url)

chat()
