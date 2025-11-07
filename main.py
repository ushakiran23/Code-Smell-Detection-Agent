from fastapi import FastAPI, File, UploadFile, HTTPException
import ast

# Initialize FastAPI app
app = FastAPI(
    title="Code Smell Detection Agent",
    description="An agent that analyzes Python code for inefficiencies using AST parsing.",
    version="1.0"
)

# 🏠 Home Route
@app.get("/")
def home():
    return {"message": "✅ Code Smell Detection Agent is running successfully!"}

# --- Helper Functions for Code Smell Detection ---

def detect_long_functions(tree, max_length=30):
    """Detect functions that are too long."""
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start)
            length = end - start
            if length > max_length:
                issues.append({
                    "type": "Long Function",
                    "function": node.name,
                    "lines": f"{start}-{end}",
                    "suggestion": "Split this function into smaller ones."
                })
    return issues


def detect_deep_nesting(tree, max_depth=3):
    """Detect deeply nested logic inside functions."""
    issues = []

    def get_depth(node, level=0):
        depth = level
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.FunctionDef)):
                depth = max(depth, get_depth(child, level + 1))
        return depth

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            depth = get_depth(node)
            if depth > max_depth:
                issues.append({
                    "type": "Deep Nesting",
                    "function": node.name,
                    "depth": depth,
                    "suggestion": "Simplify nested logic."
                })
    return issues


def detect_unused_imports_and_vars(tree):
    """Detect unused imports and variables."""
    issues = []
    imported = set()
    used = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.Name):
            used.add(node.id)

    unused = imported - used
    for u in unused:
        issues.append({
            "type": "Unused Import",
            "name": u,
            "suggestion": f"Remove unused import '{u}'."
        })
    return issues


# 🚀 Main Endpoint to Analyze Uploaded Python Files
@app.post("/analyze")
async def analyze_code(file: UploadFile = File(...)):
    """Analyze uploaded Python (.py) file for code smells."""
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Please upload a valid .py file")

    content = await file.read()
    try:
        # Parse file using AST
        tree = ast.parse(content.decode())

        # Run all checks
        issues = []
        issues.extend(detect_long_functions(tree))
        issues.extend(detect_deep_nesting(tree))
        issues.extend(detect_unused_imports_and_vars(tree))

        # Return result
        if not issues:
            return {"report": "✅ No code smells detected! Your code looks clean."}
        return {"report": issues}

    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Syntax error in uploaded code: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {e}")
