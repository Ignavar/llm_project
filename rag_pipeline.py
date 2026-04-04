import torch
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig

# Global variables to hold our loaded models in memory
embedder = None
index = None
metadata = None
llm_pipeline = None

def initialize_system():
    """Loads all models and databases into memory."""
    global embedder, index, metadata, llm_pipeline
    
    # --- THE FIX: The Singleton Guard ---
    # If the pipeline already exists, stop and don't load it again!
    if llm_pipeline is not None:
        print("Backend already initialized. Skipping duplicate load.")
        return
    # ------------------------------------
    
    print("Loading embedding model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading FAISS index and metadata...")
    index = faiss.read_index("data/bank_knowledge.index")
    with open("data/bank_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
        
    print("Loading Qwen2.5-3B-Instruct in 4-bit... This may take a moment.")
    model_id = "Qwen/Qwen2.5-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # 1. Define the exact 4-bit quantization parameters
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,       # Saves even more memory
        bnb_4bit_quant_type="nf4",            # Standard format for weights
        bnb_4bit_compute_dtype=torch.float16  # Computes in float16 for speed
    )

    # 2. Pass the config to the model loader
    model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        device_map="auto",
        quantization_config=bnb_config
    )

    llm_pipeline = pipeline(
        "text-generation", model=model, tokenizer=tokenizer,
        max_new_tokens=512, temperature=0.2, repetition_penalty=1.1
    )
    print("Backend Initialization Complete!")

def retrieve_context(query, top_k=32, distance_threshold=1.8):
    """Embeds the query and fetches relevant chunks from FAISS."""
    global embedder, index, metadata
    
    query_vector = embedder.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    retrieved_texts = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and dist <= distance_threshold:
            retrieved_texts.append(metadata[idx]['content'])
            
    # Fallback to absolute best match if threshold filters everything
    if not retrieved_texts and indices[0][0] != -1:
        retrieved_texts.append(metadata[indices[0][0]]['content'])
            
    return "\n---\n".join(retrieved_texts)

def generate_answer(query, context):
    """Constructs the strict prompt and generates a response."""
    global llm_pipeline
    
    system_prompt = (
        "You are a helpful, caring, and reliable customer service assistant for NUST Bank. "
        "Analyze the provided context carefully to answer the user's question. "
        "If the answer is present in the context, provide a clear response. "
        "CRITICAL INSTRUCTION: If the context contains a list of items, products, or features, you MUST list ALL of them exhaustively. Do not summarize or leave any bullet points out. "
        "If the context DOES NOT contain the answer, you must reply EXACTLY with this exact phrase: "
        "'I apologize, but I don't have that specific information right now. Let me connect you with a human representative.' "
        "Do not add any preambles, explanations, or extra words. Never make up information or guess."
    ) 

    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    prompt = llm_pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = llm_pipeline(prompt)
    
    response = outputs[0]["generated_text"].split("<|im_start|>assistant\n")[-1].strip()
    
    # Strict fallback guardrail to override chatty LLM behavior
    if "I apologize, but I don't have that specific information right now" in response:
        return "I apologize, but I don't have that specific information right now. Let me connect you with a human representative."
        
    return response

def process_query(query):
    """Main wrapper function for the frontend to call."""
    context = retrieve_context(query)
    return generate_answer(query, context)
