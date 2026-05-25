import os
import argparse
from dotenv import load_dotenv
from google import genai

from agent import AgentConfig, run_agent
from config import DEFAULT_MAX_ITERATIONS, DEFAULT_WORKING_DIRECTORY

load_dotenv()


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Make sure it is set in your .env file."
        )

    parser = argparse.ArgumentParser(
        description="AI coding agent with repository awareness, editing, and execution"
    )
    parser.add_argument("user_prompt", type=str, help="Task for the agent")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show token usage and full tool output",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        default=DEFAULT_WORKING_DIRECTORY,
        help=f"Sandboxed project directory (default: {DEFAULT_WORKING_DIRECTORY})",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Maximum agent loop iterations (default: {DEFAULT_MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--require-success",
        action="store_true",
        help="Keep iterating until the last command exits with code 0",
    )

    args = parser.parse_args()

    working_dir = os.path.abspath(args.working_dir)
    if not os.path.isdir(working_dir):
        raise RuntimeError(f"Working directory does not exist: {working_dir}")

    client = genai.Client(api_key=api_key)
    config = AgentConfig(
        working_directory=working_dir,
        max_iterations=args.max_iterations,
        verbose=args.verbose,
        require_success=args.require_success,
    )

    if args.verbose:
        print(f"Working directory: {working_dir}")
        print(f"Max iterations: {config.max_iterations}")
        print(f"Require success: {config.require_success}")
        print(f"Prompt: {args.user_prompt}\n")

    for event in run_agent(client, args.user_prompt, config):
        if event.kind == "usage" and args.verbose:
            print(
                f"Tokens — prompt: {event.data['prompt_tokens']}, "
                f"response: {event.data['response_tokens']}"
            )
        elif event.kind == "tool_call_result" and args.verbose:
            print(f"-> {event.data['result']}")
        elif event.kind == "retry_required" and args.verbose:
            print(f"Retrying: {event.data['reason']}")
        elif event.kind == "final_response":
            print("Final response:")
            print(event.data["text"])
        elif event.kind == "max_iterations":
            print(f"Error: {event.data['message']}")
        elif event.kind == "error":
            print(f"Error: {event.data['message']}")


if __name__ == "__main__":
    main()
