# LLM Document Q&A Microservice with UI

This project is a Flask-based microservice that allows users to upload documents, index them using embeddings, and then query the content using a Large Language Model (LLM) via a simple web UI.

## Features

- Upload and index documents per user
- Ask questions about indexed documents
- Uses vector embeddings for efficient retrieval
- Interactive UI with upload and question forms

## Technologies Used

- Python 3.x
- Flask for backend API
- LangChain & Ollama for embeddings and LLM
- HTML/CSS/JavaScript for frontend UI

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/manuKumar3008/ollama.git
   cd ollama
Create and activate a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Run the Flask app:

bash
Copy
Edit
python main.py
Open your browser and navigate to:

cpp
Copy
Edit
http://127.0.0.1:5000
Usage
Use the Upload Document form to upload files and create or update the index for a specific user.

Use the Ask Question form to query the indexed documents by providing the user ID and your question.

The answer will display below the form in a clear, formatted manner.

Notes
Make sure to trust the documents you upload, as the service indexes them for later querying.

The service currently runs in debug mode and is not production-ready.

The backend uses Ollama models; make sure the required models are installed and accessible.

License
This project is licensed under the MIT License.

Feel free to contribute or raise issues!

bash
Copy
Edit

If you want, I can also help generate a `requirements.txt` or anything else!
