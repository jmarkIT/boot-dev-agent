import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

verbose = "--verbose" in sys.argv
args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

if not args:
    print("Boot.dev Code Assistant\n")
    print('Usage: python main.py "your prompt here" [--verbose]')
    print('Example: python main.py "How do I build a calculator app?"')
    sys.exit(1)

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

user_prompt: str = " ".join(args)

if verbose:
    print(f"User prompt: {user_prompt}\n")

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]


def generate_response(
    client: genai.Client, messages: list[types.Content], verbose: bool = False
):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )

    if response.usage_metadata is not None:
        token_count = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count

    if verbose:
        print(f"Prompt tokens: {token_count}")
        print(f"Response tokens: {response_tokens}")

    print("Response:")
    print(response.text)


response = generate_response(client, messages, verbose)
