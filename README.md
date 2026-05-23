# AI Coding Agent

A Python-based AI coding agent built with the Gemini API that can:

- List directories and files
- Read file contents
- Write and overwrite files
- Execute Python programs
- Iteratively debug code using an agent loop

## Features

- Gemini function calling
- Tool/function schemas using `google-genai`
- Secure working-directory sandboxing
- File system operations
- Python subprocess execution
- Multi-step agent loop
- Verbose debugging mode

## Project Structure

```text
aiagent/
├── calculator/
├── functions/
├── main.py
├── prompts.py
├── call_function.py
├── config.py
```

## Setup

### Clone Repo

```bash
git clone <repo-url>
cd aiagent
```

### Create Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

### Create `.env`

```env
GEMINI_API_KEY="your_api_key_here"
```

## Run the Agent

```bash
uv run main.py "Fix the bug in the calculator"
```

### Verbose Mode

```bash
uv run main.py "Explain how the calculator works" --verbose
```

## Example Capabilities

- Fix calculator bugs automatically
- Read and analyze project files
- Execute Python tests
- Modify source code
- Iterate using tool feedback loops

## Technologies Used

- Python
- Gemini API
- google-genai
- argparse
- subprocess
- uv


