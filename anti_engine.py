import os
import requests

def clean_code_response(text):
    if "```python" in text:
        text = text.split("```python")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()

def run_anti_engine(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    system_prompt = "Return ONLY valid, executable Python code. Do NOT include markdown code blocks, backticks, or any introductory or trailing explanations.\n\nTask:\n" + prompt

    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return clean_code_response(raw_text)
    except (KeyError, IndexError):
        return f"Anti Engine Error: {data}"