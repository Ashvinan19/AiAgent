import subprocess


def format_process_output(result: subprocess.CompletedProcess[str], label: str = "") -> str:
    output: list[str] = []

    if label:
        output.append(label)

    if result.returncode != 0:
        output.append(f"Process exited with code {result.returncode}")

    if result.stdout:
        output.append(f"STDOUT:\n{result.stdout}")

    if result.stderr:
        output.append(f"STDERR:\n{result.stderr}")

    if not result.stdout and not result.stderr:
        output.append("No output produced")

    return "\n".join(output)


def run_in_sandbox(
    command: list[str],
    working_directory: str,
    timeout: int = 60,
) -> tuple[subprocess.CompletedProcess[str] | None, str | None]:
    try:
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result, None
    except subprocess.TimeoutExpired:
        return None, f"Error: Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return None, f"Error: Command not found: {command[0]}"
    except Exception as e:
        return None, f"Error: {e}"
