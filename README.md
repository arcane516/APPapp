### 🎙️ Voice Buddy — A cozy AI you can talk to

A Streamlit app for real-time voice chats with an AI buddy. Record your voice, it transcribes, replies with an LLM (vibes configurable), and speaks back using TTS.

#### Features
- Voice capture in-browser
- Transcription via OpenAI
- Chat responses with configurable vibes (best friend, chill, coach, therapist, comedian)
- Text-to-speech playback
- Type-chat fallback and full conversation history

#### Requirements
- Python 3.10+
- An OpenAI API key with access to GPT-4o-mini, transcription, and TTS endpoints

#### Setup
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Provide your API key (choose one)
   - Set env var before launching: `export OPENAI_API_KEY=sk-...`
   - Or add to Streamlit secrets: create `.streamlit/secrets.toml` with `OPENAI_API_KEY = "sk-..."`
   - Or paste it in the app sidebar when prompted
3. Run the app
   ```bash
   streamlit run streamlit_app.py
   ```

#### Notes
- Audio is processed locally in the browser then sent to OpenAI for STT and TTS.
- We do not store your key; it's kept only in your local session.
- Use the sidebar to switch vibes and voice and toggle auto speech.

