
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

# Configure the Gemini API Key
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY") # Replace with your actual API key or store in Streamlit secrets
genai.configure(api_key=GOOGLE_API_KEY)

# Function to perform Gemini Multimodal analysis
def generate_gemini_report(image_bytes, stt_text):
    """Generates a report for chip design analysis using Gemini's multimodal capabilities,
    handling images of chip designs or Verilog/VHDL code.
    """

    model = genai.GenerativeModel('gemini-1.5-flash') # or gemini-1.5-pro if you have access

    # Prepare the prompt
    prompt_parts = [
        "You are an AI Chip Design Copilot. Analyze the following information to assist in chip design tasks. The image could be a chip design diagram/schematic/layout OR Verilog/VHDL code. The accompanying speech-to-text (STT) transcription likely contains design notes, requirements, or explanations.  Generate a concise summary report focused on chip design aspects, considering the image type.",
        "If the image is code, focus on identifying potential errors, stylistic issues, areas for optimization, and understanding the code's functionality within a chip design context. If the image is a design diagram, focus on key elements, potential issues, and areas for improvement based on both the visual and textual information.",
        "The report should be technically informative, aimed at assisting chip designers, and provide a clear overview of the design aspects. Consider the STT transcription as context for the image, regardless of the image type.",
        "Image:",
        genai.Part.from_data(image_bytes, mime_type="image/png"),  # Or image/jpeg if applicable
        "Speech-to-text Transcription:",
        stt_text
    ]

    try:
        response = model.generate_content(prompt_parts)
        return response.text  # Extract the generated text
    except Exception as e:
        return f"Error generating report: {e}"

# Main Streamlit app
def main():
    st.title("AI Chip Design Copilot Agent")

    # Sidebar for Uploading Image
    st.sidebar.header("Chip Design Image/Code Upload")
    uploaded_file = st.sidebar.file_uploader("Choose a chip design image (schematic, layout) OR Verilog/VHDL code...", type=["jpg", "jpeg", "png"])

    # Sidebar for Speech-to-Text (STT)
    st.sidebar.header("Speech-to-Text Design Notes")
    stt_input = st.sidebar.text_area("Enter your design notes, requirements, or explanations (Speech-to-Text transcription):")

    # Processing when an image is uploaded
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chip Design Image/Code", use_column_width=True)

        # Convert PIL Image to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG') # Or JPEG
        image_bytes = img_bytes.getvalue()


    else:
        image_bytes = None

    # Report Generation
    if uploaded_file is not None or stt_input:
        st.header("Generated Chip Design Analysis Report")

        if uploaded_file is None:
            st.warning("No image uploaded. The report will be based solely on the design notes (Speech-to-Text input).")
            image_bytes = None  # Ensure it's None for text-only analysis

        if uploaded_file is not None and not stt_input:
            st.warning("No design notes provided. The report will be based solely on the uploaded chip design image/code.")

        try:
            report = generate_gemini_report(image_bytes, stt_input)
            st.write(report)
        except Exception as e:
            st.error(f"Error generating report: {e}")

    else:
        st.info("Please upload a chip design image/code or enter design notes to generate a report.")

if __name__ == "__main__":
    main()
