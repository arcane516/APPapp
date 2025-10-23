import io
import os
import tempfile
import hashlib
from typing import List, Dict, Optional

import streamlit as st
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder


def get_api_key_from_inputs() -> Optional[str]:
    if "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    session_key = st.session_state.get("_user_openai_api_key")
    if session_key:
        return session_key
    return None


def ensure_client() -> Optional[OpenAI]:
    api_key = get_api_key_from_inputs()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def get_persona_prompt(flavor: str) -> str:
    base = (
        "You are an always-on voice buddy. Keep replies brief, friendly, and natural. "
        "Ask short follow-ups sometimes. Avoid lists; speak like a human friend."
    )
    vibes = {
        "Best friend": "Your tone is warm, playful, and supportive.",
        "Chill buddy": "Your tone is relaxed, low-key, with calm reassurance.",
        "Motivational coach": "Your tone is energizing and encouraging; keep it positive and concise.",
        "Therapist vibe": "Your tone is empathetic and reflective; validate feelings and ask gentle questions.",
        "Comedian": "Your tone is witty and light; sprinkle gentle humor without being mean.",
    }
    return f"{base} {vibes.get(flavor, '')}"


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []  # type: List[Dict[str, str]]
    if "last_audio_sha" not in st.session_state:
        st.session_state["last_audio_sha"] = None


def show_header() -> None:
    st.set_page_config(page_title="Voice Buddy", page_icon="🎙️", layout="centered")
    st.title("🎙️ Voice Buddy")
    st.caption("Talk to an AI buddy that vibes with you in real-time.")


def sidebar_controls() -> Dict[str, str]:
    with st.sidebar:
        st.header("Settings")
        st.text("Provide your API key once per session.")
        user_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Stored only in your local session.",
        )
        if user_key:
            st.session_state["_user_openai_api_key"] = user_key

        persona = st.selectbox(
            "Buddy vibe",
            [
                "Best friend",
                "Chill buddy",
                "Motivational coach",
                "Therapist vibe",
                "Comedian",
            ],
            index=0,
        )

        voice = st.selectbox("Voice", ["alloy", "verse"], index=0)
        auto_tts = st.toggle("Auto speak replies", value=True)
        return {"persona": persona, "voice": voice, "auto_tts": str(auto_tts)}


def render_history() -> None:
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def add_message(role: str, content: str) -> None:
    st.session_state["messages"].append({"role": role, "content": content})


def transcribe_audio(client: OpenAI, audio_bytes: bytes) -> Optional[str]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", file=f
            )
        text = getattr(result, "text", None)
        return text
    except Exception as e:  # noqa: BLE001
        st.error(f"Transcription failed: {e}")
        return None
    finally:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:  # noqa: BLE001
            pass


def get_chat_reply(client: OpenAI, persona: str, user_text: str) -> Optional[str]:
    try:
        system_prompt = get_persona_prompt(persona)
        messages: List[Dict[str, str]] = (
            [{"role": "system", "content": system_prompt}]
            + st.session_state["messages"]
            + [{"role": "user", "content": user_text}]
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            messages=messages,
        )
        return resp.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        st.error(f"Chat failed: {e}")
        return None


def synthesize_speech(client: OpenAI, text: str, voice: str) -> Optional[bytes]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts", voice=voice, input=text
        ) as response:
            response.stream_to_file(tmp_path)
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        return audio_bytes
    except Exception as e:  # noqa: BLE001
        st.error(f"TTS failed: {e}")
        return None
    finally:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:  # noqa: BLE001
            pass


def main() -> None:
    show_header()
    init_state()
    controls = sidebar_controls()

    client = ensure_client()
    if not client:
        st.info(
            "Set your OpenAI API key in the sidebar, or as `OPENAI_API_KEY` env var."
        )

    render_history()

    st.divider()
    st.subheader("Talk")
    st.caption("Click to record. Release to stop. We'll transcribe and reply.")

    audio_bytes = audio_recorder(
        energy_threshold=(-1.0, 1.0),  # pass-through; let backend infer
        pause_threshold=1.0,
        sample_rate=44_100,
        text="Hold to talk" if st.session_state.get("record_hold", True) else "Record",
        icon_size="2x",
        key="voice_rec",
    )

    if audio_bytes:
        audio_sha = hashlib.sha256(audio_bytes).hexdigest()
        if audio_sha != st.session_state.get("last_audio_sha"):
            st.session_state["last_audio_sha"] = audio_sha
            st.audio(audio_bytes, format="audio/wav")

            if client:
                user_text = transcribe_audio(client, audio_bytes)
                if user_text:
                    add_message("user", user_text)
                    with st.chat_message("user"):
                        st.markdown(user_text)

                    reply = get_chat_reply(client, controls["persona"], user_text)
                    if reply:
                        add_message("assistant", reply)
                        with st.chat_message("assistant"):
                            st.markdown(reply)

                        if controls["auto_tts"] == "True":
                            tts_audio = synthesize_speech(
                                client, reply, controls["voice"]
                            )
                            if tts_audio:
                                st.audio(tts_audio, format="audio/mp3")
            else:
                st.warning("Add your API key to enable transcription and replies.")

    st.divider()
    st.subheader("Type instead")
    typed = st.chat_input("Say something to your buddy…")
    if typed and client:
        add_message("user", typed)
        with st.chat_message("user"):
            st.markdown(typed)
        reply = get_chat_reply(client, controls["persona"], typed)
        if reply:
            add_message("assistant", reply)
            with st.chat_message("assistant"):
                st.markdown(reply)
            if controls["auto_tts"] == "True":
                tts_audio = synthesize_speech(client, reply, controls["voice"])
                if tts_audio:
                    st.audio(tts_audio, format="audio/mp3")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset conversation"):
            st.session_state["messages"] = []
            st.session_state["last_audio_sha"] = None
            st.experimental_rerun()
    with col2:
        st.caption("Made with ❤️ for cozy chats.")


if __name__ == "__main__":
    main()

