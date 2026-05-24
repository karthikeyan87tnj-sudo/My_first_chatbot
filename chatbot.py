import streamlit as st
import google.generativeai as genai
import requests

# ── Config ──────────────────────────────────────────────────────────────────
API_KEY = st.secrets["GEMINI_API_KEY"]      # set in Streamlit Cloud secrets
GDRIVE_FILE_ID = "10iDj7__Bscs6014-mpP_CYFvW1xsFw2a"  # ← your Google Drive file ID

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Class 1 English Assistant", page_icon="📚")
st.title("📚 Class 1 – English Assistant")

# ── Load KB from Google Drive ────────────────────────────────────────────────
@st.cache_data
def load_kb(file_id):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

try:
    kb = load_kb(GDRIVE_FILE_ID)
except Exception as e:
    st.error(f"Failed to load KB from Google Drive: {e}")
    st.stop()

# ── System prompt (same as original notebook) ────────────────────────────────
system_prompt = f"""
you are my personal assistant and you need to provide information by referring the KB in polite. do go outside of KB information.
{kb}
"""

# ── Init Gemini ──────────────────────────────────────────────────────────────
@st.cache_resource
def init_model():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_prompt)

model = init_model()

# ── Session state for chat history ──────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"assistant", "content": "..."}

# ── Render past messages ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask something about the KB…")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Gemini API
    response = st.session_state.chat.send_message(user_input)
    reply = response.text

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
