
# pip install phidata google-generativeai tavily-python
# pip install streamlit
# pip install gTTS
# pip install SpeechRecognition pydub

import streamlit as st
import os
from PIL import Image
from io import BytesIO
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from tempfile import NamedTemporaryFile
from prompts import SYSTEM_PROMPT, INSTRUCTIONS
from gtts import gTTS
import base64
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io  # Import io for BytesIO

os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_KEY']
os.environ['GOOGLE_API_KEY'] = st.secrets['GEMINI_KEY']

MAX_IMAGE_WIDTH = 300

def resize_image_for_display(image_file):
    """Resize image for display only, returns bytes"""
    if isinstance(image_file, str):
        img = Image.open(image_file)
    else:
        img = Image.open(image_file)
        image_file.seek(0)
    
    aspect_ratio = img.height / img.width
    new_height = int(MAX_IMAGE_WIDTH * aspect_ratio)
    img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_resource
def get_agent(system_prompt=SYSTEM_PROMPT, instructions=INSTRUCTIONS):
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp-image-generation"),
        system_prompt=system_prompt,
        instructions=instructions,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )

def analyze_image(image_path, speech_text=""):  # Modified to accept speech_text
    agent = get_agent()
    prompt = "Analyze the given image"
    if speech_text:
        prompt += f" considering the following spoken notes: {speech_text}" #Append speech text as prompt
    with st.spinner('Analyzing image...'):
        response = agent.run(
            prompt,
            images=[image_path],
        )
        st.markdown(response.content)
        return response.content  # Return the content for TTS

def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

def record_audio():
    """Records audio using Streamlit's `st.audio` and returns the audio data."""
    audio_bytes = st.audio(None, format="audio/wav") #Use streamlit audio recorder

    if audio_bytes:
         return audio_bytes
    else :
        return None

