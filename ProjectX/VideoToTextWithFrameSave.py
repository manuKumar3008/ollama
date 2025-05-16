import os
import docx
import fitz  # PyMuPDF for PDFs
import pytesseract
import subprocess
from PIL import Image
from collections import defaultdict
from moviepy import VideoFileClip

# Set Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
        elif ext == '.docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext in ['.png', '.jpg', '.jpeg']:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return None

    return text[:1500] if text else None

def get_summary(text, model="llama3.2"):
    prompt = f"Summarize the following text in 2-3 sentences:\n\n{text}"
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout.strip()

def get_document_type(text, model="llama3.2"):
    prompt = (
        "What type of document is this? Give a short answer like 'Resume', 'Invoice', 'Report', 'Letter', etc.\n\n"
        f"{text}"
    )
    return get_summary(prompt, model)

def find_file_without_extension(folder, filename_no_ext):
    for fname in os.listdir(folder):
        if os.path.isfile(os.path.join(folder, fname)):
            name, _ = os.path.splitext(fname)
            if name.lower() == filename_no_ext.lower():
                return os.path.join(folder, fname)
    return None

def summarize_video(video_path, save_frames_path="frames", max_frames=5):
    os.makedirs(save_frames_path, exist_ok=True)
    video = VideoFileClip(video_path)
    frames = video.iter_frames(fps=1, dtype="uint8")

    text_collected = ""
    for i, frame in enumerate(frames):
        img = Image.fromarray(frame)
        text = pytesseract.image_to_string(img)
        if text.strip():
            text_collected += text.strip() + "\n"
        img.save(os.path.join(save_frames_path, f"frame_{i}.png"))
        if i >= max_frames - 1:
            break

    if text_collected.strip():
        summary = get_summary(text_collected)
        if summary.strip():
            print("\nSummary from video frames:\n", summary)
        else:
            print("Summary returned blank. Possibly due to weak OCR text.")
    else:
        print("No text detected in video frames.")

def main():
    folder_path = input("Enter the folder path: ").strip()
    while True:
        print("\nOptions:")
        print("1. Search document by filename (no extension)")
        print("2. Summarize a document by filename")
        print("3. Summarize video file by filename (no extension)")
        print("4. Exit")

        choice = input("Enter choice (1/2/3/4): ").strip()

        if choice == '1':
            name = input("Enter filename (without extension): ").strip()
            path = find_file_without_extension(folder_path, name)
            if path:
                text = extract_text_from_file(path)
                if text:
                    doc_type = get_document_type(text)
                    print(f"Document Type: {doc_type}")
                    if path.endswith('.pdf'):
                        show = input("Show summary? (Y/N): ").strip().lower()
                        if show == 'y':
                            print(get_summary(text))
                else:
                    print("Could not extract text.")
            else:
                print("File not found.")

        elif choice == '2':
            name = input("Enter filename (without extension): ").strip()
            path = find_file_without_extension(folder_path, name)
            if path:
                text = extract_text_from_file(path)
                if text:
                    print("Summary:", get_summary(text))
                else:
                    print("Text not found or unreadable.")
            else:
                print("File not found.")

        elif choice == '3':
            name = input("Enter video filename (without extension): ").strip()
            path = find_file_without_extension(folder_path, name)
            if path and path.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                summarize_video(path, save_frames_path=os.path.join(folder_path, "frames"))
            else:
                print("Video file not found or unsupported format.")

        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
