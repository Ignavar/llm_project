import torch
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def load_retrieval_system():
    """Loads the embedding model, FAISS index, and metadata."""
    print("Loading embedding model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading FAISS index and metadata...")
    index = faiss.read_index("data/bank_knowledge.index")
    with open("data/bank_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
        
    return embedder, index, metadata

def load_llm():
    """Loads the Qwen2.5 3B Instruct model."""
    print("Loading Qwen2.5-3B-Instruct... This may take a moment.")
    model_id = "Qwen/Qwen2.5-3B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    # Using device_map="auto" to efficiently utilize available GPU/CPU memory
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16, 
        device_map="auto"
    )
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=256,
        temperature=0.3, # Low temperature for more factual, less creative answers
        repetition_penalty=1.1
    )
    return pipe

def retrieve_context(query, embedder, index, metadata, top_k=3):
    """Embeds the query and fetches the most relevant document chunks."""
    query_vector = embedder.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    retrieved_texts = []
    for idx in indices[0]:
        if idx != -1: # Ensure valid index
            retrieved_texts.append(metadata[idx]['content'])
            
    return "\n---\n".join(retrieved_texts)

def generate_answer(query, context, llm_pipeline):
    """Constructs the prompt and generates the final response."""
    # Strict prompt engineering to handle domain boundaries and tone
    system_prompt = (
        "You are a helpful, caring, and reliable customer service assistant for a local bank. "
        "Use ONLY the provided context to answer the user's question. "
        "If the answer is not contained in the context, politely state that you do not have that "
        "information and offer to connect them with a human representative. Do not guess or make up information."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Let the tokenizer handle the chat template for Qwen
    prompt = llm_pipeline.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    print("\nGenerating response...")
    outputs = llm_pipeline(prompt)
    
    # Extract just the generated text (ignoring the prompt)
    generated_text = outputs[0]["generated_text"]
    response = generated_text.split("<|im_start|>assistant\n")[-1].strip()
    return response

if __name__ == "__main__":
    # Initialize the system
    embedder, index, metadata = load_retrieval_system()
    llm_pipeline = load_llm()
    
    print("\n" + "="*50)
    print("Bank Assistant Prototype Initialized!")
    print("="*50)
    
    # Interactive loop for the terminal prototype
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ['quit', 'exit']:
            break
            
        context = retrieve_context(user_query, embedder, index, metadata)
        answer = generate_answer(user_query, context, llm_pipeline)
        
        print(f"\nAssistant: {answer}")
