import os
from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_ollama import OllamaEmbeddings

def index_document(user_id: str, file_path: str):
    print(f"[INFO] Indexing document for user: {user_id}")

    # Load document text
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    # Initialize embeddings
    embeddings = OllamaEmbeddings(model="llama2-embeddings")  # Update model as needed

    # Create vectorstore
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore for the user
    vectorstore_dir = os.path.join("vectorstore", user_id)
    if not os.path.exists(vectorstore_dir):
        os.makedirs(vectorstore_dir)
    vectorstore.save_local(vectorstore_dir)
