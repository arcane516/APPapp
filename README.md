# 🎙️ AI Chat Buddy - Live Voice AI Agent

A friendly, conversational AI voice agent that you can talk to like a close buddy! This app features real-time voice interaction with speech-to-text, AI conversation, and text-to-speech capabilities.

## ✨ Features

- 🎤 **Live Voice Recording** - Click and speak naturally
- 🎧 **Speech-to-Text** - Powered by OpenAI Whisper
- 🤖 **Smart Conversations** - Claude 3.5 Sonnet AI with personality
- 🔊 **Voice Responses** - Natural-sounding AI voice replies
- 💬 **Chat History** - See your entire conversation
- 🎭 **Multiple Personalities** - Choose your buddy's vibe:
  - Chill Friend
  - Enthusiastic Buddy
  - Wise Mentor
  - Funny Sidekick
- 🎵 **Voice Customization** - Pick your favorite AI voice

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

You'll need API keys from:
- **OpenAI**: https://platform.openai.com/api-keys (for Whisper STT and TTS)
- **Anthropic**: https://console.anthropic.com/settings/keys (for Claude AI)

You can either:
- Enter them in the sidebar when running the app, OR
- Create a `.env` file (copy from `.env.example`) and add your keys there

### 3. Run the App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 How to Use

1. **Enter your API keys** in the sidebar (if not using .env)
2. **Click the microphone button** to start recording
3. **Speak your message** naturally
4. **Click again to stop** recording
5. **Listen to your AI buddy respond** with voice!

The AI will remember your conversation and respond contextually.

## 🎨 Customization

### Change AI Personality
Use the sidebar to switch between different buddy styles:
- **Chill Friend** - Laid-back and supportive
- **Enthusiastic Buddy** - Energetic and positive
- **Wise Mentor** - Thoughtful and insightful
- **Funny Sidekick** - Witty and entertaining

### Change Voice
Choose from 6 different AI voices in the sidebar:
- alloy, echo, fable, onyx, nova, shimmer

## 🛠️ Tech Stack

- **Streamlit** - Web interface
- **OpenAI Whisper** - Speech-to-text
- **Anthropic Claude 3.5 Sonnet** - AI conversation
- **OpenAI TTS** - Text-to-speech
- **audio-recorder-streamlit** - Audio recording

## 💡 Tips

- Speak clearly for best transcription
- Keep conversations natural and conversational
- Try different personalities for different moods
- The AI keeps context from recent messages

## 📝 Notes

- Audio is processed in real-time
- Conversations are stored in session (not saved between runs)
- Both API keys are required for full functionality

## 🤝 Contributing

Feel free to fork, modify, and make this buddy your own!

---

Made with ❤️ using Streamlit, OpenAI, and Anthropic Claude
