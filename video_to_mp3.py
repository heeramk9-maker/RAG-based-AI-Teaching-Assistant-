import os
import subprocess

def convert_video_to_mp3(video_path, output_dir="audios"):
    """
    Converts a single video file to MP3 using ffmpeg.

    Args:
        video_path (str): The full path to the input video file.
        output_dir (str): The directory to save the MP3 output.
    
    Returns:
        str: The path to the generated MP3 file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract filename without extension
    base_filename = os.path.splitext(os.path.basename(video_path))[0]
    
    # Check for the specific naming convention and clean it up
    if " | " in base_filename:
        # Example: "C++ #11 | Vectors in C++" -> "11_Vectors in C++"
        parts = base_filename.split(" | ")
        tutorial_number = parts[0].split(" #")[1]
        file_name = parts[1]
        output_filename = f"{tutorial_number}_{file_name}.mp3"
    else:
        # Fallback for other naming conventions
        output_filename = f"{base_filename}.mp3"
        
    mp3_path = os.path.join(output_dir, output_filename)
    
    try:
        # Run ffmpeg command to extract audio
        subprocess.run(
            ["ffmpeg", "-i", video_path, mp3_path], 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"Successfully converted {video_path} to {mp3_path}")
        return mp3_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting video: {e.stderr}")
        raise RuntimeError(f"FFmpeg failed to convert the video: {e.stderr}")