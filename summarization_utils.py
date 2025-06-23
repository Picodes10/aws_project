import os
import requests

def summarize_text_with_hf(text):
    api_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    if not api_token:
        return 'Hugging Face API token not set. Please set the HUGGINGFACEHUB_API_TOKEN environment variable.'
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {"inputs": text[:1024]}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return f"Hugging Face API error: {response.status_code} - {response.text}"
    result = response.json()
    if isinstance(result, dict) and result.get('error'):
        return f"Hugging Face API error: {result['error']}"
    return result[0]['summary_text'] if result and isinstance(result, list) and 'summary_text' in result[0] else 'No summary returned.' 