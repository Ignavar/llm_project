import streamlit as st
import json
import faiss
import pickle
import rag_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NUST Bank Assistant",
    page_icon="🏦",
    layout="wide"
)

# --- LOAD BACKEND ONCE ---
@st.cache_resource
def load_system():
    rag_pipeline.initialize_system()
    return True

load_system()

# --- SESSION STATE (CHAT MEMORY) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (ADMIN PANEL) ---
with st.sidebar:
    st.title("⚙️ Admin Panel")
    st.markdown("Upload new policies to update knowledge base")

    uploaded_file = st.file_uploader("Upload JSON", type=["json"])

    if st.button("Update Knowledge Base"):
        if uploaded_file is not None:
            try:
                new_data = json.load(uploaded_file)

                new_chunks = []
                for category in new_data.get("categories", []):
                    cat_name = category.get("category", "General")
                    for qa in category.get("questions", []):
                        chunk_text = f"Category: {cat_name} | Question: {qa['question']} | Answer: {qa['answer']}"
                        new_chunks.append({
                            "source_sheet": "Dynamic JSON Upload",
                            "content": chunk_text
                        })

                if new_chunks:
                    texts = [c['content'] for c in new_chunks]
                    new_embeddings = rag_pipeline.embedder.encode(texts).astype('float32')

                    rag_pipeline.index.add(new_embeddings)
                    rag_pipeline.metadata.extend(new_chunks)

                    faiss.write_index(rag_pipeline.index, "data/bank_knowledge.index")
                    with open("data/bank_metadata.pkl", "wb") as f:
                        pickle.dump(rag_pipeline.metadata, f)

                    st.success(f"✅ Added {len(new_chunks)} new records!")
                else:
                    st.warning("No valid data found.")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a file first.")

# --- MAIN CHAT UI ---
st.title("🏦 NUST Bank Customer Support Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask about banking services...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = rag_pipeline.process_query(user_input)
            st.markdown(response)

    # Save response
    st.session_state.messages.append({"role": "assistant", "content": response})