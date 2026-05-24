import streamlit as st
import google.generativeai as genai
import requests

# ── Config ──────────────────────────────────────────────────────────────────
API_KEY = st.secrets["GEMINI_API_KEY"]      # set in Streamlit Cloud secrets
GDRIVE_FILE_ID = "10iDj7__Bscs6014-mpP_CYFvW1xsFw2a"  # ← your Google Drive file ID

# ── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Your Personal Assistant", page_icon="🤖")

# ── Custom CSS - Futuristic Robotic Theme ────────────────────────────────────
st.markdown("""
<style>
@import url('https://github.com/karthikeyan87tnj-sudo/My_first_chatbot/blob/main/background.jpg');

/* Background */
.stApp {
    background-image: 
        linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
        url('https://github.com/karthikeyan87tnj-sudo/My_first_chatbot/blob/main/background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Grid overlay effect */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: 
        linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Title */
h1 {
    font-family: 'Orbitron', monospace !important;
    color: #00ffff !important;
    text-align: center;
    font-size: 2rem !important;
    letter-spacing: 4px !important;
    text-shadow: 0 0 20px rgba(0,255,255,0.8), 0 0 40px rgba(0,255,255,0.4);
    padding: 1rem 0;
    border-bottom: 1px solid rgba(0,255,255,0.3);
    margin-bottom: 1rem;
}

/* Chat messages */
.stChatMessage {
    background: rgba(0, 20, 40, 0.8) !important;
    border: 1px solid rgba(0,255,255,0.2) !important;
    border-radius: 4px !important;
    backdrop-filter: blur(10px);
    font-family: 'Rajdhani', sans-serif !important;
    color: #e0f7fa !important;
}

/* User message */
.stChatMessage[data-testid="user-message"] {
    border-color: rgba(0,255,255,0.4) !important;
    background: rgba(0,40,60,0.8) !important;
}

/* Chat input */
.stChatInput textarea {
    background: rgba(0, 10, 20, 0.9) !important;
    border: 1px solid rgba(0,255,255,0.4) !important;
    border-radius: 4px !important;
    color: #00ffff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
}

.stChatInput textarea::placeholder {
    color: rgba(0,255,255,0.4) !important;
}

.stChatInput textarea:focus {
    border-color: #00ffff !important;
    box-shadow: 0 0 15px rgba(0,255,255,0.3) !important;
}

/* Send button */
.stChatInput button {
    background: rgba(0,255,255,0.1) !important;
    border: 1px solid rgba(0,255,255,0.5) !important;
    color: #00ffff !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
::-webkit-scrollbar-thumb { background: rgba(0,255,255,0.4); border-radius: 2px; }

/* Error box */
.stAlert {
    background: rgba(255,0,0,0.1) !important;
    border: 1px solid rgba(255,0,0,0.4) !important;
    color: #ff6b6b !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 YOUR PERSONAL ASSISTANT")

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
