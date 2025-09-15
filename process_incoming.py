import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.metrics.pairwise import cosine_similarity
import os

def load_embeddings(file_path="data/embeddings.joblib"):
    """
    Loads the embeddings DataFrame from a joblib file.
    
    Args:
        file_path (str): The path to the joblib file.
        
    Returns:
        pandas.DataFrame: The loaded DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Embeddings file not found at {file_path}. Please upload a video first.")
    
    print("Loading embeddings...")
    return joblib.load(file_path)

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

def find_similar_chunks(df, query_embedding, top_n=5):
    """
    Finds and returns the top N most similar chunks based on cosine similarity.
    
    Args:
        df (pandas.DataFrame): The DataFrame containing embeddings.
        query_embedding (list): The embedding of the user's query.
        top_n (int): The number of top results to retrieve.
        
    Returns:
        pandas.DataFrame: A DataFrame containing the most relevant chunks.
    """
    similarities = cosine_similarity(np.vstack(df['embedding']), [query_embedding]).flatten()
    top_indices = similarities.argsort()[::-1][:top_n]
    return df.iloc[top_indices]

def generate_response(question, relevant_df):
    """
    Generates a response using Ollama and relevant context chunks.
    
    Args:
        question (str): The user's question.
        relevant_df (pandas.DataFrame): The DataFrame of relevant context chunks.
        
    Returns:
        str: The generated answer from the LLM.
    """
    prompt_context = relevant_df[['title', 'number', 'start', 'end', 'text']].to_json(orient="records")
    
    prompt = f"""I am teaching web development in my Sigma web development course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{prompt_context}
---------------------------------
"{question}"
User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course.
"""
    print("Sending prompt to Ollama...")
    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        })
        r.raise_for_status()
        return r.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama generate API: {e}")
        raise RuntimeError("Failed to get an answer from the LLM.")