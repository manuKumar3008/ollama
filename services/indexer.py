import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_DIR = "vectorstore"

def index_documents(user_id: str, doc_name: str, file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")  # ✅ Ollama model
    vectorstore = FAISS.from_documents(chunks, embeddings)

    save_dir = os.path.join(VECTOR_DIR, user_id, doc_name)
    os.makedirs(save_dir, exist_ok=True)
    vectorstore.save_local(save_dir)

def list_user_documents(user_id: str):
    user_dir = os.path.join(VECTOR_DIR, user_id)
    if not os.path.exists(user_dir):
        return []
    return os.listdir(user_dir)
