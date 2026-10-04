import json
import urllib.request
from sandbox_verifier import SandboxVerifier


def query_llm(prompt: str, model: str = "qwen2.5-coder:1.5b") -> str:
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4}
        }
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode())
            return result.get("response", "")
    except Exception as e:
        return f"# Error talking to model: {e}"


def clean_code(raw: str) -> str:
    text = raw.strip()
    if "```python" in text:
        text = text.split("```python", 1)[1]
    elif "```" in text:
        text = text.split("```", 1)[1]
    if "```" in text:
        text = text.split("```")[0]
    return text.strip()


def run_dual_engine(problem_description: str, function_signature: str, 
                    test_inputs: list, expected_outputs: list, max_anti_tries: int = 5):
    verifier = SandboxVerifier()

    print("=" * 60)
    print("HUMANIX DUAL ENGINE")
    print("=" * 60)
    print(f"Problem: {problem_description}")
    print(f"Function: {function_signature}")
    print("=" * 60)

    # ---------- HUMAN PATH ----------
    human_prompt = f"""Write a Python function {function_signature}.
{problem_description}
Use clear and normal human-style code.
Return ONLY the Python function code. No explanation."""

    print("\n--- Generating Human solution ---")
    human_raw = query_llm(human_prompt)
    human_code = clean_code(human_raw)
    print("Human code:")
    print(human_code)

    h_score, h_msg = verifier.check_code(
        human_code,
        mode="human",
        test_inputs=test_inputs,
        expected_outputs=expected_outputs
    )
    print(f"Human Score: {h_score} | {h_msg}")

    # ---------- ANTI-INTELLIGENCE PATH ----------
    anti_prompt = f"""Write a Python function {function_signature}.
{problem_description}

STRICT ANTI-INTELLIGENCE RULES:
- FORBIDDEN: the * operator
- FORBIDDEN: for loops
- FORBIDDEN: while loops
- You can only use addition and recursion

Here is an example of the STYLE you must follow (for multiplication):
def multiply(a, b):
    if b == 0:
        return 0
    return a + multiply(a, b - 1)

Now write the factorial function using the same style (only addition + recursion).
Return ONLY the pure Python function code."""

    print("\n--- Generating Anti-Intelligence solution (with retries) ---")
    
    a_score = 0.0
    a_msg = ""
    anti_code = ""

    for attempt in range(1, max_anti_tries + 1):
        print(f"  Attempt {attempt}/{max_anti_tries}...")
        anti_raw = query_llm(anti_prompt)
        anti_code = clean_code(anti_raw)
        
        a_score, a_msg = verifier.check_code(
            anti_code,
            mode="anti",
            test_inputs=test_inputs,
            expected_outputs=expected_outputs
        )
        
        print(f"  Score: {a_score} | {a_msg}")
        
        if a_score == 1.0:
            print("  Success! Valid Anti-Intelligence solution found.")
            break
        else:
            print("  Failed. Trying again...")

    print("\nFinal Anti code:")
    print(anti_code)
    print(f"Anti Score: {a_score} | {a_msg}")

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print(f"Human Intelligence : {h_score}")
    print(f"Anti-Intelligence  : {a_score}")
    print("=" * 60)


if __name__ == "__main__":
    run_dual_engine(
        problem_description="Calculate the factorial of a non-negative integer n. (Example: factorial(5) = 120)",
        function_signature="factorial(n)",
        test_inputs=[(0,), (1,), (5,), (6,)],
        expected_outputs=[1, 1, 120, 720],
        max_anti_tries=6
    )