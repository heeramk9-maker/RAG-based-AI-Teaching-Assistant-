import whisper
import json
import os

# Load the Whisper model only once when the module is imported
# This avoids reloading the model on every request, which is a major performance bottleneck
model = whisper.load_model("large-v2")

def transcribe_audio_to_json(audio_path, json_dir="jsons"):
    """
    Transcribes a single audio file and saves the transcription
    segments to a JSON file.
    
    Args:
        audio_path (str): The path to the input audio file.
        json_dir (str): The directory to save the JSON output.
    
    Returns:
        str: The path to the generated JSON file.
    """
    os.makedirs(json_dir, exist_ok=True)
    
    print(f"Transcribing {audio_path}...")
    
    # Transcribe the audio file using the loaded model
    result = model.transcribe(
        audio=audio_path,
        language="hi",
        task="translate",
        word_timestamps=False
    )
    
    # Extract metadata (assuming the format remains)
    filename = os.path.basename(audio_path)
    if "_" in filename:
        parts = filename.split("_")
        number = parts[0]
        title = parts[1].rsplit('.', 1)[0]
    else:
        # Handle cases without the number_title format
        number = "unknown"
        title = filename.rsplit('.', 1)[0]
        
    chunks = []
    for segment in result["segments"]:
        chunks.append({
            "number": number,
            "title": title,
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        })
    
    chunks_with_metadata = {"chunks": chunks, "full_text": result["text"]}
    
    # Define the output JSON path
    json_path = os.path.join(json_dir, f"{filename}.json")
    
    # Save the transcription to a JSON file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=4)
        
    return json_path