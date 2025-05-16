import os
import subprocess
import pytesseract
import fitz  # PyMuPDF
import docx
from PIL import Image
import magic
from collections import defaultdict

# Update Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# Detect MIME type based on content
def detect_mime_type(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

# Extract text based on file type
def extract_text(file_path, mime_type):
    try:
        if 'pdf' in mime_type:
            doc = fitz.open(file_path)
            return "\n".join([page.get_text() for page in doc])
        elif 'wordprocessingml.document' in mime_type:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif 'text' in mime_type:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif 'image' in mime_type:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        else:
            return None
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None

# Send a prompt to Ollama
def query_ollama(prompt, model="llama3.2"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore"
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error communicating with Ollama: {e}"

# Detect document type
def detect_document_type(text):
    prompt = f"What type of document is this? Give a short answer like 'Resume', 'Invoice', 'Contract', etc.\n\n{text}"
    return query_ollama(prompt)

# Generate a summary
def summarize_document(text):
    prompt = f"Summarize this document in 2-3 sentences:\n\n{text}"
    return query_ollama(prompt)

# Search and analyze a document by name (no extension needed)
def find_document_by_name(folder_path, filename_base):
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)) and file.lower().startswith(filename_base.lower()):
            return os.path.join(folder_path, file)
    return None

# Interface
def main():
    folder_path = input("Enter the folder path to search documents: ").strip()

    while True:
        print("\nMenu:")
        print("1. Search document by name (no extension), detect type, and get summary")
        print("2. Get summary of another document")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1' or choice == '2':
            filename_base = input("Enter the document name (without extension): ").strip()
            file_path = find_document_by_name(folder_path, filename_base)

            if not file_path:
                print("Document not found.")
                continue

            mime_type = detect_mime_type(file_path)
            file_extension = os.path.splitext(file_path)[1]  # Get the file extension
            print(f"Detected MIME type: {mime_type}")

            text = extract_text(file_path, mime_type)

            if not text:
                print("Failed to extract text.")
                continue

            print(f"\nFile: {os.path.basename(file_path)}")
            print(f"File Extension: {file_extension}")  # Display the file extension

            # Detect document type
            doc_type = detect_document_type(text[:1500])
            print(f"Document Type: {doc_type.splitlines()[0].strip()}")

            # Ask for summary
            ask_summary = input("Show summary of this document? (Y/N): ").strip().lower()
            if ask_summary == 'y':
                summary = summarize_document(text[:1500])
                print(f"\nSummary:\n{summary}")

        elif choice == '3':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
