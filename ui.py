import streamlit as st
from app import ask_question, process_uploaded_file

# --- Page Config ---
st.set_page_config(
    page_title="RAG PDF Analyzer", 
)
# --- PREMIUM PROFESSIONAL CSS ---
st.markdown("""
<style>

/* ===== GLOBAL ===== */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(180deg, #f8fafc, #eef2ff);
}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
    padding-top: 1rem;
}

/* Sidebar card */
.sidebar-card {
    background: #f9fafb;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79,70,229,0.3);
}
            
/* Reduce caption gap */
.stCaption {
    margin-bottom: 0.5rem;
}
/* ===== CHAT MESSAGES ===== */
.stChatMessage {
    border-radius: 12px !important;
    padding: 14px !important;
    margin-bottom: 10px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* USER MESSAGE */
[data-testid="stChatMessageContent"][aria-label="user message"] {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: white;
    border: none;
}

/* BOT MESSAGE */
[data-testid="stChatMessageContent"][aria-label="assistant message"] {
    background: #ffffff;
    color: #111827;
}

/* ===== INPUT BOX ===== */
.stChatInput input {
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    padding: 10px;
}

/* ===== HEADINGS ===== */
h1 {
    font-weight: 700;
    color: #111827;
     margin-top: 5px !important;
    margin-bottom: 0.3rem;
}

h2, h3 {
    color: #374151;
}

/* ===== ALERTS ===== */
.stAlert {
    border-radius: 10px;
}

/* ===== SMALL TEXT ===== */
small {
    color: #6b7280;
}

/* ===== HOVER EFFECT ===== */
.stChatMessage:hover {
    transform: scale(1.01);
    transition: 0.2s;
}

</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if "history" not in st.session_state:
    st.session_state.history = []
if "document_name" not in st.session_state:
    st.session_state.document_name = None

# --- Sidebar: Document Control Center ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=80)
    st.title("Knowledge Base")
    st.markdown("---")
    
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        if st.button("✨Load Document", use_container_width=True, type="primary"):
            with st.status("Analyzing PDF...", expanded=True) as status:
                success, message = process_uploaded_file(uploaded_file)
                if success:
                    st.session_state.document_name = uploaded_file.name
                    st.session_state.history = [] 
                    status.update(label="Processing Completed!", state="complete", expanded=False)
                    st.toast("Document processed successfully!", icon="✅")
                else:
                    status.update(label="Processing Failed", state="error")
                    st.error(message)

    if st.session_state.document_name:
        st.markdown(f"""
        <div class="sidebar-card">
            <small>Active Document:</small><br>
            <strong>{st.session_state.document_name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# --- Main Interaction Area ---
st.title("PDF RAG Chatbot")
st.caption("Advanced Retrieval-Augmented Generation Interface")

# Display Message History
if not st.session_state.history:
    st.info("💡 **Getting Started:** Upload a PDF in the sidebar to begin querying your data.")
else:
    for role, text in st.session_state.history:
        if role == "You":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**You**  \n{text}")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**AI Assistant**  \n{text}")

# --- Floating Chat Input ---
if prompt := st.chat_input("Enter your question here..."):
    if not st.session_state.document_name:
        st.error("Please upload a document before asking questions.")
    else:
        # User Message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**You**  \n{prompt}")
        
        # Bot Response
        with st.chat_message("assistant", avatar="🤖"):
            response_placeholder = st.empty()
            with st.spinner("Searching through document..."):
                answer = ask_question(prompt)
                response_placeholder.markdown(f"**AI Assistant**  \n{answer}")
        
        # Save to history
        st.session_state.history.append(("You", prompt))
        st.session_state.history.append(("Bot", answer))