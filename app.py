import os
import uuid

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.title("CogniSphere Multi tool agent")
st.caption("Ask about company policies, employee details, or percentage calculations.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask a question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    try:
        r = requests.post(
            f"{API_URL}/chat",
            json={"message": user_input, "session_id": st.session_state.session_id},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        answer, tools = data["answer"], data["tools_used"]
    except requests.RequestException as e:
        answer, tools = f"Agent service error: {e}", []
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
        if tools:
            st.caption("Tools used: " + ", ".join(tools))