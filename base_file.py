# -------------------------
# uses: Whisper, TTS, GPT 4o
# currently not using Whisper
# -------------------------

# base_file.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk

# Load environment variables from .env file
load_dotenv()

# -------------------------
# Configuration from ENV
# -------------------------

# Whisper Env Variables for STT (if you later choose to use Whisper)
STT_AZ_OPENAI_ENDPOINT = os.getenv('STT_AZ_OPENAI_ENDPOINT')
STT_AZ_OPENAI_KEY = os.getenv('STT_AZ_OPENAI_KEY')
STT_AZ_OPENAI_DEPLOYMENT = os.getenv('STT_AZ_OPENAI_DEPLOYMENT')
STT_AZ_OPENAI_VERSION = os.getenv('STT_AZ_OPENAI_VERSION')

# Speech SDK Env Variables for TTS and (optionally) Speech Recognition
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

# GPT-4o Env Variables for Chat
TEXT_AZ_OPENAI_KEY = os.getenv('TEXT_AZ_OPENAI_KEY')
TEXT_AZ_OPENAI_ENDPOINT = os.getenv('TEXT_AZ_OPENAI_ENDPOINT')
TEXT_AZ_OPENAI_DEPLOYMENT = os.getenv('TEXT_AZ_OPENAI_DEPLOYMENT')
TEXT_AZ_OPENAI_VERSION = os.getenv('TEXT_AZ_OPENAI_VERSION')

# -------------------------
# Initialize Clients
# -------------------------

# Chat Client (GPT-4o)
chat_client = AzureOpenAI(
    base_url=f"{TEXT_AZ_OPENAI_ENDPOINT}openai/deployments/{TEXT_AZ_OPENAI_DEPLOYMENT}",
    api_key=TEXT_AZ_OPENAI_KEY,
    api_version=TEXT_AZ_OPENAI_VERSION,
)

# Speech SDK Initialization (for TTS)
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
speech_config.speech_synthesis_voice_name = 'en-US-JennyMultilingualNeural'
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

# Whisper Client (STT)
stt_client = AzureOpenAI(
    azure_endpoint=STT_AZ_OPENAI_ENDPOINT,
    api_key=STT_AZ_OPENAI_KEY,
    api_version=STT_AZ_OPENAI_VERSION
)

# -------------------------
# ChatBot Logic
# -------------------------

class ChatBot:
    def __init__(self, system_prompt=None):
        # Conversation history maintained as a list of messages
        self.conversation_history = []

        # If a system prompt is given, add it at the front
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

        self.chat_client = chat_client
        self.stt_client = stt_client #currently not being used
        self.speech_synthesizer = speech_synthesizer

    def transcribe_audio(self, audio_file_path):
        """
        Transcribes an audio file (e.g. recorded externally) to text using Azure OpenAI Whisper.
        This method is not used in the current flow because the Speech SDK is used for recognition.
        """
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        response = self.stt_client.audio.transcriptions.create(
            file=audio_bytes,
            model=STT_AZ_OPENAI_DEPLOYMENT
        )
        text = response.text  
        return text

    def generate_response(self, user_input):
        """
        Generates a conversational response from GPT-4o given the user input.
        The conversation history is maintained to allow contextual replies.
        """
        # Append the user's message to the history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        response = self.chat_client.chat.completions.create(
            model=TEXT_AZ_OPENAI_DEPLOYMENT,
            messages=self.conversation_history
        )
        bot_response = response.choices[0].message.content
        # Append the bot's response to the history
        self.conversation_history.append({"role": "assistant", "content": bot_response})
        return bot_response

    def speak_text(self, text):
        """
        Uses Azure Speech SDK to convert text to speech (plays on the default speaker).
        """
        result = self.speech_synthesizer.speak_text_async(text).get()
        return result

    def reset_conversation(self):
        """
        Resets the conversation history.
        """
        self.conversation_history = []
