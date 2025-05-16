import os
import docx
import fitz
import subprocess
from collections import defaultdict

# Extract text from .txt, .pdf, .docx
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
    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return None

    return text[:1500] if text else None

# Call Ollama with a custom prompt
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

# Get summary of PDF
def get_pdf_summary(text, model="llama3.2"):
    prompt = (
        "Summarize the following document briefly in 2-3 sentences:\n\n"
        f"{text}"
    )
    return query_ollama(prompt, model)

# Analyze all files in folder
def detect_document_types_in_folder(folder_path):
    doc_type_counts = defaultdict(int)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            text = extract_text_from_file(file_path)
            if text:
                print(f"\nAnalyzing: {filename}")
                try:
                    doc_type = get_document_type(text)
                    doc_type = doc_type.split('\n')[0].strip().capitalize()
                    print(f"{filename}: {doc_type}")

                    # If PDF, ask user whether to show summary
                    if file_path.lower().endswith('.pdf'):
                        user_choice = input("Show summary for this PDF? (Y/N): ").strip().lower()
                        if user_choice == 'y':
                            summary = get_pdf_summary(text)
                            print("Summary:", summary)

                    doc_type_counts[doc_type] += 1

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            else:
                print(f"Skipped (unsupported or empty): {filename}")

    # Print document type summary
    print("\nDocument Type Summary:")
    for doc_type, count in sorted(doc_type_counts.items(), key=lambda x: -x[1]):
        print(f"{doc_type}: {count}")

# Folder to analyze
folder_to_check = "C:/Users/mkumar/OneDrive/Desktop/Appian training"
detect_document_types_in_folder(folder_to_check)
