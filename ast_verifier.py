import ast
import re
import subprocess
import tempfile
import os

FORBIDDEN_NODE_MAP = {
    "FOR_LOOPS": (ast.For, "For loop 'for ... in ...' detected"),
    "WHILE_LOOPS": (ast.While, "While loop 'while ...' detected"),
    "IMPORTS": ((ast.Import, ast.ImportFrom), "Module import statement detected"),
    "ADDITION": (ast.Add, "Addition operator '+' detected"),
    "MULTIPLICATION": (ast.Mult, "Multiplication operator '*' detected"),
    "SUBTRACTION": (ast.Sub, "Subtraction operator '-' detected"),
    "DIVISION": (ast.Div, "Division operator '/' detected"),
    "RECURSION": ("RECURSION_CHECK", "Recursive function call detected")
}

def extract_code(response_text):
    match = re.search(r'```python(.*?)```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()

def verify_constraints_and_logic(ai_response, forbidden_keys=None, test_assertion=None):
    raw_code = extract_code(ai_response)
    
    # 1. AST Syntax Analysis
    try:
        tree = ast.parse(raw_code)
    except SyntaxError:
        return False, "❌ SYNTAX ERROR: Code is not valid Python syntax."

    if forbidden_keys is None:
        forbidden_keys = []

    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

    for node in ast.walk(tree):
        for key in forbidden_keys:
            if key in FORBIDDEN_NODE_MAP:
                target, err_msg = FORBIDDEN_NODE_MAP[key]
                
                if key == "RECURSION" and isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in func_names:
                        return False, f"❌ CONSTRAINT FAILED: {err_msg}."
                elif target != "RECURSION_CHECK":
                    if isinstance(node, target):
                        return False, f"❌ CONSTRAINT FAILED: {err_msg}."
                    if hasattr(node, 'op') and isinstance(node.op, target):
                        return False, f"❌ CONSTRAINT FAILED: {err_msg}."

    # 2. Secure Subprocess Execution Sandbox (2-Second Timeout)
    exec_script = raw_code
    if test_assertion:
        exec_script += f"\n\n{test_assertion}"

    # Write the code to a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".py")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(exec_script)

    try:
        # Run the temp file in a completely isolated process
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=2.0  # Kill the AI code if it hangs
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip().split('\n')[-1]
            return False, f"❌ LOGIC / RUNTIME FAILURE: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return False, "❌ TIMEOUT: AI code exceeded 2-second execution limit (possible infinite loop)."
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return True, "✅ VERDICT: PASSED ALL AST CONSTRAINTS & SECURE SANDBOX TESTS."