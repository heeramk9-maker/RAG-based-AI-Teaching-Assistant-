import requests
import os
import json
import numpy as np
import pandas as pd
import joblib

def create_embeddings(text_list):
    """
    Calls the Ollama embedding API to generate embeddings for a list of texts.
    
    Args:
        text_list (list): A list of strings to embed.
        
    Returns:
        list: A list of embedding vectors.
    """
    try:
        r = requests.post("http://localhost:11434/api/embed", json={
            "model": "bge-m3",
            "input": text_list
        })
        r.raise_for_status()  # Raise an exception for bad status codes
        return r.json()["embeddings"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama embedding API: {e}")
        raise RuntimeError("Failed to get embeddings from Ollama.")

def update_embeddings_from_json(json_path, embeddings_file="data/embeddings.joblib"):
    """
    Embeds text segments from a JSON transcript and appends them to the 
    embeddings DataFrame.
    
    Args:
        json_path (str): The path to the JSON transcript file.
        embeddings_file (str): The path to the joblib file to save/load embeddings.
    """
    os.makedirs(os.path.dirname(embeddings_file), exist_ok=True)

    # Load existing embeddings DataFrame or create a new one
    if os.path.exists(embeddings_file):
        df = joblib.load(embeddings_file)
        print("Loaded existing embeddings DataFrame.")
    else:
        df = pd.DataFrame(columns=["chunk_id", "number", "title", "start", "end", "text", "embedding"])
        print("Created new embeddings DataFrame.")

    # Load the new transcript JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    print(f"Creating embeddings for segments in {os.path.basename(json_path)}...")
    texts = [c['text'] for c in content['chunks']]
    embeddings = create_embeddings(texts)

    # Find the next available chunk_id
    next_chunk_id = df['chunk_id'].max() + 1 if not df.empty else 0

    # Create new rows and append to the DataFrame
    new_chunks = []
    for i, chunk in enumerate(content['chunks']):
        new_row = {
            "chunk_id": next_chunk_id + i,
            "number": chunk.get("number"),
            "title": chunk.get("title"),
            "start": chunk.get("start"),
            "end": chunk.get("end"),
            "text": chunk.get("text"),
            "embedding": embeddings[i]
        }
        new_chunks.append(new_row)
    
    df_new = pd.DataFrame.from_records(new_chunks)
    df = pd.concat([df, df_new], ignore_index=True)

    # Save the updated DataFrame back to the file
    joblib.dump(df, embeddings_file)
    print(f"Updated embeddings DataFrame with {len(new_chunks)} new chunks.")

# The functions are now ready to be imported into app.py