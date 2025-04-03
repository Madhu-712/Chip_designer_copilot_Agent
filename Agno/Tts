# pip install phidata google-generativeai tavily-python
# pip install streamlit
# pip install gTTS

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
        return response.content  # Return the content for TTS

def save_uploaded_file(uploaded_file):
    with NamedTemporaryFile(dir='.', suffix='.jpg', delete=False) as f:
        f.write(uploaded_file.getbuffer())
        return f.name

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
    
    tab_examples, tab_upload, tab_camera = st.tabs([
        "📚 Example Products", 
        "📤 Upload Image", 
        "📸 Take Photo"
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
                    st.session_state.analyze_clicked = False
    
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload product image", 
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of IC chip or verilog or VHDL code"
        )
        if uploaded_file:
            resized_image = resize_image_for_display(uploaded_file)
            st.image(resized_image, caption="Uploaded Image", use_container_width=False, width=MAX_IMAGE_WIDTH)
            if st.button("🔍 Analyze Uploaded Image", key="analyze_upload"):
                temp_path = save_uploaded_file(uploaded_file)
                analysis_result = analyze_image(temp_path) # get the output of analysis
                os.unlink(temp_path)
                if analysis_result: # Check if there's text output
                    audio_html = text_to_speech(analysis_result)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
                
    
    with tab_camera:
        camera_photo = st.camera_input("Take a picture of the IC chip or verilog or VHDL code")
        if camera_photo:
            resized_image = resize_image_for_display(camera_photo)
            st.image(resized_image, caption="Captured Photo", use_container_width=False, width=MAX_IMAGE_WIDTH)
            if st.button("🔍 Analyze Captured Photo", key="analyze_camera"):
                temp_path = save_uploaded_file(camera_photo)
                analysis_result = analyze_image(temp_path) # get the output of analysis
                os.unlink(temp_path)
                if analysis_result: # Check if there's text output
                    audio_html = text_to_speech(analysis_result)
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
    
    if st.session_state.selected_example:
        st.divider()
        st.subheader("Selected image")
        resized_image = resize_image_for_display(st.session_state.selected_example)
        st.image(resized_image, caption="Selected Example", use_container_width=False, width=MAX_IMAGE_WIDTH)
        
        if st.button("🔍 Analyze Example", key="analyze_example") and not st.session_state.analyze_clicked:
            st.session_state.analyze_clicked = True
            analysis_result = analyze_image(st.session_state.selected_example)
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
