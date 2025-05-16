import os
import docx  # For DOCX text extraction
import fitz  # For PDF text extraction (PyMuPDF)
import subprocess
from collections import defaultdict

# Function to extract text from supported file types
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()  # Get file extension
    text = ""

    try:
        # Handle .txt files
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        # Handle .pdf files using PyMuPDF
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])

        # Handle .docx files using python-docx
        elif ext == '.docx':
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])

    except Exception as e:
        print(f"Failed to extract text from {file_path}: {e}")
        return None

    # Return first 1500 characters for faster processing
    return text[:1500] if text else None

# Function to send text to Ollama model and get document type
def query_ollama(text, model="llama3.2"):
    prompt = (
        "What type of document is this? Give a short answer like 'Resume', 'Invoice', "
        "'Report', 'Letter', 'Legal Document', 'Contract', etc.\n\n"
        f"{text}"
    )
    # Call Ollama with subprocess and return the model's output
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",  # Ensure UTF-8 encoding is used
        errors="ignore"    # Ignore any characters that can't be decoded
    )
    return result.stdout.strip()

# Main function to analyze all files in a folder
def detect_document_types_in_folder(folder_path):
    doc_type_counts = defaultdict(int)  # Dictionary to count each doc type

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip if it's not a file
        if os.path.isfile(file_path):
            text = extract_text_from_file(file_path)  # Extract text content

            if text:
                print(f"Analyzing: {filename}")
                try:
                    # Send to model and get type
                    doc_type = query_ollama(text)

                    # Clean and standardize the result
                    doc_type = doc_type.split('\n')[0].strip().capitalize()

                    # Print and count the type
                    print(f"{filename}: {doc_type}")
                    doc_type_counts[doc_type] += 1
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            else:
                print(f"Skipped (unsupported or empty): {filename}")

    # Print a summary of document types found
    print("\nDocument Type Summary:")
    for doc_type, count in sorted(doc_type_counts.items(), key=lambda x: -x[1]):
        print(f"{doc_type}: {count}")

# Set the folder path to analyze
folder_to_check = "C:/Users/mkumar/OneDrive/Desktop/Appian training"
detect_document_types_in_folder(folder_to_check)
