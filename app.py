import streamlit as st
import uuid
from agent import agent

st.title("CogniSphere Multi tool agent")
st.caption("Ask about company policies, employee details, or percentage calculations.")

if "thread_id" not in st.session_state:
    st.session_state.thread_id=str(uuid.uuid4)

if "messages" not in st.session_state:
    st.session_state.messages=[]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input=st.chat_input("Ask a question...")
config = {"configurable": {"thread_id": st.session_state.thread_id}, "recursion_limit": 15}
if user_input:
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Call the agent with this session's thread_id
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    response = agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config)
    answer = response["messages"][-1].content

    # Show and store assistant response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)