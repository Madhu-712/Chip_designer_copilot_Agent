









import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

# Define State and Graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Human assistance tool 
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human via Streamlit."""
    #Use streamlit for human input
    human_input = st.text_input("Human assistance needed:", key=f"human_input_{query}") 
    if human_input:
        return human_input
    return "Waiting for human input..." 

# Initialize LLM and Tools
tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
llm_with_tools = llm.bind_tools(tools)

# Chatbot function (Modified for sequential tool execution)
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    for tool_call in message.tool_calls:
        tool_result = tool_call.run(tool_call.kwargs)
        state["messages"].append({"role": "tool", "content": tool_result})
        message = llm_with_tools.invoke(state["messages"]) 
    return {"messages": [message]}

# Graph setup
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph (Removed checkpointer)
graph = graph_builder.compile()

# Streamlit UI
st.title("Chip Design Chatbot")
# Add examples
st.markdown("**Example Queries:**")
st.markdown("- How can I optimize the power consumption of my chip design?")
st.markdown("- What are the latest trends in AI-based chip design?")
st.markdown("- Can you suggest ways to improve the reliability of my ASIC?")
# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Process the user input through the graph
    config = {"configurable": {"thread_id": "1"}}  # Add thread_id
    for event in graph.stream({"messages": st.session_state.messages}, config=config):
        response_message = event.get("messages", [])[-1]
        
        # Display chatbot response or tool call
        if response_message:
            st.session_state.messages.append({"role": "assistant", "content": response_message.content})
            with st.chat_message("assistant"):
                st.markdown(response_message.content)




























