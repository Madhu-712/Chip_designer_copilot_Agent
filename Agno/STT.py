
# pip install streamlit speech_recognition pydub gTTS

import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io
from gtts import gTTS
import base64

def record_audio():
    """Records audio using Streamlit's `st.audio` and returns the audio data."""
    audio_bytes = st.audio(None, format="audio/wav")  # Use streamlit audio recorder

    if audio_bytes:
        return audio_bytes
    else:
        return None

def speech_to_text(audio_bytes):
    """Transcribes audio to text using SpeechRecognition."""
    r = sr.Recognizer()
    try:
        # Use BytesIO to work with audio_bytes directly
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))  # Use BytesIO to read
        # Split audio where silence is 700ms or greater and adjust other parameters as needed
        chunks = split_on_silence(
            audio_segment,
            min_silence_len=500,  # Reduce the minimum silence length (milliseconds)
            silence_thresh=-40,  # Adjust the silence threshold (dBFS)
            keep_silence=250,  # Keep some silence after each chunk (milliseconds)
        )
        whole_text = ""
        for i, audio_chunk in enumerate(chunks, start=1):
            # Export audio chunk and save it in a temporary file
            with io.BytesIO() as temp_wav:  # Use BytesIO directly
                audio_chunk.export(temp_wav, format="wav")  # Export to BytesIO
                temp_wav.seek(0)  # Reset the buffer position

                # Recognize the chunk
                with sr.AudioFile(temp_wav) as source:
                    audio = r.record(source)
                try:
                    text = r.recognize_google(audio)
                except sr.UnknownValueError:
                    text = "Could not understand audio"
                except sr.RequestError as e:
                    text = f"Could not request results from Google Speech Recognition service; {e}"

                whole_text += text + " "  # append text
        return whole_text
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def text_to_speech(text):
    """Converts the given text to speech and returns a playable audio widget."""
    try:
        tts = gTTS(text=text, lang='en')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        data_url = "data:audio/mp3;base64," + base64.b64encode(mp3_fp.read()).decode()
        return f"""
        <audio controls autoplay>
            <source src="{data_url}" type="audio/mp3">
        </audio>
        """
    except Exception as e:
        st.error(f"Error generating TTS: {e}")
        return None

def main():
    st.title("Speech-to-Text Application")

    # Instructions for the user
    st.write("Click the 'Record' button below to start recording audio.")
    st.write("After recording, the transcribed text will be displayed, along with an option to play the text as speech.")

    # Record audio
    audio_bytes = record_audio()

    if audio_bytes:
        with st.spinner("Transcribing audio..."):
            # Transcribe audio to text
            transcribed_text = speech_to_text(audio_bytes)

            if transcribed_text:
                st.subheader("Transcribed Text:")
                st.write(transcribed_text)

                # Text-to-speech option
                st.subheader("Text-to-Speech:")
                if st.button("Play as Speech"):
                    audio_html = text_to_speech(transcribed_text)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.warning("Could not transcribe the audio. Please try again.")
    else:
        st.info("Click the audio recorder to start recording your speech.")

if __name__ == "__main__":
    main()
