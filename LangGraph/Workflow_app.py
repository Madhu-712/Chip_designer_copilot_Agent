

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import re
from typing import List

def llm_call(prompt: str, system_prompt: str = "", llm: ChatGroq = None) -> str:
    """Calls the LLM with the given prompt and returns the response."""
    if system_prompt:
        prompt = f"{system_prompt}\n{prompt}"
    response = llm.invoke(prompt)
    return response.content

def extract_xml(text: str, tag: str) -> str:
    """Extracts the content of the specified XML tag from the given text."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""

def chain(input: str, prompts: List[str], llm: ChatGoogleGenerativeAI) -> str:
    """Chain multiple LLM calls sequentially, passing results between steps."""
    result = input
    for i, prompt in enumerate(prompts, 1):
        print(f"\nStep {i}:")
        result = llm_call(f"{prompt}\nInput: {result}", llm=llm)
        print(result)
    return result

st.title("Chip Design Copilot")

# Input for Verilog code
verilog_code = st.text_area("Enter your Verilog code here:", value="""
// Example Verilog code
module example (
  input clk,
  input rst,
  // ... other inputs and outputs
);
// ... your Verilog code ...
endmodule
""")

# Define the prompt chaining steps
data_processing_steps = [
    """Analyze the uploaded Verilog code, offer suggestions for optimization and debugging.""",
    f"""Verilog code: \n
""",
    """Highlight any potential issues or areas for improvement in the design, including:
        * Performance
        * Reliability
        * Cost
        * Security
        * Area
        * Pin count
        * Manufacturing complexity""",
    """Suggest how the traditional chip design can be upgraded with AI capabilities.""",
    """Generate a blueprint report of the chip design, detailing:
        * The current architecture and its analysis
        * Suggested improvements for optimization covering performance, reliability, cost, security, area, pin count, and manufacturing complexity
        * How AI can be incorporated into the existing design""",
    """Mention and describe the changes incorporated during the upgrade to AI-enhanced design.""",
    """Use technical terminology appropriately and provide explanations for complex concepts.""",
    """Present the information in a clear and organized manner. Use headings, bullet points, and formatting to enhance readability.""",
    """Remember the user may not be an expert in chip design; explain technical concepts in simple terms.""",
]

# Define the initial input (Designcopilot)
Designcopilot = """Expert Chip Design Copilot Agent specializing in analyzing Verilog code. Your role is to assist users in understanding and improving their chip designs by providing detailed analysis, insights, and optimization suggestions. You combine technical knowledge to deliver comprehensive and actionable information for users. Your guidance accelerates the design process, offering prescriptive insights and recommendations. Return your response in Markdown format."""

# Button to trigger report generation
if st.button("Generate Report"):
    # Initialize Gemini
   # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
     # Initialize Groq LLM
    llm = ChatGroq(model_name="deepseek-r1-distill-qwen-32b", temperature=0)  # Replace with your Groq model
    # Perform prompt chaining
    formatted_result = chain(Designcopilot, data_processing_steps, llm)

    # Display the generated report
    st.markdown(formatted_result)
