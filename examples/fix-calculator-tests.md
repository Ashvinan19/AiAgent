# Example: Run and verify calculator tests

**Prompt:**
```text
Run the calculator unit tests and report whether they pass.
```

**Command:**
```bash
uv run main.py "Run the calculator unit tests and report whether they pass." \
  --working-dir ./calculator --verbose
```

## Expected tool flow

```
 - Calling function: get_project_tree
 - Calling function: get_file_content        # tests.py
 - Calling function: run_command           # python -m unittest tests.py
```

## Sample verbose output

```
Working directory: C:\...\AiAgent\calculator
 - Calling function: get_project_tree
-> Project tree (max_depth=6):
main.py (754 bytes)
pkg/
  calculator.py (2021 bytes)
  render.py (390 bytes)
tests.py (1483 bytes)
...
 - Calling function: run_command({'command': 'python -m unittest tests.py'})
-> STDOUT:
...........
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

## Outcome

The agent maps the sandbox, locates `tests.py`, runs unittest, and reports **10 tests passed** without modifying any files.

Use `--require-success` if you want the loop to block the final answer until a command exits 0 *after* the agent has made code changes.
