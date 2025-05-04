import streamlit as st
import speech_recognition as sr
import language_tool_python
from pydub import AudioSegment
import os
import uuid

st.set_page_config(page_title="Grammar Scoring Engine", layout="centered")
st.title("Grammar Scoring Engine for Voice Samples")

# Upload audio
uploaded_file = st.file_uploader("Upload your voice sample (.wav or .mp3)", type=["wav", "mp3"])

def convert_to_wav(audio_bytes, filename, format):
    path = f"{filename}.{format}"
    with open(path, "wb") as f:
        f.write(audio_bytes)
    sound = AudioSegment.from_file(path)
    wav_path = f"{filename}.wav"
    sound.export(wav_path, format="wav")
    os.remove(path)
    return wav_path

def transcribe_audio(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "STT API unavailable"

def score_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    score = max(0, 100 - len(matches) * 5)  # Simple scoring method
    suggestions = [(m.ruleId, m.message) for m in matches]
    return score, suggestions

if uploaded_file is not None:
    ext = uploaded_file.name.split(".")[-1]
    file_id = str(uuid.uuid4())
    st.audio(uploaded_file, format='audio/wav')
    with st.spinner("Transcribing and scoring..."):
        wav_path = convert_to_wav(uploaded_file.read(), file_id, ext)
        transcribed_text = transcribe_audio(wav_path)
        os.remove(wav_path)
        st.subheader("Transcribed Text")
        st.write(transcribed_text)

        if transcribed_text and "Could not" not in transcribed_text:
            score, suggestions = score_grammar(transcribed_text)
            st.subheader("Grammar Score")
            st.write(f"{score} / 100")

            if suggestions:
                st.subheader("Suggestions")
                for rule, msg in suggestions:
                    st.markdown(f"- **{rule}**: {msg}")
            else:
                st.success("Great! No grammar issues found.")
