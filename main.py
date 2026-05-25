import os
import argparse
from collections.abc import Iterator

from dotenv import load_dotenv
from google import genai

from agent import AgentConfig, AgentEvent, AgentSession, run_agent
from config import DEFAULT_MAX_ITERATIONS, DEFAULT_WORKING_DIRECTORY

load_dotenv()

CHAT_HELP = """
Chat commands:
  /exit   — leave chat mode
  /clear  — reset conversation history
  /help   — show this help
"""


def print_events(events: Iterator[AgentEvent], verbose: bool) -> bool:
    """Print agent events. Returns False if the turn ended with an error."""
    for event in events:
        if event.kind == "usage" and verbose:
            print(
                f"Tokens — prompt: {event.data['prompt_tokens']}, "
                f"response: {event.data['response_tokens']}"
            )
        elif event.kind == "tool_call_result" and verbose:
            print(f"-> {event.data['result']}")
        elif event.kind == "retry_required" and verbose:
            print(f"Retrying: {event.data['reason']}")
        elif event.kind == "final_response":
            print(event.data["text"])
            print()
        elif event.kind == "max_iterations":
            print(f"Error: {event.data['message']}")
            return False
        elif event.kind == "error":
            print(f"Error: {event.data['message']}")
            return False
    return True


def run_single_turn(
    client: genai.Client,
    user_prompt: str,
    config: AgentConfig,
    verbose: bool,
) -> None:
    if verbose:
        print(f"Prompt: {user_prompt}\n")

    print_events(run_agent(client, user_prompt, config), verbose)


def chat_loop(
    client: genai.Client,
    config: AgentConfig,
    verbose: bool,
) -> None:
    session = AgentSession()
    print("Chat mode — conversation history is preserved between turns.")
    print(CHAT_HELP)

    while True:
        try:
            user_input = input("\n>>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input == "/exit":
            print("Bye.")
            break
        if user_input == "/clear":
            session = AgentSession()
            print("(conversation cleared)")
            continue
        if user_input == "/help":
            print(CHAT_HELP)
            continue

        print_events(
            run_agent(client, user_input, config, session=session),
            verbose,
        )


def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Make sure it is set in your .env file."
        )

    parser = argparse.ArgumentParser(
        description="AI coding agent with repository awareness, editing, and execution"
    )
    parser.add_argument(
        "user_prompt",
        nargs="?",
        default=None,
        help="Task for the agent (omit when using --chat)",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Interactive multi-turn chat; history persists until /clear or exit",
    )
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
        help=f"Maximum agent loop iterations per turn (default: {DEFAULT_MAX_ITERATIONS})",
    )
    parser.add_argument(
        "--require-success",
        action="store_true",
        help="Keep iterating until the last command exits with code 0",
    )

    args = parser.parse_args()

    if args.chat and args.user_prompt:
        parser.error("Do not pass a prompt with --chat; type messages at the >>> prompt instead.")
    if not args.chat and not args.user_prompt:
        parser.error("Provide a prompt, or use --chat for interactive mode.")

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
        print(f"Max iterations per turn: {config.max_iterations}")
        print(f"Require success: {config.require_success}\n")

    if args.chat:
        chat_loop(client, config, args.verbose)
    else:
        run_single_turn(client, args.user_prompt, config, args.verbose)


if __name__ == "__main__":
    main()
