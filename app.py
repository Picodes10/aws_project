import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import re
from gtts import gTTS
import uuid
import pyttsx3
import tempfile

UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def simple_summarize(text, num_sentences=3):
    # Split text into sentences and return the first num_sentences
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    summary = ' '.join(sentences[:num_sentences])
    return summary if summary else 'No summary could be generated.'

def generate_speech_pyttsx3(text, audio_path):
    """Generate speech using pyttsx3 (offline TTS)"""
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"pyttsx3 error: {str(e)}")
        return False

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/extract', methods=['POST'])
def extract():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Error processing image: {e}'}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    summary = simple_summarize(text)
    return jsonify({'summary': summary})

@app.route('/api/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Generate a unique filename for the audio
        audio_filename = f"speech_{uuid.uuid4().hex}.mp3"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        print(f"Generating speech for text: {text[:50]}...")  # Debug log
        print(f"Audio will be saved to: {audio_path}")  # Debug log
        
        # Try gTTS first
        try:
            # Convert text to speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(audio_path)
            print(f"gTTS audio file generated successfully: {audio_path}")  # Debug log
        except Exception as gtts_error:
            print(f"gTTS failed: {str(gtts_error)}")  # Debug log
            # Try pyttsx3 as fallback
            print("Trying pyttsx3 fallback...")  # Debug log
            if generate_speech_pyttsx3(text, audio_path):
                print(f"pyttsx3 audio file generated successfully: {audio_path}")  # Debug log
            else:
                return jsonify({'error': f'Text-to-speech service unavailable: {str(gtts_error)}'}), 503
        
        # Check if file exists and has content
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file was not created'}), 500
        
        file_size = os.path.getsize(audio_path)
        print(f"Audio file size: {file_size} bytes")  # Debug log
        
        if file_size == 0:
            return jsonify({'error': 'Audio file is empty'}), 500
        
        # Return the audio file
        return send_from_directory(
            app.config['AUDIO_FOLDER'], 
            audio_filename, 
            as_attachment=True,
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        print(f"Error in synthesize: {str(e)}")  # Debug log
        return jsonify({'error': f'Error generating speech: {str(e)}'}), 500

@app.route('/api/test-audio')
def test_audio():
    """Test endpoint to verify audio generation works"""
    try:
        test_text = "Hello, this is a test of the text to speech functionality."
        audio_filename = "test_speech.mp3"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        # Generate test audio
        tts = gTTS(text=test_text, lang='en', slow=False)
        tts.save(audio_path)
        
        return jsonify({
            'message': 'Test audio generated successfully',
            'filename': audio_filename,
            'text': test_text
        })
    except Exception as e:
        return jsonify({'error': f'Test failed: {str(e)}'}), 500

@app.route('/')
def index():
    return jsonify({
        'message': 'Smart Accessibility Reader API',
        'endpoints': {
            'upload': '/api/upload (POST)',
            'extract': '/api/extract (POST)',
            'summarize': '/api/summarize (POST)',
            'synthesize': '/api/synthesize (POST)'
        }
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/audio/<filename>')
def audio_file(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
