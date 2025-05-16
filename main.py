from flask import Flask, request, jsonify, render_template
import os

from services.indexer import index_document
from services.query_engine import query_document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def index():
    user_id = request.form['user_id']
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    file_path = os.path.join(user_folder, file.filename)
    file.save(file_path)

    # Index document
    try:
        index_document(user_id, file_path)
        return jsonify({'message': 'File indexed successfully.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_id = request.form['user_id']
        question = request.form['question']
        answer = query_document(user_id, question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
