# app.py

import streamlit as st
from aws_utils import upload_to_s3, bucket_name
from textract_lambda import extract_text_from_s3
from summarization_utils import summarize_text_with_hf
# For future integration: from textract_lambda import lambda_handler

# App title and header
st.set_page_config(page_title="Smart Accessibility Reader", layout="centered")
st.title("📖 Smart Accessibility Reader")
st.markdown("Help visually impaired users access and understand text content easily.")

# Initialize session state to hold data across reruns
if 'filename' not in st.session_state:
    st.session_state.filename = None
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None

# Upload Section
st.header("📄 Upload Document (Image)")
uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"], key="file_uploader")

# Only upload and reset extracted text if a new file is selected
if uploaded_file is not None and (
    'last_uploaded_filename' not in st.session_state or uploaded_file.name != st.session_state['last_uploaded_filename']
):
    with st.spinner("Uploading to S3..."):
        st.session_state.filename = upload_to_s3(uploaded_file, filename=None)
        st.session_state.extracted_text = None
        st.session_state['last_uploaded_filename'] = uploaded_file.name
    st.success(f"Uploaded to S3 as: {st.session_state.filename}")

# Debug: Show extracted text in the app
st.write("DEBUG: Extracted text:", st.session_state.extracted_text)

# Debug: Extracted text in session state
st.write("DEBUG: Extracted text in session state:", st.session_state.get('extracted_text'))

# Action Buttons
st.header("🧠 Actions")
col1, col2, col3 = st.columns(3)

with col1:
    extract_btn = st.button("🔍 Extract Text")
with col2:
    summarize_btn = st.button("📝 Summarize")
with col3:
    listen_btn = st.button("🔊 Listen")

# Optional: Question-Answer Section
st.header("❓ Ask a Question About the Document")
user_question = st.text_input("Type your question here...")

qa_btn = st.button("💬 Get Answer")

# Placeholder Sections for Outputs
st.markdown("---")

st.subheader("📄 Extracted Text")
extracted_text_placeholder = st.empty()

st.subheader("✍️ Summary")
summary_placeholder = st.empty()

st.subheader("🔈 Audio Output")
audio_placeholder = st.empty()

st.subheader("💡 Q&A Response")
qa_placeholder = st.empty()

# --- Action Logic ---
# Extract Text from S3 using Lambda
if extract_btn and st.session_state.filename:
    with st.spinner("Extracting text from document..."):
        st.session_state.extracted_text = extract_text_from_s3(bucket_name, st.session_state.filename)

# Summarize with Hugging Face
if summarize_btn:
    if st.session_state.extracted_text:
        with st.spinner("Generating summary with Hugging Face..."):
            API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
            payload = {"inputs": st.session_state.extracted_text[:500]}
            summary = summarize_text_with_hf(st.session_state.extracted_text)
            summary_placeholder.markdown(summary)
    else:
        st.warning("Please extract text from the document first.")

# Display extracted text if it exists in session state
if st.session_state.extracted_text:
    extracted_text_placeholder.text_area("Extracted Text", st.session_state.extracted_text, height=300)

# Dummy responses for other buttons
if listen_btn:
    audio_placeholder.audio("https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav")  # Sample

if qa_btn and user_question:
    qa_placeholder.markdown(f"**Q:** {user_question}\n\n**A:** This is a placeholder answer.")

