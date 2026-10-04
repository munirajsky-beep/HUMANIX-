from human_engine import run_human_engine
from anti_engine import run_anti_engine
from ast_verifier import verify_constraints_and_logic, extract_code

def run_self_correcting_engine(engine_func, task_prompt, constraint_rule, engine_name):
    current_prompt = f"{task_prompt}\nCONSTRAINT: {constraint_rule}"
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        print(f"\n[{engine_name} - Attempt {attempt}/{max_retries}]")
        raw_response = engine_func(current_prompt)
        passed, msg = verify_constraints_and_logic(raw_response)
        
        if passed:
            print(msg)
            return extract_code(raw_response), 1.0
        else:
            print(f"Failed: {msg}")
            # Inject a strict structural template to override pre-trained habits
            current_prompt = (
                f"{task_prompt}\nCONSTRAINT: {constraint_rule}\n"
                f"PREVIOUS ATTEMPT FAILED WITH ERROR: {msg}.\n"
                "MANDATORY TEMPLATE: You must write code using this exact pattern to avoid '*':\n"
                "def multiply(a, b):\n"
                "    total = 0\n"
                "    for _ in range(b):\n"
                "        total += a\n"
                "    return total\n\n"
                "def factorial(n):\n"
                "    res = 1\n"
                "    for i in range(1, n + 1):\n"
                "        res = multiply(res, i)\n"
                "    return res\n"
                "Return ONLY valid Python code following this structure."
            )
            
    print(f"❌ {engine_name} exhausted all retries and failed.")
    return extract_code(raw_response), 0.0

def run_pipeline():
    task = "Write a Python function named 'factorial' to calculate the factorial of 5 without using multiplication."
    constraint = "Do NOT use the '*' or '*=' operators anywhere. The function must be named 'factorial' and return 120 for input 5."
    
    print("="*60)
    print(f"HUMANIX VICTORY PIPELINE (TEMPLATE FORCED)")
    print(f"TASK: {task}")
    print("="*60)
    
    print("\n--- RUNNING HUMAN ENGINE ---")
    h_code, h_score = run_self_correcting_engine(run_human_engine, task, constraint, "HUMAN ENGINE")
    print(f"\nFinal Human Code:\n{h_code}")
    
    print("\n" + "-"*60)
    
    print("\n--- RUNNING ANTI-INTELLIGENCE ENGINE ---")
    a_code, a_score = run_self_correcting_engine(run_anti_engine, task, constraint, "ANTI ENGINE")
    print(f"\nFinal Anti Code:\n{a_code}")
    
    print("\n" + "="*60)
    print(f"FINAL EVALUATION SCORES")
    print(f"Human Intelligence Score      : {h_score}")
    print(f"Anti-Intelligence Score : {a_score}")
    print("="*60)

if __name__ == "__main__":
    run_pipeline()
   