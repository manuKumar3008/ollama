# query.py
import os
import re
import fitz
import pytesseract
from PIL import Image
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

BASE_INDEX = os.path.join(os.path.dirname(__file__), "../vectorstore")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "../uploads")

def extract_doc_name_from_question(question: str):
    patterns = [
        r"(?:document|from)\s+(?:named|called)?[\"']?([\w\s]+)[\"']?",  # English
        r"Dokument(?:\s+mit\s+dem\s+Namen)?\s+([a-zA-Z0-9_\s]+)",        # German
    ]
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1).strip().replace(" ", "_")
    return None

def get_available_documents(user_id: str):
    user_path = os.path.join(BASE_INDEX, user_id)
    if os.path.exists(user_path):
        return [d for d in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, d))]
    return []

def count_words_in_pdf(filepath):
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

def query_router(user_id: str, question: str, history: list = None) -> str:
    doc_name = extract_doc_name_from_question(question)
    user_docs = get_available_documents(user_id)
    if not user_docs:
        return "❌ Für diesen Benutzer wurden keine Dokumente gefunden."
    if not doc_name:
        return "❌ Bitte gib in deiner Frage an, auf welches Dokument du dich beziehst (z. B. 'vom Dokument Beispielbericht')."

    normalized_docs = [d.lower().replace(" ", "_") for d in user_docs]
    doc_name_normalized = doc_name.lower().replace(" ", "_")

    if doc_name_normalized not in normalized_docs:
        return f"📂 Dokument *{doc_name}* wurde nicht gefunden. Verfügbare Dokumente: {', '.join([doc.replace('_', ' ') for doc in user_docs])}"

    doc_name = user_docs[normalized_docs.index(doc_name_normalized)]

    if "anzahl" in question.lower() and "wörter" in question.lower():
        file_path = os.path.join(UPLOADS_DIR, user_id, f"{doc_name.replace('_', ' ')}.pdf")
        if not os.path.exists(file_path):
            return f"📂 Quelldatei für *{doc_name.replace('_', ' ')}* nicht gefunden."
        word_count = count_words_in_pdf(file_path)
        return f"📄 *{doc_name.replace('_', ' ')}* enthält ungefähr **{word_count} Wörter**."

    doc_path = os.path.join(BASE_INDEX, user_id, doc_name)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    llm = OllamaLLM(model="llama3.2")
    vectorstore = FAISS.load_local(doc_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)

    full_query = ""
    if history:
        for h in history:
            full_query += f"Frage: {h['question']}\nAntwort: {h['answer']}\n"
    full_query += f"Frage: {question}\nAntworte in Deutsch."

    result = qa.invoke({"query": full_query})
    for key in ['result', 'output', 'answer']:
        if key in result:
            return f"📄 *{doc_name.replace('_', ' ')}*: {result[key].strip()}"
    return f"📄 *{doc_name.replace('_', ' ')}*: {next(iter(result.values())).strip()}"