import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.call_function import call_function

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

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
model_name = "gemini-2.0-flash-001"

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory.",
            )
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads a file at the specified file path, truncated to 10000 characters, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to read, relative to the working directory.",
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file at the specified file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The python file to run, relative to the working directory.",
            )
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="writes to a file at the specified file path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file.",
            ),
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


def generate_response(
    client: genai.Client, messages: list[types.Content], verbose: bool = False
):
    for _ in range(20):
        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        if response.usage_metadata is not None:
            token_count = response.usage_metadata.prompt_token_count
            response_tokens = response.usage_metadata.candidates_token_count
        else:
            token_count = 0
            response_tokens = 0

        if verbose:
            print(f"Prompt tokens: {token_count}")
            print(f"Response tokens: {response_tokens}")

        if not response.function_calls:
            return response.text

        response_parts = []
        for function_call_part in response.function_calls:
            print(
                f"Calling function: {function_call_part.name}({
                    function_call_part.args
                })"
            )
            function_call_result = call_function(function_call_part, verbose=verbose)
            try:
                function_call_response = function_call_result.parts[  # type: ignore
                    0
                ].function_response.response  # type: ignore
                if verbose:
                    print(f"-> {function_call_response}")
            except Exception as e:
                print(f"Error: {e}")
            response_parts.append(function_call_result.parts[0])

        bundled_response = types.Content(parts=response_parts)

        if response.candidates is None:
            continue

        for candidate in response.candidates:
            if candidate.content is None:
                continue

            messages.append(candidate.content)

        messages.append(bundled_response)


if __name__ == "__main__":
    response = generate_response(client, messages, verbose)
    print(response)
