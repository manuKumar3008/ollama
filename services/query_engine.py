from langchain_community.vectorstores.faiss import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA

def query_document(user_id: str, question: str) -> str:
    vectorstore_dir = f'vectorstore/{user_id}'
    embeddings = OllamaEmbeddings(model="llama3.2")

    # Load FAISS vectorstore
    vectorstore = FAISS.load_local(vectorstore_dir, embeddings=embeddings, allow_dangerous_deserialization=True)

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    qa = RetrievalQA.from_chain_type(llm=OllamaLLM(model="llama3.2"), retriever=retriever)

    # Use invoke (not run) per new LangChain version
    answer = qa.invoke(question)
    return answer
