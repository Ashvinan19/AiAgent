# Example: Add a feature with surgical edits

**Prompt:**
```text
Add a power operator (** or ^) to the calculator. Update tests to cover 2 ** 3 = 8.
```

**Command:**
```bash
uv run main.py "Add a power operator to the calculator and add a unit test for 2 ** 3 = 8" \
  --working-dir ./calculator --require-success --verbose
```

## Expected tool flow

```
 - Calling function: get_project_tree
 - Calling function: get_file_content        # pkg/calculator.py
 - Calling function: get_file_content        # tests.py
 - Calling function: edit_file              # add ** operator to Calculator
 - Calling function: edit_file              # add test_power to tests.py
 - Calling function: run_command             # python -m unittest tests.py
 - Calling function: edit_file              # (only if tests fail)
 - Calling function: run_command             # re-verify
```

## What the agent should do

1. **Read before editing** — inspect `pkg/calculator.py` and `tests.py` for exact strings.
2. **Prefer `edit_file`** — patch only the operator dict and one new test method.
3. **Verify** — run unittest; with `--require-success`, the loop rejects a final answer until exit code 0.
4. **Optional** — `format_file` on changed `.py` files.

## Sample edit targets

In `pkg/calculator.py`, the agent might add to `self.operators`:

```python
"**": lambda a, b: a ** b,
```

In `tests.py`, a new test:

```python
def test_power(self) -> None:
    result = self.calculator.evaluate("2 ** 3")
    self.assertEqual(result, 8)
```

## Outcome

Minimal diff, tests green, final summary of what changed. This is the workflow the four-layer architecture is designed for.
