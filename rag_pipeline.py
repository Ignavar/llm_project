import torch
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def load_retrieval_system():
    print("Loading embedding model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading FAISS index and metadata...")
    index = faiss.read_index("data/bank_knowledge.index")
    with open("data/bank_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
        
    return embedder, index, metadata

def load_llm():
    print("Loading Qwen2.5-3B-Instruct... This may take a moment.")
    model_id = "Qwen/Qwen2.5-3B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16, 
        device_map="auto"
    )
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512, # Increased from 256 to allow fuller answers
        temperature=0.2,    # Lowered slightly for more factual extraction
        repetition_penalty=1.1
    )
    return pipe

def retrieve_context(query, embedder, index, metadata, top_k=6, distance_threshold=1.5):
    """Embeds query, fetches top_k chunks, and filters out poor matches using distance."""
    query_vector = embedder.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    retrieved_texts = []
    
    print("\n--- Retrieval Diagnostics ---")
    # Zip distances and indices to evaluate each chunk individually
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1:
            print(f"Match Distance: {dist:.4f} | Source: {metadata[idx].get('source_sheet', 'Unknown')}")
            
            # Only append the context if the distance is below our noise threshold
            if dist <= distance_threshold:
                retrieved_texts.append(metadata[idx]['content'])
    print("-----------------------------\n")
                
    # Fallback: If the threshold filtered everything out, return at least the absolute best match
    if not retrieved_texts and indices[0][0] != -1:
        retrieved_texts.append(metadata[indices[0][0]]['content'])
             
    return "\n---\n".join(retrieved_texts)

def generate_answer(query, context, llm_pipeline):
    system_prompt = (
        "You are a helpful, caring, and reliable customer service assistant for a local bank. "
        "Analyze the provided context carefully to answer the user's question. "
        "If the answer is present in the context, provide a clear, concise response. "
        "If the context does not contain the answer, politely state: 'I apologize, but I don't have that specific information right now. Let me connect you with a human representative.' "
        "Never make up information or guess."
    )
    
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    prompt = llm_pipeline.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    
    print("Generating response...")
    outputs = llm_pipeline(prompt)
    
    generated_text = outputs[0]["generated_text"]
    response = generated_text.split("<|im_start|>assistant\n")[-1].strip()
    return response

if __name__ == "__main__":
    embedder, index, metadata = load_retrieval_system()
    llm_pipeline = load_llm()
    
    print("\n" + "="*50)
    print("Bank Assistant Prototype Initialized!")
    print("="*50)
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ['quit', 'exit']:
            break
            
        context = retrieve_context(user_query, embedder, index, metadata)
        answer = generate_answer(user_query, context, llm_pipeline)
        
        print(f"\nAssistant: {answer}")
