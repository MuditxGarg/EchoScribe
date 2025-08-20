# EchoScribe: Multimodal Meeting Assistant

**EchoScribe** is an AI-powered assistant that transcribes meetings, summarizes content, and enables multimodal Q&A. It supports real-time and offline interactions via audio, text, and visual inputs using Azure OpenAI (GPT-4o series), Azure Speech SDK, and Whisper.

---

## 🔀 Project Variants

| Variant                           | Files Involved                                      | UI Framework | Input Modality        | Output Modality       | Models Used                                             |
|----------------------------------|-----------------------------------------------------|--------------|------------------------|------------------------|----------------------------------------------------------|
| **1. Conversational Bot**        | `base_file.py`, `base_file_streamlit.py`           | Streamlit    | Text, Audio (mic)      | Text, Audio (TTS)      | `gpt-4o`, Azure STT, Azure TTS                           |
| **2. EchoScribe Task Extractor** | `EchoScribe.py`, `EchoScribe_st.py`                | Streamlit    | Text, Audio (mic/wav)  | Text (JSON / Table)    | `gpt-4o`, `gpt-4o-mini-audio-preview`, Azure STT         |
| **3. Realtime Voice Assistant**  | `realtime_app.py`, `realtime_client.py`, `realtime_config.py`, `realtime_utils.py` | Chainlit     | Streaming Audio, Text  | Streaming Audio, Text  | `gpt-4o-realtime-preview`, Azure STT, Azure TTS          |
| **4. CLI ALT-to-Talk Demo**      | `test.py`                                           | CLI          | Audio (ALT key held)   | Text, Audio (auto-TTS) | `gpt-4o`, Azure STT, Azure TTS                           |

---

## 🧠 Models Used

- **GPT-4o Family**:
  - `gpt-4o`
  - `gpt-4o-mini`
  - `gpt-4o-mini-audio-preview`
  - `gpt-4o-mini-tts`
  - `gpt-4o-transcribe`
  - `gpt-4o-realtime-preview`
- **Azure Speech Services** (STT & TTS)
- **Whisper** (Optional offline STT)

---

## 🔐 Environment Variables Setup

Create a `.env` file in your project root and define the variables below based on the variant you are running:

### 🔊 Common Speech Configuration
```env
SPEECH_KEY=...
SPEECH_REGION=...
```

### 💬 GPT-4o for Text-based Completion
```env
TEXT_AZ_OPENAI_KEY=...
TEXT_AZ_OPENAI_ENDPOINT=https://<your-aoai>.openai.azure.com/
TEXT_AZ_OPENAI_DEPLOYMENT=<gpt4o-deployment-name>
TEXT_AZ_OPENAI_VERSION=2024-06-01
```

### 🔉 GPT-4o for Audio Completion
```env
AUDIO_AZ_OPENAI_KEY=...
AUDIO_AZ_OPENAI_ENDPOINT=https://<your-aoai>.openai.azure.com/
AUDIO_AZ_OPENAI_DEPLOYMENT=gpt-4o-mini-audio-preview
AUDIO_AZ_OPENAI_VERSION=2024-08-01-preview
```

### 🔁 Realtime Voice Assistant (Chainlit)
```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT_NAME=<your-aoai-endpoint-hostname>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-realtime-preview
```

### 📝 Whisper STT (Optional)
```env
STT_AZ_OPENAI_ENDPOINT=https://<your-aoai>.openai.azure.com/
STT_AZ_OPENAI_KEY=...
STT_AZ_OPENAI_DEPLOYMENT=whisper
STT_AZ_OPENAI_VERSION=2024-06-01
```

---

EchoScribe is modular and configurable — ideal for real-time meetings, audio summaries, task extraction, and enterprise chatbot integration. This is just a simple exploration project which can be converted into a full realtime project as per use case.
