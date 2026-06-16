"""Check for backslashes inside f-string expressions (Python 3.11 restriction)."""
import re
import sys

with open("app.py") as f:
    lines = f.readlines()

found = False
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    # Detect f-string start
    m = re.search(r"""f(['"])""", stripped)
    if m:
        quote = m.group(1)
        # Simple check: look for backslash before the closing quote/brace
        # Find all expressions { ... } in f-strings
        depth = 0
        expr_start = -1
        for j, c in enumerate(stripped):
            if c == '{' and stripped[j-1:j+1] != '{{':
                if depth == 0:
                    expr_start = j
                depth += 1
            elif c == '}' and stripped[j-1:j+1] != '}}':
                depth -= 1
                if depth == 0 and expr_start >= 0:
                    expr = stripped[expr_start + 1:j]
                    # Check for backslash in expression
                    if '\\' in expr:
                        print(f"Line {i+1}: Backslash in f-string expr: {expr[:100]}")
                        found = True
                    expr_start = -1
    i += 1

if not found:
    print("No backslashes found inside f-string expressions. Python 3.11 safe!")
    sys.exit(0)
else:
    print(f"\n{found} issue(s) found. Fix before deploying to Python 3.11.")
    sys.exit(1)
