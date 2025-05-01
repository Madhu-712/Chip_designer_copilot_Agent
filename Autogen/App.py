

import streamlit as st
import autogen
import os
import subprocess
import warnings

# Install necessary packages if not already installed
try:
    import autogen
except ImportError:
    st.write("Installing autogen...")
    subprocess.run(["pip", "install", "autogen"])
    import autogen



# Ollama installation and setup
try:
    import ollama
except ImportError:
    st.write("Installing and setting up Ollama...")
    subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"])
    import ollama

try:
    subprocess.Popen(["ollama", "serve"])
except FileNotFoundError:
    st.error("Ollama not found in PATH. Please install or add to PATH.")
except OSError as e:
    st.error(f"Error starting Ollama server: {e}")
subprocess.Popen(["ollama", "serve"])
subprocess.run(["ollama", "pull", "llama3.2:1b"])

os.environ['OAI_CONFIG_LIST'] ='[{"model": "llama3.2:1b","api_key": "EMPTY", "max_tokens":1000}]'

# AutoGen configuration
llm_config={
    "timeout": 600,
    "cache_seed": 68,
    "config_list": autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={"model": ["llama3.2:1b"]},
    ),
    "temperature": 0.5,
}

llm_config['config_list'][0]["base_url"] = f"http://localhost:11434/v1"

# Suppress warnings
warnings.filterwarnings("ignore")

# Agent definitions
from autogen import UserProxyAgent, AssistantAgent

def termination_message(msg: str) -> bool:
    content = msg.get("content", "").lower()
    return "terminate" in content

user_proxy = UserProxyAgent(
    name="User",
    llm_config=False,
    is_termination_msg=termination_message,
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
)

Orchestrator = AssistantAgent(
    name="OrchestratorAgent",
    description="Orchestrates the interactions between AI model Agent and Design Agent.The Orchestrator agent maintains the overall quality and consistency of Final design",
    system_message="""Manage the entire AI-assisted chip design workflow for an IT startup ensuring seamless integration of AI suggestions and maintaining design integrity.""",
    llm_config=llm_config,
)

AI_model = AssistantAgent(
    name="AI_modelAgent",
    description="This Agent analyze the provided chip design data using pre-trained AI models to identify potential bugs, suggest optimizations ,Power consumption, area, performance,reliability and cost. Provide predictions.",
    system_message="""Analyze chip design data using pre-trained AI models and provide actionable suggestions for bug detection,optimization, and other improvements.A structured report including flagged potential bugs, specific optimization suggestions (with justifications), and predictions """,
    llm_config=llm_config,
)

Design = AssistantAgent(
    name="Design_assistant_agent",
    description ="This agent possesses deep expertise in EDA (Electronic design automation)tools and the intricacies of chip design,chip architecture.It acts as a gatekeeper, carefully reviewing AI suggestions before they are integrated.The Design Agent prioritizes design quality and reliability, preventing the introduction of errors or undesirable trade-offs.",
    system_message="""Act like a Design Assistant or coworker. Evaluate AI-generated suggestions for feasibility, correctness and compliance with design constraint ensuring the design's integrity and functionality.""",
    llm_config=llm_config,
)

groupchat = autogen.GroupChat(agents=[user_proxy, Orchestrator, AI_model, Design], messages=[], max_round=6)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Streamlit UI
st.title("Chip Design Assistant")

user_input = st.text_area("Enter your chip design query:")

if st.button("Submit"):
    with st.spinner("Generating report..."):
        response = user_proxy.initiate_chat(
            manager, message=user_input
        )
        st.write(response)
