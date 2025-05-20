import os
import re
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

BASE_INDEX = os.path.join(os.path.dirname(__file__), "../vectorstore")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "../uploads")

def extract_doc_name_from_question(question: str):
    match = re.search(r"(?:document|from)\s+(?:named|called)?[\"']?([\w\s]+)[\"']?", question, re.IGNORECASE)
    if match:
        return match.group(1).strip().replace(" ", "_")
    return None

def get_available_documents(user_id: str):
    user_path = os.path.join(BASE_INDEX, user_id)
    if os.path.exists(user_path):
        return [d for d in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, d))]
    return []

def count_words_in_pdf(filepath):
    """
    Extracts text (with OCR fallback) and counts the number of words in the PDF.
    """
    word_count = 0
    with fitz.open(filepath) as doc:
        for page in doc:
            text = page.get_text().strip()
            if not text:
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
            word_count += len(text.split())
    return word_count

def query_router(user_id: str, question: str) -> str:
    doc_name = extract_doc_name_from_question(question)
    user_docs = get_available_documents(user_id)

    if not user_docs:
        return "No documents are indexed for this user."

    if not doc_name:
        return "❌ Please specify which document you're referring to in your question (e.g., 'from document Scheduler Working')."

    if doc_name not in user_docs:
        return f"📂 Document *{doc_name}* was not found. Available documents: {', '.join(user_docs)}"

    # 🧠 Word count question detected
    if "count" in question.lower() and "word" in question.lower():
        file_path = os.path.join(UPLOADS_DIR, user_id, f"{doc_name}.pdf")
        if not os.path.exists(file_path):
            return f"📂 Source file for *{doc_name}* not found."
        word_count = count_words_in_pdf(file_path)
        return f"📄 *{doc_name}* contains approximately **{word_count} words**."

    # 🤖 Default: LLM-powered QA
    doc_path = os.path.join(BASE_INDEX, user_id, doc_name)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    llm = OllamaLLM(model="llama3")

    vectorstore = FAISS.load_local(doc_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)
    result = qa.invoke({"query": question})

    for key in ['result', 'output', 'answer']:
        if key in result:
            return f"📄 *{doc_name}*: {result[key].strip()}"
    return f"📄 *{doc_name}*: {next(iter(result.values())).strip()}"
