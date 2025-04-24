
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
from tavily import TavilyClient

# Configure the Gemini API Key
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")  # Replace with your actual API key or store in Streamlit secrets
genai.configure(api_key=GOOGLE_API_KEY)

# Configure the Tavily API Key
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")  # Store in Streamlit secrets

# Initialize Tavily Client (only if an API key is available)
tavily = None
if TAVILY_API_KEY:
    try:
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        st.error(f"Error initializing Tavily Client: {e}")
        tavily = None # Ensure tavily is None if initialization fails
else:
    st.warning("Tavily API Key not found. Web search capabilities will be limited.")

# Function to perform Gemini Multimodal analysis, potentially using Tavily for search
def generate_gemini_report(image_bytes, stt_text, tavily_client=None):
    """Generates a report for chip design analysis using Gemini's multimodal capabilities,
    handling images of chip designs or Verilog/VHDL code, and potentially using Tavily for web search.
    """

    model = genai.GenerativeModel('gemini-1.5-flash') # or gemini-1.5-pro if you have access

    # Prepare the prompt
    prompt_parts = [
        "You are an AI Chip Design Copilot. Analyze the following information to assist in chip design tasks. The image could be a chip design diagram/schematic/layout OR Verilog/VHDL code. The accompanying speech-to-text (STT) transcription likely contains design notes, requirements, or explanations.  Generate a concise summary report focused on chip design aspects, considering the image type.",
        "If the image is code, focus on identifying potential errors, stylistic issues, areas for optimization, and understanding the code's functionality within a chip design context. If the image is a design diagram, focus on key elements, potential issues, and areas for improvement based on both the visual and textual information.",
        "The report should be technically informative, aimed at assisting chip designers, and provide a clear overview of the design aspects. Consider the STT transcription as context for the image, regardless of the image type.",
        "Optionally, use web search to find relevant information. For example, if the design mentions a specific technology or component, search for datasheets or application notes. If analyzing code, search for examples or explanations of specific functions or libraries. If you use search, clearly cite the source of the information.",
        "Image:",
        genai.Part.from_data(image_bytes, mime_type="image/png"),  # Or image/jpeg if applicable
        "Speech-to-text Transcription:",
        stt_text,
    ]

    # Example of using Tavily (conditional on tavily_client being available)
    if tavily_client and stt_text: # Only search if we have a tavily client and STT input to search with
        try:
            search_results = tavily_client.search(query=stt_text, search_interval="7d")  # Search for the STT transcription itself
            prompt_parts.append("Web Search Results (from Tavily):")
            prompt_parts.append(search_results)
        except Exception as e:
            st.warning(f"Error during Tavily search: {e}")

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
    uploaded_file = st.sidebar.file_uploader(
        "Choose a chip design image (schematic, layout) OR Verilog/VHDL code...",
        type=["jpg", "jpeg", "png"],
    )

    image_bytes = None  # Initialize image_bytes outside the if block

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chip Design Image/Code", use_column_width=True)

        # Convert PIL Image to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")  # Or JPEG
        image_bytes = img_bytes.getvalue()

    analyze_image_button = st.button("Analyze Image")

    # Sidebar for Speech-to-Text (STT)
    st.sidebar.header("Speech-to-Text Design Notes")
    stt_input = st.sidebar.text_area(
        "Enter your design notes, requirements, or explanations (Speech-to-Text transcription):",
        disabled=not analyze_image_button, #Disable speech to text until image has been analyzed.
    )

    generate_report_button = st.button("Generate Report", disabled=not (analyze_image_button and (uploaded_file is not None or stt_input))) #Disable button till image analyzed

    # Report Generation
    if generate_report_button:
        st.header("Generated Chip Design Analysis Report")

        if uploaded_file is None:
            st.warning("No image uploaded. The report will be based solely on the design notes (Speech-to-Text input).")
            image_bytes = None  # Ensure it's None for text-only analysis

        if uploaded_file is not None and not stt_input:
            st.warning("No design notes provided. The report will be based solely on the uploaded chip design image/code.")

        try:
            report = generate_gemini_report(image_bytes, stt_input, tavily_client=tavily)  # Pass the Tavily client
            st.write(report)
        except Exception as e:
            st.error(f"Error generating report: {e}")

    else:
        st.info("Upload a chip design image/code and click 'Analyze Image'. Then, enter design notes and click 'Generate Report'.")


if __name__ == "__main__":
    main()
