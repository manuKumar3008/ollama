import os
import traceback
from langdetect import detect
from langchain_community.vectorstores import FAISS
from langchain_mistralai import ChatMistralAI
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA
from services.prompt import render_prompt
from services.chitchat_filter import detect_chitchat

# === Mistral API Key ===
MISTRAL_API_KEY = "AV7Bn0Douoc9YqtAKcRyFZcxiZD4zfbs"
VECTOR_DIR = "vectorstore"

# === Utility Functions ===

def get_available_documents(user_id: str):
    user_dir = os.path.join(VECTOR_DIR, user_id)
    return os.listdir(user_dir) if os.path.exists(user_dir) else []

def normalize_doc_name(name: str) -> str:
    name = name.lower().replace('_', ' ').replace('-', ' ')
    return ' '.join(name.split())

def extract_doc_name_from_question(question: str, user_docs: list) -> str:
    question_lower = question.lower()
    tokens = question_lower.split()
    preps = [
        "from", "in", "of", "about", "regarding", "related to",
        "based on", "including", "within", "concerning", "document",
        "file", "report", "pdf", "doc",
        "von", "vom", "aus", "im", "bericht", "dokument"
    ]
    normalized_docs = {normalize_doc_name(doc): doc for doc in user_docs}
    for prep in preps:
        if prep in question_lower:
            prep_tokens = prep.split()
            for i in range(len(tokens)):
                if tokens[i:i + len(prep_tokens)] == prep_tokens:
                    max_len = max(len(normalize_doc_name(doc).split()) for doc in user_docs)
                    for length in range(max_len, 0, -1):
                        candidate_tokens = tokens[i + len(prep_tokens): i + len(prep_tokens) + length]
                        candidate_str = ' '.join(candidate_tokens).strip()
                        if normalize_doc_name(candidate_str) in normalized_docs:
                            return normalized_docs[normalize_doc_name(candidate_str)]
    normalized_question = normalize_doc_name(question)
    for norm_doc, original_doc in normalized_docs.items():
        if norm_doc in normalized_question:
            return original_doc
    return None

# === Main Query Router ===

def query_router(user_id: str, question: str, history: list = None) -> str:
    try:
        lang = detect(question)
    except:
        lang = "de"

    # 📂 Load documents
    user_docs = get_available_documents(user_id)
    if not user_docs:
        return "❌ Für diesen Benutzer wurden keine Dokumente gefunden." if lang == "de" else "❌ No documents found for this user."

    # 🔍 Try to detect document name first
    doc_name = extract_doc_name_from_question(question, user_docs)

    # 🧠 If NO document name is found → check for chitchat
    if not doc_name:
        chitchat_response = detect_chitchat(question, lang)
        if chitchat_response:
            return chitchat_response
        return "❌ Bitte gib in deiner Frage an, auf welches Dokument du dich beziehst." if lang == "de" else "❌ Please specify the document you're referring to in your question."

    # 📝 Match document name
    doc_name_norm = normalize_doc_name(doc_name)
    matched_doc = next((d for d in user_docs if normalize_doc_name(d) == doc_name_norm), None)

    if matched_doc is None:
        available = ", ".join(user_docs)
        return (
            f"📂 Dokument *{doc_name}* wurde nicht gefunden. Verfügbare Dokumente: {available}"
            if lang == "de" else
            f"📂 Document *{doc_name}* not found. Available documents: {available}"
        )

    doc_path = os.path.join(VECTOR_DIR, user_id, matched_doc)
    if not os.path.exists(doc_path):
        return f"❌ Vectorstore not found for document {matched_doc}"

    # 🔍 Run Retrieval QA
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = FAISS.load_local(doc_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever()

        llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-small")
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
            chain_type="stuff"
        )

        full_query = render_prompt(history or [], question, lang)
        result = qa.invoke({"query": full_query})

        response_text = result.get('result') or result.get('output') or result.get('answer') or result.get('text')
        if response_text:
            return f"📄 *{matched_doc}*: {response_text.strip()}"

        return f"📄 *{matched_doc}*: ⚠️ Unexpected response format: {result}"

    except Exception as e:
        print("❌ Exception during query:")
        traceback.print_exc()
        return f"❌ Query failed: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
