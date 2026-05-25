# Example: Explain the codebase (no tools needed)

**Prompt:**
```text
What is a Python decorator?
```

**Command:**
```bash
uv run main.py "What is a Python decorator?"
```

## Expected behavior

The system prompt instructs the model to answer general programming questions **directly** without calling tools. The agent should respond with an explanation immediately — no `get_project_tree`, no `grep_files`.

## Sample final response (abbreviated)

```
Final response:
A Python decorator is a function that takes another function (or class) and
extends or modifies its behavior without changing its source code. You apply
it with @decorator_name above the function definition...
```

## Why this matters

Earlier versions of the prompt forced tool use on every question. The updated `prompts.py` separates:

- **Q&A** → answer directly
- **Code tasks** → map → read → edit → verify

This prevents `--require-success` from blocking innocent questions (the flag only activates after a modifying tool has been called).
