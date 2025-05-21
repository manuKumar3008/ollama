from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from collections import defaultdict
from services.indexer import index_documents, list_user_documents
from services.query_engine import query_router

app = Flask(__name__)
UPLOADS = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS, exist_ok=True)
chat_history = defaultdict(list)

@app.route("/", methods=["GET"])
def index():
    user_id = request.args.get("user", "default")
    return render_template("index.html", user_id=user_id)

@app.route("/upload", methods=["POST"])
def upload():
    user_id = request.form.get("user_id", "default")
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    safe_name = secure_filename(file.filename)
    user_dir = os.path.join(UPLOADS, user_id)
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, safe_name)
    file.save(file_path)
    doc_name = os.path.splitext(safe_name)[0]
    index_documents(user_id, doc_name, file_path)
    return jsonify({"message": f"Document '{safe_name}' indexed successfully."})

@app.route("/ask", methods=["POST"])
def ask():
    user_id = request.form.get("user_id", "default")
    question = request.form.get("question")
    if not question:
        return jsonify({"answer": "Please provide a question."}), 400
    try:
        previous_messages = chat_history[user_id]
        answer = query_router(user_id, question, history=previous_messages)
        chat_history[user_id].append({"question": question, "answer": answer})
        return jsonify({"answer": answer, "history": chat_history[user_id]})
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"answer": "Error processing your question."}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
