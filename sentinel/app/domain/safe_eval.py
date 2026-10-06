"""Sandboxed Safe Python Quick-Runner.

Safely evaluates lightweight Python expressions, datetime logic, token formulas,
and mathematical snippets directly from Telegram with AST-based security gates
and stdout redirection.
"""

import ast
import io
import sys
import math
import datetime
import json
import re
import random
from typing import Dict, Any, Tuple


DISALLOWED_MODULES = {
    "os", "sys", "subprocess", "socket", "requests", "httpx", "urllib",
    "shutil", "pathlib", "threading", "multiprocessing", "ctypes", "builtins"
}

DISALLOWED_CALLS = {
    "eval", "exec", "__import__", "open", "getattr", "setattr", "delattr",
    "compile", "globals", "locals", "input", "breakpoint"
}


class SecurityValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in DISALLOWED_MODULES:
                self.errors.append(f"Import of '{alias.name}' is prohibited for security.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in DISALLOWED_MODULES:
                self.errors.append(f"Import from '{node.module}' is prohibited for security.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in DISALLOWED_CALLS:
                self.errors.append(f"Call to '{node.func.id}()' is prohibited for security.")
        self.generic_visit(node)


class SafePythonRunner:
    def execute(self, code_str: str) -> str:
        """Executes sandboxed Python snippet and captures output."""
        clean = code_str.strip()
        if not clean:
            return (
                "🐍 **Sandboxed Python Quick-Runner**\n\n"
                "Execute safe Python snippets, formulas, or datetime calculations directly:\n"
                "Usage: `/run_py <python code or formula>`\n\n"
                "Examples:\n"
                "• `/run_py 5000 * (1200 * 0.15 + 400 * 0.60) / 1000000 * 30`\n"
                "• `/run_py import math; print([math.ceil(x/8) * 8 for x in [13, 27, 45]])`\n"
                "• `/run_py from datetime import datetime, timedelta; print((datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'))`"
            )

        # 1. AST Security Inspection
        try:
            tree = ast.parse(clean)
            validator = SecurityValidator()
            validator.visit(tree)
            if validator.errors:
                return f"🛑 **Execution Blocked**: {validator.errors[0]}"
        except SyntaxError as e:
            return f"❌ **Syntax Error**: {str(e)}"

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            base_mod = name.split(".")[0]
            if base_mod in DISALLOWED_MODULES:
                raise ImportError(f"Import of '{name}' is prohibited for security.")
            return __import__(name, globals, locals, fromlist, level)

        safe_builtins = {
            "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
            "chr": chr, "dict": dict, "divmod": divmod, "enumerate": enumerate,
            "float": float, "format": format, "hex": hex, "int": int,
            "isinstance": isinstance, "len": len, "list": list, "map": map,
            "max": max, "min": min, "oct": oct, "ord": ord, "pow": pow,
            "range": range, "reversed": reversed, "round": round, "set": set,
            "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
            "type": type, "zip": zip, "print": print,
            "__import__": safe_import,
        }

        safe_globals = {
            "__builtins__": safe_builtins,
            "math": math,
            "datetime": datetime,
            "json": json,
            "re": re,
            "random": random,
        }

        # 3. Capture standard output
        captured_out = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_out

        result_val = None
        try:
            # Check if it's a single expression or multi-statement code
            if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
                # Evaluate expression
                compiled = compile(clean, "<sandbox>", "eval")
                result_val = eval(compiled, safe_globals, safe_globals)
            else:
                compiled = compile(clean, "<sandbox>", "exec")
                exec(compiled, safe_globals, safe_globals)
        except Exception as e:
            return f"⚠️ **Runtime Error**: {type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout

        out_text = captured_out.getvalue().strip()
        lines = ["🐍 **Python Sandbox Execution Result**\n"]

        if out_text:
            lines.append(f"**Output (stdout)**:\n```\n{out_text}\n```")
        if result_val is not None:
            lines.append(f"**Evaluated Result**:\n`{repr(result_val)}`")

        if not out_text and result_val is None:
            lines.append("✅ Code executed successfully (no stdout or return value).")

        return "\n".join(lines)
