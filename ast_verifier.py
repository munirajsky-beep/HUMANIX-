import ast

FORBIDDEN_NODE_MAP = {
    ast.Import: "Imports are restricted for security reasons.",
    ast.ImportFrom: "ImportFrom is restricted for security reasons.",
    ast.Exec: "Exec is not allowed.",
    ast.Eval: "Eval is not allowed."
}

def verify_constraints_and_logic(code_str):
    """
    Verifies code constraints via AST parsing and executes dynamic unit tests.
    Returns (is_valid, error_message).
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
        
    for node in ast.walk(tree):
        for node_type, msg in FORBIDDEN_NODE_MAP.items():
            if isinstance(node, node_type):
                return False, f"Security Violation: {msg}"
                
    local_namespace = {}
    try:
        exec(code_str, {}, local_namespace)
        
        if 'reverse_string' not in local_namespace:
            return False, "NameError: name 'reverse_string' is not defined"
            
        func = local_namespace['reverse_string']
        if func("hello") != "olleh":
            return False, "Logic Failure: reverse_string('hello') did not return 'olleh'"
        if func("HumaniX") != "XinamuH":
            return False, "Logic Failure: reverse_string('HumaniX') did not return 'XinamuH'"
            
        return True, ""
    except Exception as e:
        safe_err = str(e).replace("'", "").replace('"', "")
        return False, f"Runtime/Logic Error: {safe_err}"

def verify_code(code_str):
    """Alias for orchestrator compatibility"""
    return verify_constraints_and_logic(code_str)