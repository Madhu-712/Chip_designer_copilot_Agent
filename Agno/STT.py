
# Required installations:
# pip install streamlit
# pip install SpeechRecognition pyaudio
# pip install phidata google-generativeai tavily-python

import streamlit as st
import os
from PIL import Image
from io import BytesIO
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from tempfile import NamedTemporaryFile
import speech_recognition as sr

# Set environment variables for API keys
os.environ['TAVILY_API_KEY'] = st.secrets['TAVILY_KEY']
os.environ['GOOGLE_API_KEY'] = st.secrets['GEMINI_KEY']

# Constants
MAX_IMAGE_WIDTH = 300

# System Prompt and Instructions
SYSTEM_PROMPT = """
You are an expert chip design agent. Analyze the uploaded image, which may contain IC chip designs, Verilog/VHDL code, or circuit diagrams. Generate a detailed report on the chip's architecture, including optimization techniques and potential areas for improvement.
"""

INSTRUCTIONS = """
1. Analyze the uploaded image or provided content to extract meaningful details about the chip design.
2. Provide a comprehensive report covering:
   - Architecture details of the chip.
   - Identification of key modules or components.
   - Suggestions for optimization techniques.
   - Any potential areas for improvement in the design.
3. Ensure the output is easy to understand for both technical and non-technical users.
"""

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
def get_agent():
    return Agent(
        model=Gemini(id="gemini-2.0-flash-exp-image-generation"),
        system_prompt=SYSTEM_PROMPT,
        instructions=INSTRUCTIONS,
        tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
        markdown=True,
    )

def analyze_image(image_path):
    agent = get_agent()
    with st.spinner('Analyzing image...'):
        response = agent.run(
            "Analyze the given image",
            images=[image_path],
        )
        st.markdown(response.content)
        return response.content  # Return the analysis result

def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

def speech_to_text():
    """Converts speech input from microphone to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak into the microphone.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            st.success(f"Recognized Speech: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
        return None

def main():
    st.title("🤖🖥 Design Copilot Agent")
    
    if 'analyze_clicked' not in st.session_state:
        st.session_state.analyze_clicked = False
    
    tab_speech, tab_upload = st.tabs([
        "🎤 Speech Input", 
        "📤 Upload Image"
    ])
    
    with tab_speech:
        st.header("🎤 Speech Input for Analysis")
        if st.button("Record Speech"):
            user_query = speech_to_text()
            if user_query:
                st.write(f"Your query: {user_query}")
                st.info("Use the 'Upload Image' tab to upload an image for analysis.")

    with tab_upload:
        st.header("📤 Upload Image for Analysis")
        uploaded_file = st.file_uploader(
            "Upload product image", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of IC chip or Verilog/VHDL code"
        )
        if uploaded_file:
            resized_image = resize_image_for_display(uploaded_file)
            st.image(resized_image, caption="Uploaded Image", use_column_width=False, width=MAX_IMAGE_WIDTH)
            if st.button("🔍 Analyze Uploaded Image", key="analyze_upload"):
                temp_path = save_uploaded_file(uploaded_file)
                analysis_result = analyze_image(temp_path)  # Get the output of analysis
                os.unlink(temp_path)
                if analysis_result:  # Check if there's text output
                    st.write(analysis_result)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Design Copilot/Assistant Agent",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    main()
