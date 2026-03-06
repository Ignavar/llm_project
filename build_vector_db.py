import pandas as pd
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

def build_faiss_index(csv_path, index_path, metadata_path):
    print("Loading preprocessed data...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}. Did you run the preprocessing script first?")
        return
        
    # Ensure no empty rows slip through
    df = df.dropna(subset=['content'])
    documents = df['content'].tolist()
    
    print(f"Loaded {len(documents)} document chunks.")
    
    # Load the embedding model
    print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("Generating vector embeddings. This might take a minute...")
    embeddings = model.encode(documents, show_progress_bar=True)
    
    # Convert to float32 (FAISS strict requirement)
    embeddings = np.array(embeddings).astype('float32')
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    print(f"Initializing FAISS index with dimension: {dimension}...")
    index = faiss.IndexFlatL2(dimension) 
    
    # Add vectors to the index
    index.add(embeddings)
    print(f"Total vectors in FAISS index: {index.ntotal}")
    
    # Save the index to disk
    faiss.write_index(index, index_path)
    print(f"FAISS index saved to {index_path}")
    
    # Save the metadata (the original text and source sheets) mapping 
    metadata = df.to_dict('records')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"Metadata saved to {metadata_path}")

if __name__ == "__main__":
    CSV_FILE = "data/processed_bank_knowledge.csv"
    FAISS_INDEX_FILE = "data/bank_knowledge.index"
    METADATA_FILE = "data/bank_metadata.pkl"
    
    build_faiss_index(CSV_FILE, FAISS_INDEX_FILE, METADATA_FILE)
