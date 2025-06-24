from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import boto3

from aws_utils import upload_to_s3, bucket_name
from textract_lambda import extract_text_from_s3
from summarization_utils import summarize_text_with_apyhub  # Updated import

app = Flask(__name__)
CORS(app)

# Test route to verify API is working
@app.route('/')
def home():
    return jsonify({'message': 'API is running'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        filename = upload_to_s3(file)
        return jsonify({'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract', methods=['POST'])
def extract_text():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    try:
        extracted_text = extract_text_from_s3(bucket_name, filename)
        return jsonify({'text': extracted_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        summary = summarize_text_with_apyhub(text)  # Updated function call
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/synthesize', methods=['POST'])
def synthesize_speech():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'Joanna')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        audio_data = text_to_speech(text, voice)
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


polly = boto3.client("polly")

def text_to_speech(summary_text, voice="Joanna"):
    response = polly.synthesize_speech(
        Text=summary_text,
        OutputFormat="mp3",
        VoiceId=voice
    )
    return response["AudioStream"].read()
