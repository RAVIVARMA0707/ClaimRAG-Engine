import streamlit as st
import requests
import os

# ---------------------------
# API CONFIG
# ---------------------------

CHAT_API_URL = "http://127.0.0.1:8000/api/v1/query/"
UPLOAD_API_URL = "http://127.0.0.1:8000/api/v1/upload-pdf"

# ---------------------------
# SAMPLE JSON
# ---------------------------
sample_json = """
{
  "claim_details": {
    "claim_id": "CLM001",
    "policy_id": "POL00234",
    "claim_type": "Motor",
    "incident_type": "Repair",
    "incident_date": "2026-02-10",
    "reported_delay_days": 2,
    "estimated_damage": 300000,
    "idv": 800000,
    "deductible": 10000,
    "previous_claims_90_days": 2,
    "documents_submitted": ["Policy Copy", "Repair Estimate"],
    "policy_status": "Active"
  }
}
"""
# ---------------------------
# FUNCTION: SEND QUERY
# ---------------------------
def send_query(query, history):
    try:
        response = requests.post(
            CHAT_API_URL,
            json={"query": query, "history": history}
        )
        return response.json().get("response", "No response from API")
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="AI Insurance Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# SIDEBAR NAVIGATION
# ---------------------------
with st.sidebar:
    st.title("🧠 AI Assistant")

    page = st.radio(
        "Navigation",
        ["💬 Chat", "🛠️ Admin"]
    )

    st.divider()

# =========================================================
# 💬 CHAT PAGE
# =========================================================
if page == "💬 Chat":

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
    # CHAT SIDEBAR (HISTORY)
    # ---------------------------
    with st.sidebar:
        st.markdown("### 💬 Chats")

        if st.button("➕ New Chat"):
            new_chat = f"Chat {len(st.session_state.chat_sessions) + 1}"
            st.session_state.chat_sessions[new_chat] = []
            st.session_state.current_chat = new_chat

        for chat in st.session_state.chat_sessions:
            if st.button(f"📁 {chat}"):
                st.session_state.current_chat = chat

    # ---------------------------
    # LOAD CURRENT CHAT
    # ---------------------------
    current_chat = st.session_state.current_chat
    messages = st.session_state.chat_sessions[current_chat]

    st.markdown(f"### 💬 {current_chat}")
    st.divider()

    # ---------------------------
    # DISPLAY MESSAGES
    # ---------------------------
    if len(messages) == 0:
        st.info("👋 Start a conversation...")

    for msg in messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    # ---------------------------
    # USER INPUT
    # ---------------------------
    user_input = st.chat_input("Enter claim details or ask a question...")

    if user_input:
        # Save user message
        messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking... 🤔"):

                response_json = send_query(user_input, insurance_data)

                if "error" in response_json:
                    st.error(response_json["error"])
                    response_text = response_json["error"]
                else:
                    main_text = response_json.get("response", "")
                    page_no = response_json.get("page")
                    doc_name = response_json.get("doc_name")
                    confidence = response_json.get("confidence")

                    meta = f"\n\n📄 Page: {page_no} | Doc: {doc_name}" if page_no else ""
                    conf = f"\n🎯 Confidence: {confidence}" if confidence else ""

                    response_text = f"{main_text}{meta}{conf}"

                    st.markdown(response_text)

        messages.append({"role": "assistant", "content": response_text})

# =========================================================
# 🛠️ ADMIN PAGE
# =========================================================
elif page == "🛠️ Admin":

    st.title("🛠️ Admin Dashboard")

    # ---------------------------
    # ADMIN AUTH (BASIC)
    # ---------------------------
    password = st.text_input("Enter Admin Password", type="password")

    if password != "admin123":
        st.warning("🔒 Admin access only")
        st.stop()

    st.success("✅ Access Granted")

    st.divider()

    # ---------------------------
    # FILE UPLOAD
    # ---------------------------
    st.markdown("### 📄 Upload Insurance Documents")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if uploaded_file:
        st.success(f"Selected: {uploaded_file.name}")

        if st.button("🚀 Upload"):
            try:
                with st.spinner("Uploading..."):

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            "application/pdf"
                        )
                    }

                    response = requests.post(
                        UPLOAD_API_URL,
                        files=files
                    )

                    if response.status_code == 200:
                        st.success("✅ File uploaded successfully!")
                    else:
                        st.error("❌ Upload failed!")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # ---------------------------
    # SHOW UPLOADED FILES (LOCAL)
    # ---------------------------
    st.divider()
    st.markdown("### 📂 Uploaded Files")

    upload_folder = "uploads"

    if os.path.exists(upload_folder):
        files = os.listdir(upload_folder)

        if files:
            for f in files:
                st.write(f"• {f}")
        else:
            st.info("No files uploaded yet.")
    else:
        st.info("Upload folder not found.")