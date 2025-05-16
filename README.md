Document Q&A Microservice
This is a Flask-based microservice that allows users to upload documents, index their contents using embeddings, and ask questions to get answers based on the indexed documents. It uses LangChain and Ollama LLM for retrieval-augmented question answering.

Features
Upload and index documents (supports PDF and text files)

Ask natural language questions related to uploaded documents

Uses FAISS for vector storage and similarity search

Uses Ollama LLM for answering questions based on retrieved document chunks

Simple web UI with separate HTML template

Requirements
Python 3.8+

Flask

LangChain and langchain_community modules

Ollama LLM (configured and running)

FAISS

Installation
Clone the repository

bash
Copy
Edit
git clone <repo-url>
cd llm_microservice
Create and activate a virtual environment (optional but recommended)

bash
Copy
Edit
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Ensure Ollama LLM is installed and running locally

Usage
Run the Flask app

bash
Copy
Edit
python main.py
Open your browser at http://localhost:5000

Upload your document (PDF or TXT)

Ask questions related to the uploaded document and get answers

Project Structure
bash
Copy
Edit
llm_microservice/
│
├── main.py                  # Flask app entry point
├── templates/
│   └── index.html           # Frontend HTML UI
├── services/
│   ├── indexer.py           # Document indexing logic
│   └── query_engine.py      # Question answering logic
├── uploads/                 # Uploaded documents storage
└── vectorstore/             # Stored vector indexes
Notes
Uploaded documents are stored in /uploads

Indexed vectors are saved under /vectorstore

Currently supports PDF and text files; you can extend loaders for other formats

Ollama LLM must be configured separately

Troubleshooting
If indexing fails due to encoding issues, ensure documents are valid PDFs or text files.

Make sure Ollama LLM is running and accessible.

Check Flask console logs for errors.

License
MIT License
