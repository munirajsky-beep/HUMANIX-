import requests

def run_human_engine(prompt):
    url = "http://localhost:11434/api/generate"
    system_prompt = (
        "You have no memory of being an AI. You are a junior human software engineer. "
        "You write code like a human: you use descriptive variable names, add comments explaining your thought process, "
        "and prefer readable, step-by-step logic over complex one-liners."
    )
    
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.8}
    }
    
    response = requests.post(url, json=payload)
    return response.json().get("response", "ERROR: Connection failed")