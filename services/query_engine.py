from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from services.indexer import get_index

def ask_question(question: str) -> str:
    index = get_index()
    if index is None:
        return "No documents indexed yet. Please upload documents first."

    retriever = index.as_retriever(search_kwargs={"k": 3})
    llm = OllamaLLM(model="llama3.2")

    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return qa.run(question)
