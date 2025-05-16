import os
import docx
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
from PIL import Image
import subprocess
from collections import defaultdict

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# List of supported extensions
SUPPORTED_EXTENSIONS = ['.txt', '.docx', '.pdf', '.png', '.jpg', '.jpeg']

# Extract text from supported file types
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

# Get document type
def get_document_type(text, model="llama3.2"):
    prompt = (
        "What type of document is this? Give a short answer like 'Resume', 'Invoice', "
        "'Report', 'Letter', 'Legal Document', 'Contract', etc.\n\n"
        f"{text}"
    )
    return query_ollama(prompt, model)

# Get summary
def get_summary(text, model="llama3.2"):
    prompt = (
        "Summarize the following document briefly in 2-3 sentences:\n\n"
        f"{text}"
    )
    return query_ollama(prompt, model)

# Search for file without knowing the extension
def find_file_by_name(folder_path, base_name):
    for file in os.listdir(folder_path):
        name, ext = os.path.splitext(file)
        if name.lower() == base_name.lower() and ext.lower() in SUPPORTED_EXTENSIONS:
            return os.path.join(folder_path, file)
    return None

# Main function
def main():
    folder_path = "C:/Users/mkumar/OneDrive/Pictures/Screenshots"
    base_name = input("Enter file name without extension: ").strip()

    file_path = find_file_by_name(folder_path, base_name)
    if not file_path:
        print("File not found with supported extension.")
        return

    print(f"\nFound file: {os.path.basename(file_path)}")
    text = extract_text_from_file(file_path)
    if not text:
        print("Could not extract text.")
        return

    # Document type
    doc_type = get_document_type(text)
    doc_type = doc_type.split('\n')[0].strip().capitalize()
    print(f"Document Type: {doc_type}")

    # Summary if PDF or image
    if file_path.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        choice = input("Show summary for this file? (Y/N): ").strip().lower()
        if choice == 'y':
            summary = get_summary(text)
            print("Summary:", summary)

if __name__ == "__main__":
    main()
