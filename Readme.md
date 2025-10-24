# How to use this RAG AI Teaching assistant on your own data
## Step 1 - Collect your videos
Move all your video files to the videos folder

## Step 2 - Convert to MP3
Convert all the video files to MP3 by running video_to_mp3

## Step 3 - Convert mp3 to json 
Convert all the MP3 files to JSON by running mp3_to_json

## Step 4 - Convert the JSON files to Vectors
Use the file preprocess_json to convert the JSON files to a dataframe with Embeddings and save it as a joblib pickle

## Step 5 - Prompt generation and feeding to LLM

Read the joblib file and load it into the memory. Then, create a relevant prompt as per the user query and feed it to the LLM


#Interface Overview

## Initial Website Interface
<img width="1911" height="982" alt="image" src="https://github.com/user-attachments/assets/2bfa12e0-c627-4222-ab64-445d5c356fe9" />
## AI-Generated Response Example
<img width="1903" height="976" alt="image" src="https://github.com/user-attachments/assets/afad1009-1521-4ca3-aafc-264a2ce2c12a" />
