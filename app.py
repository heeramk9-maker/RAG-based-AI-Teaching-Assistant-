import json
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import requests

app = Flask(__name__)
CORS(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'videos'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory store to simulate video processing and data storage.
# In a real-world scenario, this would be a database like Firestore or a vector DB.
video_data_store = {}
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def is_ollama_running():
    """
    Checks if the Ollama server is running.
    """
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def allowed_file(filename):
    """
    Checks if a file's extension is in the allowed list.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/')
def home():
    return "Flask server is running! Try /api/videos or /api/ask"


@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    """
    Endpoint to handle video file uploads.
    
    This endpoint simulates video processing:
    1. Receives the video file from the request.
    2. Saves the file to a local directory.
    3. Simulates generating a transcription and embeddings.
    4. Returns a success message with a video ID (the filename).
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to the upload folder
        file.save(filepath)
        
        # Simulate processing time
        time.sleep(2)
        
        # Store a mock transcription for RAG purposes
        video_data_store[filename] = {
            "transcription": (
                "This video discusses the basics of Retrieval-Augmented Generation, or RAG. "
                "It explains how RAG combines a retrieval component and a generation component to improve "
                "the factual accuracy of large language models. The retrieval part searches a "
                "knowledge base, while the generation part uses the retrieved information to "
                "formulate a grounded response. The speaker also mentions a project on "
                "video RAG, which is a new and exciting application of this technology."
            ),
            "url": f"/api/videos/{filename}"
        }
        
        return jsonify({
            "message": "Video uploaded and processing initiated successfully.",
            "videoId": filename
        }), 200
    
    return jsonify({"error": "File type not allowed."}), 400

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """
    Endpoint to get a list of all uploaded video files.
    
    It scans the UPLOAD_FOLDER and returns a list of filenames.
    """
    try:
        video_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
        return jsonify({"videos": video_files}), 200
    except FileNotFoundError:
        return jsonify({"error": "Video directory not found."}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/videos/<filename>', methods=['GET', 'DELETE'])
def handle_video(filename):
    """
    Endpoint to serve or delete a video file from the server.
    """
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if request.method == 'DELETE':
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                # Also remove from the in-memory data store
                if filename in video_data_store:
                    del video_data_store[filename]
                return jsonify({"message": f"Video '{filename}' deleted successfully."}), 200
            except OSError as e:
                return jsonify({"error": f"Error deleting file: {e}"}), 500
        else:
            return jsonify({"error": "Video file not found."}), 404
    
    elif request.method == 'GET':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """
    Endpoint for asking a question about a processed video.
    
    This endpoint simulates the RAG process. In a real application, this would:
    1. Receive a question and video ID.
    2. Use the question to perform a semantic search on the video's embeddings.
    3. Retrieve the most relevant text chunks from the video transcription.
    4. Augment a prompt for the LLM with the retrieved text.
    5. Call the LLM to generate a grounded answer.
    """
    data = request.get_json()
    video_id = data.get('videoId')
    question = data.get('question')

    if not video_id or not question:
        return jsonify({"error": "Missing videoId or question."}), 400
    
    video_info = video_data_store.get(video_id)
    if not video_info:
        return jsonify({"error": "Video ID not found. Please upload the video first."}), 404

    # Check if Ollama is running before trying to call it
    if not is_ollama_running():
        return jsonify({"error": "Ollama server is not running or not reachable."}), 503

    try:
        # Simulate the RAG process using a simple keyword search.
        # This is a placeholder for a real semantic search and LLM call.
        relevant_text = ""
        if "rag" in question.lower() or "retrieval" in question.lower():
            relevant_text = video_info["transcription"]
        else:
            relevant_text = "The video doesn't contain information on that specific topic."
        
        # Simulate the LLM generating a response based on the relevant text
        time.sleep(2)
        answer = f"Based on the video's content, here is the answer to your question: '{relevant_text}'."

        return jsonify({"answer": answer}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Ollama: {str(e)}"}), 500

if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)
