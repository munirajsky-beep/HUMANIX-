import requests

url = "http://127.0.0.1:8000/verify"

headers = {
    "X-API-Key": "humanix-enterprise-secret-key-2026",
    "Content-Type": "application/json"
}

payload = {
    "task": "Write a python function named reverse_string that reverses a given word.",
    "constraint": "Do not use for-loops or while-loops. Use recursion or python slicing.",
    "blocked_nodes": ["FOR_LOOPS", "WHILE_LOOPS"],
    "test_assertion": "assert reverse_string('hello') == 'olleh', 'String was not reversed correctly'"
}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response Body:", response.json())