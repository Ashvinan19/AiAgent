import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Make sure it is set in your .env file."
    )

parser = argparse.ArgumentParser(description="Chatbot")

parser.add_argument(
    "user_prompt",
    type=str,
    help="User prompt"
)

parser.add_argument(
    "--verbose",
    action="store_true",
    help="Enable verbose output"
)

args = parser.parse_args()

client = genai.Client(api_key=api_key)

messages: list[types.Content] = [
    types.Content(
        role="user",
        parts=[types.Part(text=args.user_prompt)]
    )
]

for _ in range(20):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        ),
    )

    if response.usage_metadata is None:
        raise RuntimeError("Response usage metadata is missing.")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    function_responses = []

    if response.function_calls:
        for function_call in response.function_calls:
            function_call_result = call_function(
                function_call,
                verbose=args.verbose
            )

            if not function_call_result.parts:
                raise RuntimeError("Function call result has no parts")

            if function_call_result.parts[0].function_response is None:
                raise RuntimeError("Function response is missing")

            if function_call_result.parts[0].function_response.response is None:
                raise RuntimeError("Function response data is missing")

            function_responses.append(function_call_result.parts[0])

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

        messages.append(
            types.Content(
                role="user",
                parts=function_responses
            )
        )

    else:
        print("Final response:")
        print(response.text)
        break

else:
    print("Error: Maximum iterations reached.")
