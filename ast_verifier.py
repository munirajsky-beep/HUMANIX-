import ast

def verify_code(code_str):
    """
    Parses code via AST for safety checks and executes it in a sandbox 
    to run unit tests (e.g., verifying 'reverse_string').
    """
    # 1. AST Syntax & Safety Check
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
        
    # Block dangerous modules/nodes if needed
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ["os", "sys", "subprocess", "shutil"]:
                    return False, f"Security Violation: Import of '{alias.name}' is forbidden."
        if isinstance(node, ast.ImportFrom):
            if node.module in ["os", "sys", "subprocess", "shutil"]:
                return False, f"Security Violation: Import from '{node.module}' is forbidden."

    # 2. Execution & Unit Testing Sandbox
    local_namespace = {}
    try:
        # Execute the generated code definition
        exec(code_str, {}, local_namespace)
        
        # Check if the requested function 'reverse_string' exists
        if 'reverse_string' not in local_namespace:
            return False, "NameError: name 'reverse_string' is not defined"
            
        # Run dynamic unit tests against the function
        func = local_namespace['reverse_string']
        
        # Test Case 1
        if func("hello") != "olleh":
            return False, "Logic Failure: reverse_string('hello') did not return 'olleh'"
            
        # Test Case 2
        if func("HumaniX") != "XinamuH":
            return False, "Logic Failure: reverse_string('HumaniX') did not return 'XinamuH'"
            
        return True, ""
        
    except Exception as e:
        safe_err = str(e).replace("'", "").replace('"', "")
        return False, f"Runtime/Logic Error: {safe_err}"