def speech_to_text(audio_bytes):
    """Transcribes audio to text using SpeechRecognition."""
    r = sr.Recognizer()
    try:
        # Use BytesIO to work with audio_bytes directly
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes)) # Use BytesIO to read
         # Split audio where silence is 700ms or greater and adjust other parameters as needed
        chunks = split_on_silence(
            audio_segment,
            min_silence_len=500,  # Reduce the minimum silence length (milliseconds)
            silence_thresh=-40,   # Adjust the silence threshold (dBFS)
            keep_silence=250       # Keep some silence after each chunk (milliseconds)
        )
        whole_text = ""
        for i, audio_chunk in enumerate(chunks, start=1):
            # Export audio chunk and save it in a temporary file
            with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                audio_chunk.export(temp_wav.name, format="wav")
                
                # Recognize the chunk
                with sr.AudioFile(temp_wav.name) as source:
                    audio = r.record(source)
                try:
                    text = r.recognize_google(audio)
                except sr.UnknownValueError:
                    text = "Could not understand audio"
                except sr.RequestError as e:
                    text = f"Could not request results from Google Speech Recognition service; {e}"

                whole_text += text + " " # append text
                os.unlink(temp_wav.name) #Remove temp file
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
    st.title("🤖🖥 Design Copilot Agent")

    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = None
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    if 'custom_system_prompt' not in st.session_state:
        st.session_state.custom_system_prompt = SYSTEM_PROMPT
    if 'custom_instructions' not in st.session_state:
        st.session_state.custom_instructions = INSTRUCTIONS
    if 'speech_tab_text' not in st.session_state:
        st.session_state.speech_tab_text = "" #Initialize in session state

    # Record initial instructions from user
    st.subheader("Record Initial Instructions")
    initial_audio_bytes = record_audio()

    if initial_audio_bytes:
        with st.spinner("Transcribing initial instructions..."):
            initial_instructions = speech_to_text(initial_audio_bytes)
            if initial_instructions:
                st.write("Transcribed Instructions:")
                st.write(initial_instructions)
                st.session_state.custom_system_prompt = "You are an AI Agent assistant"  #Override to make a good prompt
                st.session_state.custom_instructions = initial_instructions  #Setting instructions for session


    tab_examples, tab_upload, tab_camera, tab_speech = st.tabs([ #Fixed: Added tab_speech in assignment
        "📚 Example Products", 
        "📤 Upload Image", 
        "📸 Take Photo",
        "🎤 Speech-to-Text" # New Tab
    ])

    with tab_examples:
        example_images = {
            "Chip 1": "images/Chip 1.jpg",
            "Chip 2": "images/Chip 2.jpg",
            "Code 1": "images/Code 1.jpg",
            "Code 2": "images/Code 2.jpg"
        }
        
        cols = st.columns(4)
        for idx, (name, path) in enumerate(example_images.items()):
            with cols[idx]:
                if st.button(name, use_container_width=True):
                    st.session_state.selected_example = path
                    st.session_state.analyze_clicked = False #Reset click


    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload product image", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of IC chip or verilog or VHDL code",
            key="upload_image" # Unique key for image uploader
        )
        
        speech_text = ""  # Initialize an empty variable for speech_text.
        audio_bytes = record_audio()  #Record audio with streamlit 

        if uploaded_file:
            resized_image = resize_image_for_display(uploaded_file)
            st.image(resized_image, caption="Uploaded Image", use_container_width=False, width=MAX_IMAGE_WIDTH)
        
        if audio_bytes:
            with st.spinner("Transcribing Audio..."): # Add a spinner to show that audio is processing
                speech_text = speech_to_text(audio_bytes)
                if speech_text:
                    st.write("Transcription:")
                    st.write(speech_text) # Print audio transcribed text

        #Use transcription stored from speech tab
        if 'speech_tab_text' in st.session_state:
            speech_text = st.session_state.speech_tab_text
        
        if uploaded_file and st.button("🔍 Analyze Uploaded Image with Audio", key="analyze_upload_audio"):
            temp_path = save_uploaded_file(uploaded_file)
            analysis_result = analyze_image(temp_path, speech_text) #Pass speech text to analysis
            os.unlink(temp_path)
            if analysis_result:  # Check if there's text output
                audio_html = text_to_speech(analysis_result)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)
  
    with tab_camera:
        camera_photo = st.camera_input("Take a picture of the IC chip or verilog or VHDL code", key="camera_input")  #Unique key
        audio_bytes = record_audio()  #Record audio with streamlit 

        speech_text = ""  # Initialize an empty variable for speech_text.


        if camera_photo:
            resized_image = resize_image_for_display(camera_photo)
            st.image(resized_image, caption="Captured Photo", use_container_width=False, width=MAX_IMAGE_WIDTH)

        if audio_bytes:
            with st.spinner("Transcribing Audio..."): # Add a spinner to show that audio is processing
                speech_text = speech_to_text(audio_bytes)
                if speech_text:
                    st.write("Transcription:")
                    st.write(speech_text) # Print audio transcribed text
        
        #Use transcription stored from speech tab
        if 'speech_tab_text' in st.session_state:
            speech_text = st.session_state.speech_tab_text


        if camera_photo and st.button("🔍 Analyze Captured Photo with Audio", key="analyze_camera_audio"):
            temp_path = save_uploaded_file(camera_photo)
            analysis_result = analyze_image(temp_path, speech_text)  # Pass speech text to analysis
            os.unlink(temp_path)
            if analysis_result:  # Check if there's text output
                audio_html = text_to_speech(analysis_result)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)

    with tab_speech:
        st.subheader("Speech-to-Text Interface")
        
        speech_audio_bytes = record_audio()
        
        if speech_audio_bytes:
            with st.spinner("Transcribing Audio..."):
                speech_tab_text = speech_to_text(speech_audio_bytes)
                if speech_tab_text:
                    st.write("Transcribed Text:")
                    st.write(speech_tab_text)
                    st.session_state.speech_tab_text = speech_tab_text  #Store for access later.

        st.write("You can use the transcribed text in other tabs now.")


    if st.session_state.selected_example:
        st.divider()
        st.subheader("Selected image")
        resized_image = resize_image_for_display(st.session_state.selected_example)
        st.image(resized_image, caption="Selected Example", use_container_width=False, width=MAX_IMAGE_WIDTH)
        
        audio_bytes = record_audio()
        speech_text = "" # Initiliaze Text

        if audio_bytes:
            with st.spinner("Transcribing Audio..."): # Add a spinner to show that audio is processing
                speech_text = speech_to_text(audio_bytes)
                if speech_text:
                    st.write("Transcription:")
                    st.write(speech_text) # Print audio transcribed text
        
        #Use transcription stored from speech tab
        if 'speech_tab_text' in st.session_state:
            speech_text = st.session_state.speech_tab_text


        if st.button("🔍 Analyze Example with Audio", key="analyze_example_audio") and not st.session_state.analyze_clicked: #Modified Button and ensure that click will not trigger again
            st.session_state.analyze_clicked = True #Ensure button can't trigger again
            
            #Get Agent with custom system prompt and instructions
            agent = get_agent(system_prompt = st.session_state.custom_system_prompt, instructions = st.session_state.custom_instructions)
            temp_path = st.session_state.selected_example
            prompt = "Analyze the given image"
            if speech_text:
                prompt += f" considering the following spoken notes: {speech_text}" #Append speech text as prompt
            with st.spinner('Analyzing image...'):
                response = agent.run(
                    prompt,
                    images=[temp_path],
                )
                analysis_result = response.content
                st.markdown(analysis_result)
            
            if analysis_result:  # Check if there's text output
                audio_html = text_to_speech(analysis_result)
                if audio_html:
                    st.markdown(audio_html, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Design copilot/assistant Agent",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
