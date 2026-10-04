import ast

class DualASTChecker(ast.NodeVisitor):
    def __init__(self, mode="human"):
        self.mode = mode
        self.violations = []

    def visit_For(self, node):
        if self.mode == "anti":
            self.violations.append("Banned: for-loop")
        self.generic_visit(node)

    def visit_While(self, node):
        if self.mode == "anti":
            self.violations.append("Banned: while-loop")
        self.generic_visit(node)

    def visit_Mult(self, node):
        if self.mode == "anti":
            self.violations.append("Banned: * operator")
        self.generic_visit(node)


class SandboxVerifier:
    def __init__(self):
        pass

    def check_code(self, code_str: str, mode="human", test_inputs=None, expected_outputs=None) -> tuple[float, str]:
        try:
            tree = ast.parse(code_str)

            checker = DualASTChecker(mode=mode)
            checker.visit(tree)

            if checker.violations:
                return 0.0, f"AST Violation: {', '.join(checker.violations)}"

            # Create a proper scope so recursion works
            local_scope = {}
            exec(code_str, local_scope, local_scope)   # Important: same dict for globals and locals

            target_func = None
            for name, obj in local_scope.items():
                if callable(obj) and not isinstance(obj, type):
                    target_func = obj
                    break

            if target_func is None:
                return 0.0, "No function found"

            if test_inputs is None or expected_outputs is None:
                return 1.0, "Code ran successfully (no tests)"

            passed = 0
            total = len(test_inputs)
            details = []

            for inp, expected in zip(test_inputs, expected_outputs):
                try:
                    if isinstance(inp, (list, tuple)):
                        result = target_func(*inp)
                    else:
                        result = target_func(inp)

                    if result == expected:
                        passed += 1
                        details.append(f"{inp} → {result} (correct)")
                    else:
                        details.append(f"{inp} → {result} (expected {expected})")
                except Exception as e:
                    details.append(f"{inp} → Error: {e}")

            score = passed / total
            return score, f"Passed {passed}/{total} | Details: {details}"

        except Exception as e:
            return 0.0, f"Failed: {str(e)}"


if __name__ == "__main__":
    verifier = SandboxVerifier()

    test_inputs = [(3, 4), (5, 5), (2, 8)]
    expected_outputs = [12, 25, 16]

    print("=== HUMAN MODE ===")
    human_code = """
def multiply(a, b):
    return a * b
"""
    score, msg = verifier.check_code(human_code, mode="human", test_inputs=test_inputs, expected_outputs=expected_outputs)
    print(score, "|", msg)

    print("\n=== ANTI MODE ===")
    anti_code = """
def multiply(a, b):
    if b == 0:
        return 0
    if b == 1:
        return a
    if b % 2 == 0:
        return multiply(a << 1, b // 2)
    return a + multiply(a, b - 1)
"""
    score, msg = verifier.check_code(anti_code, mode="anti", test_inputs=test_inputs, expected_outputs=expected_outputs)
    print(score, "|", msg)