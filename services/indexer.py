import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

from pdf2image import convert_from_path
from pytesseract import image_to_string
from langchain_core.documents import Document

VECTOR_DIR = "vectorstore"

# Optional: Set this if tesseract is not in PATH
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_via_ocr(pdf_path):
    print("[INFO] Performing OCR fallback...")
    images = convert_from_path(pdf_path)
    text = ""
    for i, img in enumerate(images):
        page_text = image_to_string(img)
        text += f"\n\nPage {i+1}:\n" + page_text
    return [Document(page_content=text)]

def index_documents(user_id: str, doc_name: str, file_path: str):
    print(f"[INFO] Indexing document: {file_path}")

    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        if not documents or all(len(doc.page_content.strip()) == 0 for doc in documents):
            raise ValueError("Empty document content")
    except Exception as e:
        print(f"[WARN] Failed standard load: {str(e)}")
        documents = extract_text_via_ocr(file_path)

    if not documents:
        raise ValueError(f"No content extracted from {file_path}. Is it a valid PDF?")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError(f"Text splitting failed. No chunks generated from {file_path}.")

    print(f"[INFO] Total chunks extracted: {len(chunks)}")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    try:
        vectorstore = FAISS.from_documents(chunks, embeddings)
    except IndexError:
        raise ValueError("No embeddings were created. The document might be empty or embedding failed.")

    save_dir = os.path.join(VECTOR_DIR, user_id, doc_name)
    os.makedirs(save_dir, exist_ok=True)
    vectorstore.save_local(save_dir)
    print(f"[SUCCESS] Vectorstore saved to {save_dir}")

def list_user_documents(user_id: str):
    user_dir = os.path.join(VECTOR_DIR, user_id)
    if not os.path.exists(user_dir):
        return []
    return os.listdir(user_dir)
