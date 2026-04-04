import json
import streamlit as st
import faiss
import pickle
import numpy as np

# Import your custom UI modules
from theme_config import get_theme
from styles import build_css
import components as ui

try:
    import rag_pipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# ── Page config ─────────────────────────────────────────
st.set_page_config(
    page_title="NUST Bank Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ───────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Theme ───────────────────────────────────────────────
theme = get_theme(st.session_state.dark_mode)

st.markdown(build_css(theme, st.session_state.dark_mode), unsafe_allow_html=True)

# ── GLOBAL CSS OVERRIDES ────────────────────────────────
def apply_global_theme_overrides(theme, dark_mode: bool):
    if dark_mode:
        st.markdown(f"""
        <style>

        /* ───────────────── GLOBAL TEXT ───────────────── */
        .stApp, .stApp * {{
            color: {theme['on_surface']} !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: {theme['on_surface']} !important;
        }}

        h1, h2, h3, h4, h5 {{
            color: {theme['on_surface']} !important;
        }}

        /* ───────────────── PLACEHOLDERS ───────────────── */
        input::placeholder, textarea::placeholder {{
            color: {theme['on_surface_variant']} !important;
            opacity: 1;
        }}

        /* ───────────────── BUTTONS ───────────────── */
        button {{
            background-color: {theme['surface_container']} !important;
            color: {theme['on_surface']} !important;
            border: 1px solid {theme['outline_variant']} !important;
        }}

        button:hover {{
            background-color: {theme['surface_container_high']} !important;
        }}

        /* ───────────────── FILE UPLOADER FIX ───────────────── */

        /* Outer container */
        [data-testid="stFileUploaderDropzone"] {{
            background-color: {theme['surface_container']} !important;
            border: 1px solid {theme['outline_variant']} !important;
        }}

        /* Remove ALL inner backgrounds */
        [data-testid="stFileUploaderDropzone"] * {{
            background-color: transparent !important;
        }}

        /* Instructions area */
        [data-testid="stFileUploaderDropzoneInstructions"] {{
            background-color: transparent !important;
        }}

        /* Upload button */
        [data-testid="stFileUploader"] button {{
            background-color: {theme['surface_container_high']} !important;
            color: {theme['on_surface']} !important;
            border: 1px solid {theme['outline_variant']} !important;
        }}

        [data-testid="stFileUploader"] button:hover {{
            background-color: {theme['surface_container_highest']} !important;
        }}

        /* ───────────────── CHAT INPUT FIX ───────────────── */

        /* Outer chat input container */
        div[data-testid="stChatInput"] {{
            background-color: {theme['surface_container']} !important;
        }}

        /* Remove BaseWeb wrappers */
        div[data-baseweb="textarea"],
        div[data-baseweb="base-input"] {{
            background-color: transparent !important;
            box-shadow: none !important;
        }}

        /* Inner wrapper divs */
        div[data-testid="stChatInput"] > div {{
            background-color: transparent !important;
        }}

        /* Textarea itself */
        textarea[data-testid="stChatInputTextArea"] {{
            background-color: {theme['surface_container']} !important;
            color: {theme['on_surface']} !important;
            border: 1px solid {theme['outline_variant']} !important;
        }}

        /* Send button */
        button[data-testid="stChatInputSubmitButton"] {{
            background-color: {theme['surface_container_high']} !important;
            border: 1px solid {theme['outline_variant']} !important;
        }}

        button[data-testid="stChatInputSubmitButton"]:hover {{
            background-color: {theme['surface_container_highest']} !important;
        }}

        /* ───────────────── FIX STREAMLIT FAINT TEXT ───────────────── */
        .st-emotion-cache-ue6h4q,
        .st-emotion-cache-1v0mbdj {{
            color: {theme['on_surface']} !important;
        }}

        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <style>
        .stApp, .stApp * {{
            color: {theme['on_surface']} !important;
        }}
        </style>
        """, unsafe_allow_html=True)


apply_global_theme_overrides(theme, st.session_state.dark_mode)

# ── Load backend ────────────────────────────────────────
@st.cache_resource
def load_rag():
    if RAG_AVAILABLE:
        print("Booting up backend systems...")
        rag_pipeline.initialize_system()
    return RAG_AVAILABLE

rag_ready = load_rag()

# ───────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏦 Admin")

    if st.button(theme["label"], use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown(ui.status_indicator(online=rag_ready), unsafe_allow_html=True)

    st.markdown(ui.sidebar_section_label("Knowledge Base"), unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload bank data (JSON)",
        type=["json"],
        label_visibility="collapsed",
    )

    if st.button("Update Knowledge Base", use_container_width=True):
        if uploaded_file is not None:
            try:
                new_data = json.load(uploaded_file)
                if RAG_AVAILABLE:
                    new_chunks = []
                    # Parse the JSON layout
                    for category in new_data.get("categories", []):
                        cat_name = category.get("category", "General")
                        for qa in category.get("questions", []):
                            chunk_text = f"Category: {cat_name} | Question: {qa['question']} | Answer: {qa['answer']}"
                            new_chunks.append({"source_sheet": "Dynamic JSON Upload", "content": chunk_text})
                    
                    if new_chunks:
                        # Generate embeddings via the backend embedder
                        texts = [chunk['content'] for chunk in new_chunks]
                        new_embeddings = rag_pipeline.embedder.encode(texts).astype('float32')
                        
                        # Update the FAISS index and metadata
                        rag_pipeline.index.add(new_embeddings)
                        rag_pipeline.metadata.extend(new_chunks)
                        
                        # Save the updated knowledge base to disk
                        faiss.write_index(rag_pipeline.index, "data/bank_knowledge.index")
                        with open("data/bank_metadata.pkl", "wb") as f:
                            pickle.dump(rag_pipeline.metadata, f)
                            
                        st.success(f"Successfully processed and indexed {len(new_chunks)} new records!")
                    else:
                        st.warning("No valid QA pairs found in the JSON.")
                else:
                    st.success("Knowledge base updated (Dev Mode).")
            except Exception as exc:
                st.error(f"Upload failed: {exc}")
        else:
            st.warning("Please select a JSON file first.")

    st.markdown(ui.sidebar_section_label("Conversation"), unsafe_allow_html=True)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        f"""
        <div style='margin-top:2rem; padding-top:1rem; 
        border-top:1px solid {theme['outline_variant']}33; 
        font-family:{theme['font_label']}; 
        font-size:0.68rem; 
        color:{theme['on_surface_variant']}; 
        text-transform:uppercase; 
        letter-spacing:0.08em;'>
        NUST Bank · Internal Tool<br>Theme: {theme['name']}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────
st.markdown(ui.page_header(), unsafe_allow_html=True)

chat_area = st.container()

with chat_area:
    if not st.session_state.messages:
        st.markdown(ui.empty_state(), unsafe_allow_html=True)
    else:
        st.markdown(ui.chat_wrapper_open(), unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(ui.user_bubble(msg["content"]), unsafe_allow_html=True)
            else:
                st.markdown(ui.bot_bubble(msg["content"]), unsafe_allow_html=True)
        st.markdown(ui.chat_wrapper_close(), unsafe_allow_html=True)

user_input = st.chat_input("Ask about loans, accounts, transfers…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
):
    with st.spinner("Searching bank records..."):
        last_query = st.session_state.messages[-1]["content"]

        if RAG_AVAILABLE:
            response = rag_pipeline.process_query(last_query)
        else:
            response = f"*(Dev mode)*\n\nYou asked: **{last_query}**"

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
