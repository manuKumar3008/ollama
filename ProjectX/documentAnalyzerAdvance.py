import os
import docx
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
import speech_recognition as sr
from PIL import Image  # To open image files
from moviepy import VideoFileClip
import subprocess
from collections import defaultdict
import cv2

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# Extract text from supported file types (text, pdf, docx, image, and video)
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        # Text files
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        # PDF files
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])

        # Word documents
        elif ext == '.docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])

        # Image files (OCR)
        elif ext in ['.png', '.jpg', '.jpeg']:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        # Video files (Speech-to-text and OCR)
        elif ext in ['.mp4', '.avi', '.mov']:
            text = extract_text_from_video(file_path)
        
    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return None

    return text[:1500] if text else None  # Limit to 1500 chars

# Extract text from video (audio-to-text and OCR on frames)
def extract_text_from_video(video_file):
    # Extract speech-to-text from the audio
    print(f"Extracting audio from video: {video_file}")
    audio_file = extract_audio_from_video(video_file)
    transcribed_text = transcribe_audio_to_text(audio_file)
    
    # Extract text from frames using OCR
    frames = extract_frames_from_video(video_file)
    ocr_text = ocr_on_frames(frames)
    
    # Combine both transcribed audio text and OCR text
    return transcribed_text + "\n\n" + "\n".join(ocr_text)

def extract_audio_from_video(video_file):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio_file = "extracted_audio.wav"
    audio.write_audiofile(audio_file)
    return audio_file

def transcribe_audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text

def extract_frames_from_video(video_file):
    video = cv2.VideoCapture(video_file)
    frame_list = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        frame_list.append(frame)
    video.release()
    return frame_list

def ocr_on_frames(frames):
    texts = []
    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        if text.strip():
            texts.append(text)
    return texts

# Send prompt to Ollama model
def query_ollama(prompt, model="llama3.2"):
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout.strip()

# Get document type from text
def get_document_type(text, model="llama3.2"):
    prompt = (
        "What type of document is this? Give a short answer like 'Resume', 'Invoice', "
        "'Report', 'Letter', 'Legal Document', 'Contract', etc.\n\n"
        f"{text}"
    )
    return query_ollama(prompt, model)

# Get summary for PDF documents
def get_pdf_summary(text, model="llama3.2"):
    prompt = (
        "Summarize the following document briefly in 2-3 sentences:\n\n"
        f"{text}"
    )
    return query_ollama(prompt, model)

# Main function to process all files
def detect_document_types_in_folder(folder_path):
    doc_type_counts = defaultdict(int)

    while True:
        print("\nOptions:")
        print("1. Search document by name without extension and get summary")
        print("2. Search and get summary for a specific document")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            file_name = input("Enter file name without extension: ").strip().lower()
            found = False

            for filename in os.listdir(folder_path):
                if file_name in filename.lower():  # Search for file without extension
                    file_path = os.path.join(folder_path, filename)
                    text = extract_text_from_file(file_path)

                    if text:
                        print(f"\nDocument found: {filename}")
                        doc_type = get_document_type(text)
                        print(f"Document Type: {doc_type}")

                        if filename.lower().endswith('.pdf'):
                            choice_summary = input("Show summary for this PDF? (Y/N): ").strip().lower()
                            if choice_summary == 'y':
                                summary = get_pdf_summary(text)
                                print("Summary:", summary)
                        found = True
                    break

            if not found:
                print(f"Document with name '{file_name}' not found.")
        
        elif choice == "2":
            file_name = input("Enter file name (with or without extension): ").strip().lower()
            found = False

            for filename in os.listdir(folder_path):
                if file_name in filename.lower():  # Search for file name (with or without extension)
                    file_path = os.path.join(folder_path, filename)
                    text = extract_text_from_file(file_path)

                    if text:
                        print(f"\nDocument found: {filename}")
                        doc_type = get_document_type(text)
                        print(f"Document Type: {doc_type}")

                        if filename.lower().endswith('.pdf'):
                            choice_summary = input("Show summary for this PDF? (Y/N): ").strip().lower()
                            if choice_summary == 'y':
                                summary = get_pdf_summary(text)
                                print("Summary:", summary)
                        found = True
                    break

            if not found:
                print(f"Document with name '{file_name}' not found.")

        elif choice == "3":
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")

# Set your folder path here
folder_to_check = "C:/Users/mkumar/OneDrive/Desktop/Appworks/TCCI PROJECT IMAGES/Video of the Form Design"
detect_document_types_in_folder(folder_to_check)
