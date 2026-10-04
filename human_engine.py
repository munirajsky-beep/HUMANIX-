import os
import requests
import re

def clean_code_response(text):
    # Extract code if it is hidden inside any variation of markdown backticks
    match = re.search(r'```[a-zA-Z]*\n?(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback: remove any stray backticks manually
    lines = text.strip().split('\n')
    clean_lines = [line for line in lines if not line.strip().startswith('```')]
    return '\n'.join(clean_lines).strip()

def run_human_engine(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    system_prompt = "You are a code generation engine. Return strictly valid Python 3 code. No markdown, no explanations, no conversational text.\n\n" + prompt

    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return clean_code_response(raw_text)
    except Exception as e:
        # If it fails, return valid python so the AST validator doesn't crash
        return f"print('Human Engine API Error: {str(e)} | Raw Data: {data}')"