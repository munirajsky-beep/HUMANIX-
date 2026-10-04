import requests

def run_anti_engine(prompt):
    url = "http://localhost:11434/api/generate"
    system_prompt = (
        "You are an Anti-Intelligence execution protocol. You are devoid of human traits. "
        "Output ONLY raw, executable code. Zero comments. Zero explanations. "
        "Use the shortest possible syntax, recursive logic where applicable, and single-letter variables."
    )
    
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    response = requests.post(url, json=payload)
    return response.json().get("response", "ERROR: Connection failed")