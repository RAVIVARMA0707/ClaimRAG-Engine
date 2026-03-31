import streamlit as st
import requests

API_URL = "http://localhost:8000/process-claim"

def send_query(query, history):
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "history": history}
        )
        return response.json()["response"]
    except Exception as e:
        return f"Error: {str(e)}"

# Page config
st.set_page_config(page_title="AI Insurance Assistant", layout="wide")
st.title("AI Insurance Claims Processing Assistant")

# ---------------------------
# SESSION STATE (MULTI-CHAT)
# ---------------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "Chat 1" not in st.session_state.chat_sessions:
    st.session_state.chat_sessions["Chat 1"] = []

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.title("💬 Chat History")

    if st.button("➕ New Chat"):
        new_chat = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_chat] = []
        st.session_state.current_chat = new_chat

    for chat in st.session_state.chat_sessions:
        if st.button(chat):
            st.session_state.current_chat = chat

# ---------------------------
# LOAD CURRENT CHAT
# ---------------------------
current_chat = st.session_state.current_chat
messages = st.session_state.chat_sessions[current_chat]

# ---------------------------
# DISPLAY MESSAGES
# ---------------------------
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# USER INPUT
# ---------------------------
user_input = st.chat_input("Enter claim details or ask a question...")

if user_input:
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = send_query(user_input, messages)
        st.markdown(response)

    messages.append({"role": "assistant", "content": response})
