
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the LLM
llm = ChatGoogleGenerativeAI(temperature=0.0)

st.title("Designer Copilot Agent")

# Add examples
st.markdown("**Example Queries:**")
st.markdown("- How can I optimize the power consumption of my chip design?")
st.markdown("- What are the latest trends in AI-based chip design?")
st.markdown("- Can you suggest ways to improve the reliability of my ASIC?")

user_input = st.text_input("Enter your chip design query:")

if user_input:
    # Define the prompt
    prompt = f"""
    Act as an expert Chip Design Copilot Agent.
    You are tasked with assisting designers in optimizing chip designs.
    Consider factors like performance, reliability, cost, security, area, pin count, and manufacturing complexity.

    User query: {user_input}

    Provide a detailed report with recommendations in Markdown format.
    """

    # Get LLM response
    response = llm.invoke(prompt).content

    # Display the response
    st.markdown(response)
