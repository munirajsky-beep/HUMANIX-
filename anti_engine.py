import os
import requests
import re

def clean_code_response(text):
    match = re.search(r'```[a-zA-Z]*\n?(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    lines = text.strip().split('\n')
    clean_lines = [line for line in lines if not line.strip().startswith('```')]
    return '\n'.join(clean_lines).strip()

def run_anti_engine(prompt):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
    
    system_prompt = (
        "You are a strict Python 3 code generator.\n"
        "RULES:\n"
        "1. Return ONLY pure executable Python code. Do not include markdown formatting, explanations, or comments.\n"
        "2. Examine the task description for the expected function name (e.g., 'reverse_string'). You MUST name your function exactly as requested in the task.\n"
        "3. Do NOT include example usage, print statements, or test runner code at the bottom. Return the function definition and nothing else.\n\n"
        f"TASK:\n{prompt}"
    )

    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        return clean_code_response(raw_text)
    except Exception as e:
        safe_error = str(e).replace("'", "").replace('"', "")
        return f"print('''Anti Engine Error: {safe_error}''')"