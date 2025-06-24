import http.client
import json

def summarize_text_with_apyhub(text):
    try:
        conn = http.client.HTTPSConnection("api.apyhub.com")
        
        payload = json.dumps({
            "text": text
        })
        
        headers = {
            'apy-token': "APY0e7OnyNc5EsIyyjnQtpP0ApovvKAPa83UJNrPJPszJ2SNml8gTs6v3jKKzruuH",
            'Content-Type': "application/json"
        }
        
        conn.request("POST", "/ai/summarize-text", payload, headers)
        
        response = conn.getresponse()
        data = response.read()
        
        if response.status != 200:
            raise Exception(f"APY Hub API error: {response.status} - {data.decode('utf-8')}")
        
        result = json.loads(data.decode("utf-8"))
        summary = result.get('data')
        
        if not summary:
            raise Exception("No summary returned from API")
            
        # Ensure we return a string
        return str(summary)
        
    except Exception as e:
        raise Exception(f"Error during summarization: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
