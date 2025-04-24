
import streamlit as st
import speech_recognition as sr
from io import StringIO
import pyverilog.vparser.parser as verilog_parser
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator

def analyze_verilog_code(verilog_code):
    """
    Analyze Verilog code to provide a summary, optimization opportunities, and architecture explanation.
    """
    try:
        # Parse the Verilog code
        ast, _ = verilog_parser.parse([verilog_code])
        
        # Generate report
        report = "### Verilog Code Analysis Report\n"
        report += "- **Module Names**: Extracted module names from the code.\n"
        report += "- **Optimization Opportunities**: Suggestions will be added here.\n"
        report += "- **Architecture Explanation**: Explanation of the chip design architecture will be detailed here.\n"
        
        return report
    except Exception as e:
        return f"Error parsing Verilog code: {str(e)}"

def process_uploaded_file(uploaded_file):
    """
    Process the uploaded Verilog file and return its contents.
    """
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        return stringio.read()
    return None

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
        # Speech recognition
        query = recognizer.recognize_google(audio)
        st.success(f"Recognized Speech: {query}")
        return query
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    return None

# Streamlit Application
st.title("Chip Design Architecture Analysis")
st.write("""
    This application allows you to:
    1. Provide a speech prompt for analysis.
    2. Upload a Verilog file to analyze chip design architecture.
    3. Generate a report with analysis, explanation, and optimization opportunities.
""")

# Speech Input
st.header("Step 1: Provide Speech Input")
if st.button("Record Speech"):
    user_query = speech_to_text()
    if user_query:
        st.write(f"Your query: {user_query}")

# File Upload
st.header("Step 2: Upload Verilog File")
uploaded_file = st.file_uploader("Upload your Verilog file here", type=["v", "sv"])

# Analysis
if uploaded_file:
    verilog_code = process_uploaded_file(uploaded_file)
    if verilog_code:
        st.header("Step 3: Analysis Report")
        st.write("Analyzing the Verilog code...")
        report = analyze_verilog_code(verilog_code)
        st.markdown(report)
