from flask import Flask, request, jsonify, render_template
from services.indexer import index_document
from services.query_engine import ask_question
import os

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/index", methods=["POST"])
def upload_and_index():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    try:
        index_document(filepath)
        return jsonify({"message": "Document indexed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_question(question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
