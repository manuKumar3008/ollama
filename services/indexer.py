import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from langchain_ollama import OllamaEmbeddings  # updated import
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

BASE_UPLOADS = os.path.join(os.path.dirname(__file__), "../uploads")
BASE_INDEX = os.path.join(os.path.dirname(__file__), "../vectorstore")
os.makedirs(BASE_UPLOADS, exist_ok=True)
os.makedirs(BASE_INDEX, exist_ok=True)

def extract_text_from_pdf(filepath):
    full_text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text = page.get_text().strip()
            if text:
                full_text += text + "\n"
            else:
                # Convert page to image for OCR
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                full_text += ocr_text + "\n"
    return full_text

def index_documents(user_id, doc_name, filepath):
    raw_text = extract_text_from_pdf(filepath)
    if not raw_text.strip():
        raise ValueError("No extractable text found.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(raw_text)
    documents = [Document(page_content=chunk) for chunk in chunks]

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = FAISS.from_documents(documents, embeddings)

    save_path = os.path.join(BASE_INDEX, user_id, doc_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    vectordb.save_local(save_path)

def list_user_documents(user_id):
    user_dir = os.path.join(BASE_UPLOADS, user_id)
    return os.listdir(user_dir) if os.path.exists(user_dir) else []
