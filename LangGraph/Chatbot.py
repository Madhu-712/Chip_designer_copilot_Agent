
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
from langchain_core.messages import HumanMessage  # Import HumanMessage

# Ensure secrets are loaded correctly;  adapt as needed for your Streamlit setup
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
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)  # Consider adding a max_tokens parameter
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
                state["messages"].append({"role": "tool", "content": f"Error using tool: {e}"})
        return {"messages": [message]}  # Return the LLM's response, not the last tool call
    except Exception as e:
        return {"messages": [{"role": "assistant", "content": f"An error occurred: {e}"}]}


# Graph setup
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile()

# Streamlit app
st.title("Chip Design Copilot Chatbot")


st.markdown("**Example Queries:**")
st.markdown("- How can I optimize the power consumption of my chip design?")
st.markdown("- What are the latest trends in AI-based chip design?")
st.markdown("- Can you suggest ways to improve the reliability of my ASIC?")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Hi, I Am Md.How can you assist you with chip design"):
    if user_input: # Check if user_input is not None or empty
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        config = {"configurable": {"thread_id": "1"}, "recursion_limit": 100}
        events = graph.stream(  
         { "messages": [HumanMessage(content=user_input)]},
                
            config,
            stream_mode="values",
        )

        for event in events:
            if "messages" in event:
                response_content = event["messages"][-1]["content"]  # Corrected: Access content from dictionary
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_content}
                )
                with st.chat_message("assistant"):
                    st.markdown(response_content)
