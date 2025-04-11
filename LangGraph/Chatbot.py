



import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command
import os
from langchain.schema import HumanMessage  # Import HumanMessage

# Ensure secrets are loaded correctly
try:
    os.environ['TAVILY_API_KEY'] = st.secrets["TAVILY_KEY"]
    os.environ['GOOGLE_API_KEY'] = st.secrets["GEMINI_KEY"]
except KeyError as e:
    st.error(f"Missing secret key: {e}. Please configure your Streamlit secrets.")
    st.stop()

# Define State and Graph
class State(TypedDict):
    messages: Annotated[List[dict], add_messages]

graph_builder = StateGraph(State)

# Human assistance tool
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human via Streamlit."""
    human_input = st.text_input(f"Human assistance needed for: {query}", key=f"human_input_{query}")
    if human_input:
        return human_input
    return "Waiting for human input..."

# Initialize LLM and Tools
tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0) 
llm_with_tools = llm.bind_tools(tools)

# Chatbot function (Improved handling of tool calls and errors)
def chatbot(state: State):
    try:
        message = llm_with_tools.invoke(state["messages"])
        for tool_call in message.tool_calls:
            try:
                tool_result = tool_call.run(tool_call.kwargs)
                state["messages"].append({"role": "tool", "content": tool_result})
            except Exception as e:
                state["messages"].append({"role": "tool", "content": f"Error: {e}"})  # Handle the error with a message
        state["messages"].append({"role": "assistant", "content": message.content})  # Append assistant's message after tool calls
    except Exception as e:
        st.error(f"An error occurred: {e}")  # Handle the general error with a message
        state["messages"].append({"role": "assistant", "content": "Sorry, I encountered an error."})
    return state

# Graph setup
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Initialize memory and compile the graph
# memory = MemorySaver()  # If you need to save and load state, uncomment this line
graph = graph_builder.compile() #checkpointer=memory) # If using memory, uncomment this line

# Streamlit UI
st.title("Chip Design Chatbot")

# Add examples
st.markdown("**Example Queries:**")
st.markdown("- How can I optimize the power consumption of my chip design?")
st.markdown("- What are the latest trends in AI-based chip design?")
st.markdown("- Can you suggest ways to improve the reliability of my ASIC?")

# Display and handle chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    

for message in st.session_state.messages:
    if isinstance(message, HumanMessage):  # Check if it's a HumanMessage
        if hasattr(message, "role"):
            role = message.role  # Access the role if it exists as an attribute
        else:
            role = message.type  # Attempt to access using .type if .role is not found 
    elif isinstance(message, dict) and "role" in message:  # Check if it's a dictionary with 'role'
        role = message["role"]
    else:
        role = "unknown" 

   
    with st.chat_message(role):
        if isinstance(message, HumanMessage):
            st.markdown(message.content)  # Access content for HumanMessage
        elif isinstance(message, AIMessage):  # Check if it's an AIMessage
            st.markdown(message.content)  # Access content for AIMessage
        elif isinstance(message, dict) and "content" in message:  # Check for dictionary
            st.markdown(message["content"])
        else:
            st.markdown(str(message))  
    



# User input and chatbot response
if user_input := st.chat_input("Enter your message:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process the user input through the graph
    state = {"messages": st.session_state.messages}  
    updated_state = graph.invoke(state) 
    st.session_state.messages = updated_state["messages"]
















