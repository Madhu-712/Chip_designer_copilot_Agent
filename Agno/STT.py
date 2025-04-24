
import streamlit as st
import speech_recognition as sr
import pytesseract
from PIL import Image

def speech_to_text():
    """
    Convert speech input to text using SpeechRecognition library.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        st.info("Listening... Please speak your query.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Web Speech API
        query = recognizer.recognize_google(audio)
        st.success(f"Recognized Speech: {query}")
        return query
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    return None

def process_image(image):
    """
    Process the uploaded image and extract text using OCR.
    """
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error processing image: {str(e)}"

# Streamlit Application
st.title("Chip Design Architecture Analysis")
st.write("""
    This application allows you to:
    1. Provide a speech prompt for analysis.
    2. Upload an image containing Verilog/VHDL code or a circuit diagram.
    3. Generate a report or answer based on the content.
""")

# Speech Input
st.header("Step 1: Provide Speech Input")
if st.button("Record Speech"):
    user_query = speech_to_text()
    if user_query:
        st.write(f"Your query: {user_query}")

# Image Upload
st.header("Step 2: Upload Image")
uploaded_image = st.file_uploader("Upload an image (Verilog/VHDL code or Circuit Diagram)", type=["png", "jpg", "jpeg"])

# Analysis
if uploaded_image:
    st.header("Step 3: Analysis Report")
    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.write("Extracting text from the image...")
    extracted_text = process_image(Image.open(uploaded_image))
    
    if extracted_text:
        st.subheader("Extracted Text")
        st.text(extracted_text)
        st.subheader("Analysis and Recommendations")
        st.write("Further analysis of the content will be implemented here.")
    else:
        st.error("No text found in the image or an error occurred.")
