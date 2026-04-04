import gradio as gr
import json
import faiss
import pickle

# Import our backend logic
import rag_pipeline


def chat_function(message, history):
    """Passes the user message to the RAG backend."""
    return rag_pipeline.process_query(message)

def handle_file_upload(file_path):
    """Handles the Real-Time Updates requirement."""
    if file_path is None:
        return "No file uploaded."
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
            
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
                
            return f"Successfully processed and indexed {len(new_chunks)} new records!"
        else:
            return "No valid QA pairs found in the JSON."
    except Exception as e:
        return f"Error processing file: {e}"

# --- BUILD THE GRADIO UI ---
with gr.Blocks(title="NUST Bank Support", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏦 NUST Bank Customer Support Assistant")
    
    with gr.Row():
        # LEFT COLUMN: Admin Controls
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Admin: Real-Time Updates")
            gr.Markdown("Upload new JSON policies to update the knowledge base instantly.")
            
            file_upload = gr.File(label="Upload JSON File", file_types=[".json"])
            upload_button = gr.Button("Update Knowledge Base", variant="primary")
            upload_status = gr.Textbox(label="System Status", interactive=False)
            
            # Link the button to the upload function
            upload_button.click(
                fn=handle_file_upload,
                inputs=file_upload,
                outputs=upload_status
            )
            
        # RIGHT COLUMN: Chat Interface
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat_function,
                chatbot=gr.Chatbot(height=500),
                textbox=gr.Textbox(placeholder="Ask a question about our banking services...", container=False, scale=7),
                title="Chat with our AI Agent"
            )

if __name__ == "__main__":
    # Boot up the LLM and DB when the app starts
    print("Booting up backend systems...")
    rag_pipeline.initialize_system()

    # Launch the web application
    demo.launch()
