
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

# Initialize Session State for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Define State and Graph as before
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Human assistance tool (modified for Streamlit)
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human via Streamlit."""
    human_input = st.text_input("Human assistance needed:", key=f"human_input_{query}")
    if human_input:
        return human_input
    return "Waiting for human input..."  # Placeholder while waiting

# LLM and Tools setup
tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
llm_with_tools = llm.bind_tools(tools)

# Chatbot function
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Ensure single tool call (modify if needed for parallel tool calls)
    tool_calls = message.tool_calls
    if tool_calls and len(tool_calls) > 1:
         st.warning("Multiple tool calls detected. Only the first will be executed.")
         message.tool_calls = [tool_calls[0]]
       
    return {"messages": [message]}

# Graph setup (same as before)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Streamlit UI
st.title("Chip Design Chatbot")

# Add examples
st.markdown("**Example Queries:**")
st.markdown("- How can I optimize the power consumption of my chip design?")
st.markdown("- What are the latest trends in AI-based chip design?")
st.markdown("- Can you suggest ways to improve the reliability of my ASIC?")
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if user_input := st.chat_input("Enter your message:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process the user input through the graph
    config = {"configurable": {"thread_id": "1"}}  # Add thread_id
    for event in graph.stream({"messages": st.session_state.messages}, config=config):
        response_message = event.get("messages", [])[-1]
        
        # Display chatbot response or tool call
        if response_message:
            st.session_state.messages.append({"role": "assistant", "content": response_message.content})
            with st.chat_message("assistant"):
                st.markdown(response_message.content)



















