
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def llm_call(prompt: str, system_prompt: str = "", llm: Optional[ChatGoogleGenerativeAI] = None) -> str:
    """Calls the LLM with the given prompt and returns the response."""
    try:
        if system_prompt:
            prompt = f"{system_prompt}\n{prompt}"
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error("Error during LLM call: %s", e)
        return "An error occurred during the LLM call."

def extract_xml(text: str, tag: str) -> str:
    """Extracts the content of the specified XML tag from the given text."""
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""

def chain(input: str, prompts: List[str], llm: ChatGoogleGenerativeAI) -> str:
    """Chain multiple LLM calls sequentially, passing results between steps."""
    result = input
    for i, prompt in enumerate(prompts, 1):
        logger.info(f"Step {i}:")
        try:
            result = llm_call(f"{prompt}\nInput: {result}", llm=llm)
        except Exception as e:
            logger.error("Error during chaining at step %d: %s", i, e)
            return "An error occurred during the chaining process."
        logger.info(result)
    return result

def main():
    st.title("Chip Design Copilot Agentic Workflow using LangGraph")

    

    # Define the prompt chaining steps
    data_processing_steps = [
        """Act like a expert chip design Copilot \n""",
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
    design_copilot = """Expert Chip Design Copilot Agent specializing in analyzing Verilog code. Your role is to assist users in understanding and improving their chip designs by providing detailed analysis and suggestions."""

    # Button to trigger report generation
    if st.button("Generate Report"):
        # Initialize Google Generative AI
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)  # Replace with your Google model
        # Perform prompt chaining
        formatted_result = chain(design_copilot, data_processing_steps, llm)

        # Display the generated report
        st.markdown(formatted_result)

if __name__ == "__main__":
    main()
