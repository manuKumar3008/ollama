import os
from langdetect import detect
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA

VECTOR_DIR = "vectorstore"

def normalize_doc_name(name: str) -> str:
    name = name.lower().replace('_', ' ')
    name = ' '.join(name.split())
    return name

def get_available_documents(user_id: str):
    user_dir = os.path.join(VECTOR_DIR, user_id)
    if not os.path.exists(user_dir):
        return []
    return os.listdir(user_dir)

def extract_doc_name_from_question(question: str) -> str:
    question_lower = question.lower()
    tokens = question_lower.split()

    preps = [
    # English
    "from", "from the", "in", "inside", "of", "about", "regarding", "related to",
    "based on", "including", "within", "concerning", "according to", "as per",
    "document", "file", "report", "text", "pdf", "doc",

    # German
    "von", "vom", "vom dokument", "aus", "aus dem", "aus der", "im", "im dokument",
    "bezüglich", "basierend auf", "entsprechend", "laut", "über", "hinsichtlich",
    "einschließlich", "im bezug auf", "gemäß", "in bezug auf", "bericht", "dokument"
]
    for prep in preps:
        if prep in question_lower:
            idx = tokens.index(prep.split()[-1])
            return ' '.join(tokens[idx + 1:]).strip()
    return None

def query_router(user_id: str, question: str, history: list = None) -> str:
    try:
        lang = detect(question)
    except:
        lang = "de"

    doc_name = extract_doc_name_from_question(question)
    user_docs = get_available_documents(user_id)

    if not user_docs:
        return (
            "❌ Für diesen Benutzer wurden keine Dokumente gefunden."
            if lang == "de" else
            "❌ No documents found for this user."
        )

    if not doc_name:
        return (
            "❌ Bitte gib in deiner Frage an, auf welches Dokument du dich beziehst."
            if lang == "de" else
            "❌ Please specify the document you're referring to in your question."
        )

    doc_name_norm = normalize_doc_name(doc_name)
    matched_doc = None
    for d in user_docs:
        if normalize_doc_name(d) == doc_name_norm:
            matched_doc = d
            break

    if matched_doc is None:
        available = ", ".join(user_docs)
        return (
            f"📂 Dokument *{doc_name}* wurde nicht gefunden. Verfügbare Dokumente: {available}"
            if lang == "de" else
            f"📂 Document *{doc_name}* not found. Available documents: {available}"
        )

    doc_path = os.path.join(VECTOR_DIR, user_id, matched_doc)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    llm = OllamaLLM(model="llama3.2")  # You can change model if needed
    vectorstore = FAISS.load_local(doc_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=False)

    full_query = ""
    if history:
        for h in history:
            full_query += (
                f"Frage: {h['question']}\nAntwort: {h['answer']}\n"
                if lang == "de" else
                f"Question: {h['question']}\nAnswer: {h['answer']}\n"
            )

    full_query += (
        f"Frage: {question}\nAntworte in Deutsch."
        if lang == "de" else
        f"Question: {question}\nAnswer in English."
    )

    result = qa.invoke({"query": full_query})

    for key in ['result', 'output', 'answer']:
        if key in result:
            return f"📄 *{matched_doc}*: {result[key].strip()}"

    return f"📄 *{matched_doc}*: {next(iter(result.values())).strip()}"
