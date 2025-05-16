import os
import moviepy as mp
import pytesseract
from PIL import Image
import speech_recognition as sr
import subprocess

# Set Tesseract path if necessary (Change it to your Tesseract path)
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Function to extract text from video frames using OCR
def extract_text_from_video_frames(video_path):
    video = mp.VideoFileClip(video_path)
    frames = video.iter_frames(fps=1, dtype="uint8")  # Adjust FPS for frame rate

    extracted_text = ""
    
    # Process the first 5 frames for demo purposes (you can adjust this)
    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        text = pytesseract.image_to_string(img)
        
        if text.strip():  # Collect frames with text
            extracted_text += text.strip() + "/n"
        
        if i > 5:  # Limiting to 5 frames
            break

    return extracted_text

# Function to extract audio from video and transcribe it
def transcribe_audio_from_video(video_path):
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile("temp_audio.wav")  # Save audio to a temporary file
    
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp_audio.wav") as source:
        audio_data = recognizer.record(source)  # Record the audio
    
    try:
        # Use Google API for speech recognition (you can change this)
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to generate a summary using an external model (e.g., OpenAI GPT or Ollama)
def summarize_text(text):
    # Ensure that the text is not empty or too short
    if len(text.strip()) < 50:
        return "Text is too short to summarize."

    prompt = f"Summarize the following text in 2-3 sentences:/n/n{text}"

    # Use subprocess to run Ollama model or another summarization model
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],  # Replace with your model or API call
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore"
        )
        summary = result.stdout.strip()

        if not summary:
            return "No summary generated."

        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error generating summary."

# Main function to process video and generate summary
def process_video(video_path):
    print(f"Processing video: {video_path}")

    # Extract text from video frames (OCR)
    extracted_text = extract_text_from_video_frames(video_path)
    
    # If no text extracted from frames, extract from audio (transcription)
    if not extracted_text:
        print("No text found in frames, extracting from audio...")
        extracted_text = transcribe_audio_from_video(video_path)

    if extracted_text:
        # Get the summary of the extracted text
        summary = summarize_text(extracted_text)
        print("\nSummary:")
        print(summary)
    else:
        print("No text could be extracted from the video.")

# Input video path (adjust as per your file)
video_path = "C:/Users/mkumar/OneDrive/Desktop/Appworks/TCCI PROJECT IMAGES/Video of the Form Design/Scheduler Manager .mp4"  # Provide the correct video path here

# Call the function to process the video
process_video(video_path)
