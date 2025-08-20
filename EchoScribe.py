import base64
import os
import tempfile
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk
import pyaudio
import numpy as np
import wave

# Load environment variables
load_dotenv()

# Configuration from ENV
#GPT 4o audio preview
AUDIO_AZ_OPENAI_ENDPOINT = os.getenv("AUDIO_AZ_OPENAI_ENDPOINT")
AUDIO_AZ_OPENAI_KEY = os.getenv('AUDIO_AZ_OPENAI_KEY')
AUDIO_AZ_OPENAI_DEPLOYMENT = os.getenv("AUDIO_AZ_OPENAI_DEPLOYMENT")
AUDIO_AZ_OPENAI_VERSION = os.getenv('AUDIO_AZ_OPENAI_VERSION')

#GPT 4o
TEXT_AZ_OPENAI_KEY = os.getenv('TEXT_AZ_OPENAI_KEY')
TEXT_AZ_OPENAI_ENDPOINT = os.getenv('TEXT_AZ_OPENAI_ENDPOINT')
TEXT_AZ_OPENAI_DEPLOYMENT = os.getenv('TEXT_AZ_OPENAI_DEPLOYMENT')
TEXT_AZ_OPENAI_VERSION = os.getenv('TEXT_AZ_OPENAI_VERSION')

#Speech SDK
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

# Initialize OpenAI Client
audio_client = AzureOpenAI(
    base_url=f"{AUDIO_AZ_OPENAI_ENDPOINT}openai/deployments/{AUDIO_AZ_OPENAI_DEPLOYMENT}/",
    api_key=AUDIO_AZ_OPENAI_KEY,
    api_version=AUDIO_AZ_OPENAI_VERSION,
)

text_client = AzureOpenAI(
    base_url=f"{TEXT_AZ_OPENAI_ENDPOINT}openai/deployments/{TEXT_AZ_OPENAI_DEPLOYMENT}/",
    api_key=TEXT_AZ_OPENAI_KEY,
    api_version=TEXT_AZ_OPENAI_VERSION,
)

class ChatBot:
    def __init__(self, system_prompt=None):
        # Conversation history
        self.conversation_history = []
        
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

    def generate_response(self, user_input=None, audio_file_path=None):
        """
        Generates a response using GPT-4o. Uses text-only GPT-4o for text inputs
        and GPT-4o Audio Preview when an audio file is provided.
        """
        if user_input:
            self.conversation_history.append({"role": "user", "content": user_input})
            
            response = text_client.chat.completions.create(
                model=TEXT_AZ_OPENAI_DEPLOYMENT,  # Standard GPT-4o for text input
                messages=self.conversation_history
            )

            bot_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            return bot_response

        elif audio_file_path:
            with open(audio_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                audio_b64 = base64.b64encode(audio_bytes).decode()

                response = audio_client.chat.completions.create(
                    model=AUDIO_AZ_OPENAI_DEPLOYMENT,  # GPT-4o Audio Preview for audio input
                    messages=[{"role": "user", "content": [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}]},],
                )

            bot_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            return bot_response

    def record_audio(self):
        """
        Uses PyAudio to record audio, saves it as a WAV file, and transcribes it using Azure Speech SDK.
        Returns the file path and transcribed text.
        """
        try:
            audio_format = pyaudio.paInt16
            channels = 1  # Mono audio
            p = pyaudio.PyAudio()

            # Open audio stream for recording
            stream = p.open(format=audio_format,
                            channels=channels,
                            rate=16000,
                            input=True,
                            frames_per_buffer=1024)

            print("Recording... Speak now.")
            frames = []
            silence_count = 0
            silence_threshold = 500

            while True:
                data = stream.read(1024)
                frames.append(data)

                # Check if the recorded chunk is silent
                audio_level = max(data)  # Get max amplitude in chunk
                if audio_level < silence_threshold:
                    silence_count += 1
                else:
                    silence_count = 0  # Reset if sound is detected

                # Stop recording if silence is detected for `silence_timeout` seconds
                if silence_count > (16000 / 1024) * 5:
                    print("Silence detected. Stopping recording.")
                    break

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save recorded audio as a WAV file
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            with wave.open(temp_audio, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(audio_format))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

            print(f"Audio recorded and saved at: {temp_audio}")

            # Transcribe using Azure Speech SDK
            audio_config = speechsdk.audio.AudioConfig(filename=temp_audio)
            speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"Transcription: {result.text}")
                return temp_audio, result.text

            print("Speech not recognized.")
        except Exception as e:
            print(f"Error: {e}")

        return None, None
    
    def reset_conversation(self):
        """
        Resets the conversation history.
        """
        self.conversation_history = []
