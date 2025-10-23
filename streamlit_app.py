import streamlit as st
import os
from io import BytesIO
import base64
from audio_recorder_streamlit import audio_recorder
import openai
from anthropic import Anthropic
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="AI Chat Buddy 🎙️",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a friendly, modern UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .ai-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .status-box {
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: white;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False

# Sidebar for API keys
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys
    openai_api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key = st.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
    
    st.markdown("---")
    
    # Voice settings
    st.subheader("🎵 Voice Settings")
    voice_choice = st.selectbox(
        "AI Voice",
        ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        index=4  # nova default
    )
    
    st.markdown("---")
    
    # Personality settings
    st.subheader("🤖 AI Personality")
    personality = st.selectbox(
        "Buddy Style",
        ["Chill Friend", "Enthusiastic Buddy", "Wise Mentor", "Funny Sidekick"],
        index=0
    )
    
    st.markdown("---")
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 How to use:")
    st.markdown("""
    1. Add your API keys above
    2. Click the microphone to record
    3. Speak your message
    4. Stop recording
    5. AI buddy will respond with voice!
    """)

# Main content
st.markdown("<h1>🎙️ AI Chat Buddy</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your friendly voice AI companion - Let's vibe together! 🤗</p>", unsafe_allow_html=True)

# Check API keys
if not openai_api_key or not anthropic_api_key:
    st.warning("⚠️ Please enter your OpenAI and Anthropic API keys in the sidebar to get started!")
    st.info("💡 Get your API keys from:\n- OpenAI: https://platform.openai.com/api-keys\n- Anthropic: https://console.anthropic.com/settings/keys")
    st.stop()

# Initialize clients
openai.api_key = openai_api_key
anthropic_client = Anthropic(api_key=anthropic_api_key)

def get_personality_prompt(personality_type):
    """Get the system prompt based on personality type"""
    prompts = {
        "Chill Friend": "You are a chill, laid-back friend who speaks naturally and casually. You're supportive, easy-going, and always there to listen. Keep responses conversational and concise (2-4 sentences max). Use casual language like 'yeah', 'totally', 'for sure'.",
        "Enthusiastic Buddy": "You are an enthusiastic, energetic friend who's always excited to chat! You're positive, encouraging, and full of life. Keep responses upbeat and concise (2-4 sentences max). Use expressions like 'awesome!', 'amazing!', 'that's so cool!'",
        "Wise Mentor": "You are a wise, thoughtful mentor who gives great advice. You're insightful, caring, and help friends see things clearly. Keep responses thoughtful but concise (2-4 sentences max). Speak with wisdom and kindness.",
        "Funny Sidekick": "You are a funny, witty friend who loves to make people laugh. You're playful, joke around, and keep things light. Keep responses humorous and concise (2-4 sentences max). Be clever and entertaining!"
    }
    return prompts.get(personality_type, prompts["Chill Friend"])

def transcribe_audio(audio_bytes):
    """Transcribe audio using OpenAI Whisper"""
    try:
        # Save audio to temporary file
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        # Transcribe using Whisper
        client = openai.OpenAI(api_key=openai_api_key)
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        st.error(f"❌ Transcription error: {str(e)}")
        return None

def get_ai_response(user_message, personality_type):
    """Get AI response using Anthropic Claude"""
    try:
        # Build conversation history
        messages = []
        for msg in st.session_state.messages[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response from Claude
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            system=get_personality_prompt(personality_type),
            messages=messages
        )
        
        return response.content[0].text
    except Exception as e:
        st.error(f"❌ AI response error: {str(e)}")
        return None

def text_to_speech(text, voice="nova"):
    """Convert text to speech using OpenAI TTS"""
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Return audio bytes
        return response.content
    except Exception as e:
        st.error(f"❌ Text-to-speech error: {str(e)}")
        return None

def autoplay_audio(audio_bytes):
    """Autoplay audio in the browser"""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Display conversation history
if st.session_state.messages:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-message'>🎤 You: {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-message'>🤖 Buddy: {message['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div class='status-box'>
            <h3>👋 Hey there!</h3>
            <p>Ready to chat? Hit the record button below and let's vibe! 🎵</p>
        </div>
    """, unsafe_allow_html=True)

# Audio recorder
st.markdown("### 🎤 Press to talk:")
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#667eea",
    icon_name="microphone",
    icon_size="3x"
)

# Process audio when recorded
if audio_bytes:
    with st.spinner("🎧 Listening..."):
        # Transcribe audio
        user_text = transcribe_audio(audio_bytes)
        
        if user_text:
            # Add user message to history
            st.session_state.messages.append({
                "role": "user",
                "content": user_text
            })
            
            with st.spinner("🤔 Thinking..."):
                # Get AI response
                ai_response = get_ai_response(user_text, personality)
                
                if ai_response:
                    # Add AI message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    with st.spinner("🔊 Speaking..."):
                        # Convert to speech
                        audio_response = text_to_speech(ai_response, voice_choice)
                        
                        if audio_response:
                            # Autoplay the response
                            autoplay_audio(audio_response)
                            
                            # Also provide download option
                            st.audio(audio_response, format="audio/mp3")
                    
                    st.session_state.conversation_started = True
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <p style='text-align: center; color: white; font-size: 0.9rem;'>
    Made with ❤️ using Streamlit, OpenAI, and Anthropic Claude<br>
    Your AI buddy is powered by Claude 3.5 Sonnet
    </p>
""", unsafe_allow_html=True)
