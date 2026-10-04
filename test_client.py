import requests

url = "https://humanix-1.onrender.com/verify"

payload = {
    "task": "Write a Python function named 'reverse_string' that accepts a string 's' and returns the reversed string.",
    "constraint": "Do not use standard library imports."
}

try:
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
except Exception as e:
    print("Error connecting to server:", e)