import pandas as pd
import os
import re

def clean_text(text):
    """Standardizes text for LLM ingestion."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def anonymize_data(text):
    """Redacts sensitive PII."""
    # Redact Email
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[REDACTED_EMAIL]', text)
    # Redact Phone Numbers
    text = re.sub(r'(\+92|0)?3\d{2}[-\s]?\d{7}', '[REDACTED_PHONE]', text)
    # Redact CNIC
    text = re.sub(r'\b\d{5}-\d{7}-\d{1}\b', '[REDACTED_CNIC]', text)
    return text

def process_excel_document(input_file, output_file):
    """Reads an Excel file, iterates through sheets, cleans, and anonymizes."""
    print(f"Loading Excel file from: {input_file}")
    
    try:
        # sheet_name=None loads all sheets into a dictionary of DataFrames
        sheets = pd.read_excel(input_file, sheet_name=None)
    except Exception as e:
        print(f"Error reading the Excel file. Please check the path: {e}")
        return

    processed_documents = []

    for sheet_name, df in sheets.items():
        print(f"Processing sheet: {sheet_name}")
        for index, row in df.iterrows():
            # Combine the column names and values into a single string
            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            
            cleaned = clean_text(row_text)
            anonymized = anonymize_data(cleaned)
            
            # Only add if the resulting string isn't empty
            if anonymized.strip():
                processed_documents.append({
                    "source_sheet": sheet_name,
                    "content": anonymized
                })

    final_df = pd.DataFrame(processed_documents)
    final_df.to_csv(output_file, index=False)
    print(f"\nSuccess! Processed {len(processed_documents)} document chunks into {output_file}")

if __name__ == "__main__":
    # --- UPDATE THIS PATH to where your actual .xlsx file is located ---
    INPUT_EXCEL_FILE = "data/raw/NUST Bank-Product-Knowledge.xlsx" 
    CLEAN_DATA_FILE = "data/processed_bank_knowledge.csv"
    
    os.makedirs(os.path.dirname(CLEAN_DATA_FILE), exist_ok=True)
    process_excel_document(INPUT_EXCEL_FILE, CLEAN_DATA_FILE)
