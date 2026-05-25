from collections.abc import Iterator
from dataclasses import dataclass, field
import re

from google import genai
from google.genai import types

from call_function import available_functions, call_function
from config import DEFAULT_MAX_ITERATIONS
from prompts import system_prompt

EXECUTION_TOOLS = {"run_python_file", "run_command"}
MODIFYING_TOOLS = {
    "write_file",
    "edit_file",
    "format_file",
    "run_python_file",
    "run_command",
    "install_dependencies",
}


@dataclass
class AgentConfig:
    working_directory: str
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    verbose: bool = False
    require_success: bool = False
    model: str = "gemini-2.5-flash"


@dataclass
class AgentSession:
    messages: list[types.Content] = field(default_factory=list)
    last_exit_code: int | None = None
    iteration: int = 0
    modified_project: bool = False
    verified_after_change: bool = False


@dataclass
class AgentEvent:
    kind: str
    data: dict


def _parse_exit_code(result: str) -> int:
    match = re.search(r"Process exited with code (\d+)", result)
    if match:
        return int(match.group(1))
    if result.startswith("Error:"):
        return 1
    return 0


def run_agent(
    client: genai.Client,
    user_prompt: str,
    config: AgentConfig,
) -> Iterator[AgentEvent]:
    session = AgentSession(
        messages=[
            types.Content(
                role="user",
                parts=[types.Part(text=user_prompt)],
            )
        ]
    )

    for iteration in range(config.max_iterations):
        session.iteration = iteration + 1

        try:
            response = client.models.generate_content(
                model=config.model,
                contents=session.messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt,
                    temperature=0,
                ),
            )
        except Exception as e:
            yield AgentEvent("error", {"message": str(e)})
            return

        if response.usage_metadata and config.verbose:
            yield AgentEvent(
                "usage",
                {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "response_tokens": response.usage_metadata.candidates_token_count,
                },
            )

        if response.candidates:
            for candidate in response.candidates:
                if candidate.content is not None:
                    session.messages.append(candidate.content)

        if response.function_calls:
            function_responses = []

            for function_call in response.function_calls:
                yield AgentEvent(
                    "tool_call_start",
                    {
                        "name": function_call.name,
                        "args": dict(function_call.args) if function_call.args else {},
                    },
                )

                tool_content, result_text = call_function(
                    function_call,
                    working_directory=config.working_directory,
                    verbose=config.verbose,
                )

                if function_call.name in MODIFYING_TOOLS:
                    session.modified_project = True

                if function_call.name in EXECUTION_TOOLS:
                    session.last_exit_code = _parse_exit_code(result_text)
                    if session.last_exit_code == 0:
                        session.verified_after_change = True

                yield AgentEvent(
                    "tool_call_result",
                    {
                        "name": function_call.name,
                        "result": result_text,
                        "exit_code": session.last_exit_code,
                    },
                )

                if not tool_content.parts:
                    yield AgentEvent("error", {"message": "Function call result has no parts"})
                    return

                function_responses.append(tool_content.parts[0])

            session.messages.append(
                types.Content(role="user", parts=function_responses)
            )
            continue

        final_text = response.text or ""

        needs_verification = (
            config.require_success
            and session.modified_project
            and not session.verified_after_change
        )

        if needs_verification:
            reason = (
                f"Your last command failed with exit code {session.last_exit_code}. "
                "Analyze the error output, fix the code, and run verification again."
                if session.last_exit_code not in (None, 0)
                else (
                    "You changed the project but have not verified the result. "
                    "Run the relevant tests or scripts and ensure they exit with code 0 "
                    "before giving your final answer."
                )
            )
            session.messages.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=reason)],
                )
            )
            yield AgentEvent(
                "retry_required",
                {"reason": reason, "exit_code": session.last_exit_code},
            )
            continue

        yield AgentEvent("final_response", {"text": final_text})
        return

    yield AgentEvent(
        "max_iterations",
        {"message": f"Maximum iterations ({config.max_iterations}) reached."},
    )
