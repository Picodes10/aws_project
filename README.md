# Smart Accessibility Reader

A web application that helps users extract text from images, summarize content, and provides accessibility features.

## Features

- 📄 **Image Upload**: Upload images (PNG, JPG, JPEG)
- 🔍 **Text Extraction**: Extract text from images using OCR
- 📝 **Text Summarization**: Generate summaries of extracted text
- 🔊 **Text-to-Speech**: Listen to extracted text and summaries
- ❓ **Q&A**: (Coming soon) Ask questions about the content

## Setup

### Prerequisites

1. **Python 3.7+**
2. **Tesseract OCR**: Required for text extraction
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask backend**:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the React development server**:
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Upload an image containing text
3. Click "Extract Text" to extract text from the image
4. Click "Summarize" to generate a summary of the extracted text
5. Click "Listen to Text" to hear the extracted text
6. Click "Listen to Summary" to hear the summarized text

## API Endpoints

- `POST /api/upload` - Upload an image file
- `POST /api/extract` - Extract text from uploaded image
- `POST /api/summarize` - Summarize extracted text
- `POST /api/synthesize` - Convert text to speech (returns audio file)

## AWS Integration

The application includes AWS S3 integration for file storage. To use AWS features:

1. Configure AWS credentials via environment variables or AWS CLI
2. Update the S3 bucket name in `aws_utils.py` if needed

## Troubleshooting

- **"Tesseract not found" error**: Make sure Tesseract OCR is installed and in your system PATH
- **CORS errors**: The backend includes CORS support, but ensure both frontend and backend are running
- **File upload issues**: Check that the `uploads/` directory exists and has write permissions 